"""
Process Audit Contracts - Wave 18 AP3

Neutrale Audit-Typen fuer den Process Kernel. Die Contracts verankern
Entscheidungsgruende, Evidenzpfade, Policy-Snapshots und den Bezug auf
kanonische Prozessdefinitionen sowie versionierte Workflows.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.canonical_process_definitions import get_canonical_process_definition
from app.core.workflow_versioning import (
    WorkflowDefinitionRef,
    get_active_workflow_version,
)
from app.core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionResult,
)


ProcessActorType = Literal["human", "ai_agent", "system"]


class PolicySnapshot(BaseModel):
    """Serialisierte Sicht auf die wirksame Policy-Lage zum Entscheidungszeitpunkt."""

    rule_id: str = Field(min_length=1)
    effective_scope: str = Field(min_length=1)
    effective_enabled: bool = True
    effective_params: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None
    schema_version: int = 1


class ProcessDecisionReason(BaseModel):
    """Begruendung fuer einen Prozessschritt oder eine Freigabeentscheidung."""

    code: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    detail: str | None = None
    schema_version: int = 1


class ProcessAuditEvidenceRef(BaseModel):
    """Leichte, kernneutrale Evidenzreferenz fuer Audit-Contracts."""

    evidence_id: str = Field(min_length=1)
    evidence_type: str = Field(min_length=1)
    source_system: str = Field(min_length=1)
    external_ref: str = Field(min_length=1)
    verified: bool = False
    schema_version: int = 1


class ProcessAuditEntry(BaseModel):
    """Einheitlicher Audit-Datensatz fuer den Process Kernel."""

    audit_entry_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    process_definition_key: str = Field(min_length=3)
    workflow_ref: WorkflowDefinitionRef
    aggregate_type: str = Field(min_length=1)
    aggregate_id: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    actor_type: ProcessActorType
    actor_id: str = Field(min_length=1)
    decision_reason: ProcessDecisionReason
    policy_snapshot: PolicySnapshot | None = None
    evidence_refs: list[ProcessAuditEvidenceRef] = Field(default_factory=list)
    reference_context: dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1

    def has_verified_evidence(self) -> bool:
        return any(ref.verified for ref in self.evidence_refs)


def build_process_audit_entry(
    *,
    audit_entry_id: str,
    tenant_id: str,
    process_definition_key: str,
    aggregate_type: str,
    aggregate_id: str,
    action_name: str,
    actor_type: ProcessActorType,
    actor_id: str,
    decision_reason: ProcessDecisionReason,
    policy_snapshot: PolicySnapshot | None = None,
    evidence_refs: list[ProcessAuditEvidenceRef] | None = None,
    reference_context: dict[str, Any] | None = None,
) -> ProcessAuditEntry:
    """Baut einen Audit-Eintrag auf Basis der aktiven Workflow-Version eines Prozesses."""

    canonical_process = get_canonical_process_definition(process_definition_key)
    if aggregate_type not in canonical_process.aggregate_sequence:
        raise ValueError(
            f"Aggregat '{aggregate_type}' ist nicht Teil der Prozessdefinition "
            f"'{process_definition_key}'"
        )

    active_version = get_active_workflow_version(process_definition_key)
    if active_version is None:
        raise ValueError(
            f"Keine aktive Workflow-Version fuer Prozessdefinition '{process_definition_key}' gefunden"
        )

    return ProcessAuditEntry(
        audit_entry_id=audit_entry_id,
        tenant_id=tenant_id,
        process_definition_key=process_definition_key,
        workflow_ref=active_version.definition_ref,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        action_name=action_name,
        actor_type=actor_type,
        actor_id=actor_id,
        decision_reason=decision_reason,
        policy_snapshot=policy_snapshot,
        evidence_refs=list(evidence_refs or []),
        reference_context=dict(reference_context or {}),
    )


def validate_process_audit_entry(entry: ProcessAuditEntry) -> list[str]:
    """Validiert den Bezug eines Audit-Eintrags auf Prozessdefinition und Workflow-Version."""

    errors: list[str] = []

    try:
        canonical_process = get_canonical_process_definition(entry.process_definition_key)
    except KeyError as exc:
        return [str(exc)]

    if entry.aggregate_type not in canonical_process.aggregate_sequence:
        errors.append(
            f"{entry.process_definition_key}: aggregate_type '{entry.aggregate_type}' gehoert nicht zur Prozesskette"
        )

    if entry.workflow_ref.process_definition_key != entry.process_definition_key:
        errors.append(
            f"{entry.process_definition_key}: workflow_ref.process_definition_key passt nicht"
        )

    if entry.workflow_ref.workflow_key not in canonical_process.workflow_process_keys:
        errors.append(
            f"{entry.process_definition_key}: workflow_key '{entry.workflow_ref.workflow_key}' ist nicht erlaubt"
        )

    active_version = get_active_workflow_version(entry.process_definition_key)
    if active_version is None:
        errors.append(
            f"{entry.process_definition_key}: keine aktive Workflow-Version zur Validierung verfuegbar"
        )
    else:
        if (
            entry.workflow_ref.version_number
            != active_version.definition_ref.version_number
        ):
            errors.append(
                f"{entry.process_definition_key}: workflow version {entry.workflow_ref.version_number} ist nicht die aktive Version"
            )

    return errors


def build_action_execution_audit_entry(
    request: ActionExecutionRequest,
    result: ActionExecutionResult,
    *,
    evidence_refs: list[ProcessAuditEvidenceRef] | None = None,
    policy_snapshot: PolicySnapshot | None = None,
) -> ProcessAuditEntry:
    """
    Baut einen ProcessAuditEntry direkt aus Execute-Request und Execute-Result.

    Der Builder setzt voraus, dass der Action-Layer bereits mit
    `process_definition_key` und Workflow-Metadaten angereichert wurde.
    """

    process_definition_key = (
        result.process_definition_key or request.process_definition_key
    )
    if process_definition_key is None:
        raise ValueError(
            "ActionExecutionResult enthaelt keinen process_definition_key; "
            "Audit-Bruecke setzt Wave-18-Prozessmetadaten voraus"
        )

    decision_reason = ProcessDecisionReason(
        code=(result.error.code if result.error else result.status.value.upper()),
        summary=(
            result.error.message
            if result.error is not None
            else f"Action '{result.command_name}' wurde mit Status '{result.status.value}' verarbeitet"
        ),
        detail=(result.error.detail if result.error is not None else None),
    )

    reference_context: dict[str, Any] = {}
    normalized_reference = request.normalized_reference_context()
    if normalized_reference is not None:
        reference_context = normalized_reference.model_dump(mode="json")

    return build_process_audit_entry(
        audit_entry_id=result.execution_id,
        tenant_id=request.tenant_id,
        process_definition_key=process_definition_key,
        aggregate_type=result.aggregate_type,
        aggregate_id=result.aggregate_id,
        action_name=result.command_name,
        actor_type=request.issuer_type,
        actor_id=request.issuer_role or request.issuer_type,
        decision_reason=decision_reason,
        policy_snapshot=policy_snapshot,
        evidence_refs=evidence_refs,
        reference_context=reference_context,
    )
