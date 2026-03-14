"""
Wave 17: Action Execution Layer fuer den Process Kernel.

Orchestriert Command-Katalog, Aggregate-Ownership, Agent-Guards und Idempotenz
unter einem stabilen Execute-Contract.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.aggregate_registry import (
    AggregateDefinition,
    get_aggregate_definition,
    validate_command_aggregate_consistency,
)
from app.core.agent_command_manifest import build_agent_command_manifest
from app.core.business_commands import BusinessCommand, CommandError, CommandStatus
from app.core.canonical_process_definitions import get_canonical_process_definition
from app.core.command_dispatcher import CommandDispatcher
from app.core.process_references import ProcessReferenceContext
from app.core.workflow_versioning import get_active_workflow_version


class ActionExecutionStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING_APPROVAL = "pending_approval"
    DUPLICATE = "duplicate"


class ActionResultSource(str, Enum):
    FRESH = "fresh"
    IDEMPOTENT_REPLAY = "idempotent_replay"


class ActionExecutionRequest(BaseModel):
    command_name: str = Field(min_length=1)
    aggregate_type: str = Field(min_length=1)
    aggregate_id: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = Field(min_length=1)
    issuer_role: str | None = None
    issuer_type: Literal["human", "ai_agent", "system"]
    idempotency_key: str = Field(min_length=1)
    human_confirmation: bool = False
    reference_context: dict[str, Any] | None = None
    process_definition_key: str | None = None
    workflow_key: str | None = None
    workflow_version_number: int | None = None

    def to_business_command(
        self,
        *,
        process_definition_key: str | None = None,
        workflow_key: str | None = None,
        workflow_version_number: int | None = None,
    ) -> BusinessCommand:
        return BusinessCommand(
            command_id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            command_name=self.command_name,
            process_definition_key=process_definition_key or self.process_definition_key,
            workflow_key=workflow_key or self.workflow_key,
            workflow_version_number=(
                workflow_version_number or self.workflow_version_number
            ),
            issued_by=self._build_issued_by(),
            idempotency_key=self.idempotency_key,
            payload=self.payload,
            requires_human_confirmation=self.human_confirmation,
        )

    def normalized_reference_context(self) -> ProcessReferenceContext | None:
        if self.reference_context is None:
            return None
        return ProcessReferenceContext(**self.reference_context)

    def request_fingerprint(self) -> str:
        reference = None
        if self.reference_context is not None:
            reference = self.normalized_reference_context().model_dump(mode="json")
        serialized = json.dumps(
            {
                "command_name": self.command_name,
                "aggregate_type": self.aggregate_type,
                "aggregate_id": self.aggregate_id,
                "payload": self.payload,
                "tenant_id": self.tenant_id,
                "issuer_role": self.issuer_role,
                "issuer_type": self.issuer_type,
                "human_confirmation": self.human_confirmation,
                "reference_context": reference,
                "process_definition_key": self.process_definition_key,
                "workflow_key": self.workflow_key,
                "workflow_version_number": self.workflow_version_number,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _build_issued_by(self) -> str:
        role = self.issuer_role or "unknown"
        return f"{self.issuer_type}:{role}"


class ActionExecutionResult(BaseModel):
    execution_id: str
    command_id: str
    status: ActionExecutionStatus
    aggregate_type: str
    aggregate_id: str
    aggregate_owner: str
    command_name: str
    idempotency_key: str
    process_definition_key: str | None = None
    workflow_key: str | None = None
    workflow_version_number: int | None = None
    requires_human_confirmation: bool = False
    result_source: ActionResultSource = ActionResultSource.FRESH
    error: CommandError | None = None
    schema_version: int = 1

    @classmethod
    def from_dispatch(
        cls,
        *,
        command: BusinessCommand,
        aggregate_definition: AggregateDefinition,
        dispatch_status: CommandStatus,
        error: CommandError | None = None,
    ) -> "ActionExecutionResult":
        status_map = {
            CommandStatus.ACCEPTED: ActionExecutionStatus.ACCEPTED,
            CommandStatus.REJECTED: ActionExecutionStatus.REJECTED,
            CommandStatus.PENDING_APPROVAL: ActionExecutionStatus.PENDING_APPROVAL,
        }
        status = status_map.get(dispatch_status, ActionExecutionStatus.REJECTED)
        return cls(
            execution_id=str(uuid.uuid4()),
            command_id=command.command_id,
            status=status,
            aggregate_type=command.aggregate_type,
            aggregate_id=command.aggregate_id,
            aggregate_owner=aggregate_definition.business_domain,
            command_name=command.command_name,
            idempotency_key=command.idempotency_key,
            process_definition_key=command.process_definition_key,
            workflow_key=command.workflow_key,
            workflow_version_number=command.workflow_version_number,
            requires_human_confirmation=aggregate_requires_human_confirmation(
                command.command_name
            ),
            error=error,
        )

    def as_idempotent_replay(self) -> "ActionExecutionResult":
        return self.model_copy(
            update={
                "status": ActionExecutionStatus.DUPLICATE,
                "result_source": ActionResultSource.IDEMPOTENT_REPLAY,
            }
        )


def aggregate_requires_human_confirmation(command_name: str) -> bool:
    manifest = build_agent_command_manifest()
    entry = next((item for item in manifest.commands if item.command_name == command_name), None)
    return bool(entry and entry.requires_human_confirmation)


def build_action_conflict_error() -> CommandError:
    return CommandError(
        code="IDEMPOTENCY_KEY_REUSED",
        message="Idempotency-Key wurde bereits fuer einen anderen Request verwendet",
    )


def build_action_process_contract_error(message: str) -> CommandError:
    return CommandError(
        code="PROCESS_CONTRACT_INVALID",
        message=message,
    )


class ActionExecutionService:
    """Einziger Orchestrator fuer Execute-Requests im Process Kernel."""

    def __init__(self, dispatcher: CommandDispatcher | None = None) -> None:
        self._dispatcher = dispatcher or CommandDispatcher()

    def execute(
        self, request: ActionExecutionRequest, aggregate_state: dict[str, Any] | None = None
    ) -> ActionExecutionResult:
        aggregate_definition = get_aggregate_definition(request.aggregate_type)
        command_definition = self._dispatcher.get_definition(request.command_name)
        process_contract_error, process_metadata = self._resolve_process_contract(request)
        command = request.to_business_command(**process_metadata)
        if process_contract_error is not None:
            return ActionExecutionResult.from_dispatch(
                command=command,
                aggregate_definition=aggregate_definition,
                dispatch_status=CommandStatus.REJECTED,
                error=process_contract_error,
            )
        if not validate_command_aggregate_consistency(
            request.command_name, request.aggregate_type
        ):
            return ActionExecutionResult(
                execution_id=str(uuid.uuid4()),
                command_id=command.command_id,
                status=ActionExecutionStatus.REJECTED,
                aggregate_type=request.aggregate_type,
                aggregate_id=request.aggregate_id,
                aggregate_owner=aggregate_definition.business_domain,
                command_name=request.command_name,
                idempotency_key=request.idempotency_key,
                process_definition_key=command.process_definition_key,
                workflow_key=command.workflow_key,
                workflow_version_number=command.workflow_version_number,
                requires_human_confirmation=aggregate_requires_human_confirmation(
                    request.command_name
                ),
                error=CommandError(
                    code="AGGREGATE_COMMAND_MISMATCH",
                    message=(
                        f"Command '{request.command_name}' passt nicht zu "
                        f"Aggregat '{request.aggregate_type}'"
                    ),
                ),
            )

        agent_error = self._validate_agent_constraints(request)
        if agent_error is not None:
            return ActionExecutionResult.from_dispatch(
                command=command,
                aggregate_definition=aggregate_definition,
                dispatch_status=CommandStatus.REJECTED,
                error=agent_error,
            )

        dispatch = self._dispatcher.dispatch(
            command,
            aggregate_state=aggregate_state or request.payload,
            issuer_role=self._resolve_dispatch_role(request, command_definition),
        )
        return ActionExecutionResult.from_dispatch(
            command=command,
            aggregate_definition=aggregate_definition,
            dispatch_status=dispatch.status,
            error=dispatch.error,
        )

    def _resolve_process_contract(
        self,
        request: ActionExecutionRequest,
    ) -> tuple[CommandError | None, dict[str, Any]]:
        metadata = {
            "process_definition_key": request.process_definition_key,
            "workflow_key": request.workflow_key,
            "workflow_version_number": request.workflow_version_number,
        }
        if request.process_definition_key is None:
            if request.workflow_key is not None or request.workflow_version_number is not None:
                return (
                    build_action_process_contract_error(
                        "workflow_key und workflow_version_number duerfen nicht ohne process_definition_key gesetzt werden"
                    ),
                    metadata,
                )
            return None, metadata

        try:
            process_definition = get_canonical_process_definition(
                request.process_definition_key
            )
        except KeyError as exc:
            return build_action_process_contract_error(str(exc)), metadata

        if request.aggregate_type not in process_definition.aggregate_sequence:
            return (
                build_action_process_contract_error(
                    f"Aggregat '{request.aggregate_type}' ist nicht Teil der Prozessdefinition "
                    f"'{request.process_definition_key}'"
                ),
                metadata,
            )

        if request.command_name not in process_definition.action_command_names:
            return (
                build_action_process_contract_error(
                    f"Command '{request.command_name}' ist nicht Teil der Action-Contracts "
                    f"fuer Prozessdefinition '{request.process_definition_key}'"
                ),
                metadata,
            )

        active_version = get_active_workflow_version(request.process_definition_key)
        if active_version is None:
            return (
                build_action_process_contract_error(
                    f"Keine aktive Workflow-Version fuer Prozessdefinition '{request.process_definition_key}' gefunden"
                ),
                metadata,
            )

        if (
            request.workflow_key is not None
            and request.workflow_key != active_version.definition_ref.workflow_key
        ):
            return (
                build_action_process_contract_error(
                    f"workflow_key '{request.workflow_key}' passt nicht zur aktiven Workflow-Version"
                ),
                metadata,
            )

        if (
            request.workflow_version_number is not None
            and request.workflow_version_number
            != active_version.definition_ref.version_number
        ):
            return (
                build_action_process_contract_error(
                    f"workflow_version_number {request.workflow_version_number} ist nicht aktiv"
                ),
                metadata,
            )

        metadata["workflow_key"] = (
            request.workflow_key or active_version.definition_ref.workflow_key
        )
        metadata["workflow_version_number"] = (
            request.workflow_version_number
            or active_version.definition_ref.version_number
        )
        return None, metadata

    def _validate_agent_constraints(
        self, request: ActionExecutionRequest
    ) -> CommandError | None:
        if request.issuer_type != "ai_agent":
            return None
        manifest = build_agent_command_manifest()
        if request.command_name in manifest.fully_blocked_for_agents:
            return CommandError(
                code="AGENT_COMMAND_BLOCKED",
                message=f"Command '{request.command_name}' ist fuer Agenten gesperrt",
            )
        entry = next(
            (item for item in manifest.commands if item.command_name == request.command_name),
            None,
        )
        if entry is None:
            return CommandError(
                code="UNKNOWN_COMMAND",
                message=f"Unbekannter Command: {request.command_name}",
            )
        agent_role = request.issuer_role or ""
        if agent_role not in entry.allowed_agent_types:
            return CommandError(
                code="AGENT_TYPE_NOT_ALLOWED",
                message=(
                    f"Agent-Typ '{agent_role}' darf '{request.command_name}' "
                    "nicht ausfuehren"
                ),
            )
        return None

    def _resolve_dispatch_role(
        self,
        request: ActionExecutionRequest,
        command_definition: Any,
    ) -> str | None:
        if request.issuer_type != "ai_agent":
            return request.issuer_role
        if command_definition is None or not command_definition.allowed_roles:
            return request.issuer_role
        return command_definition.allowed_roles[0]
