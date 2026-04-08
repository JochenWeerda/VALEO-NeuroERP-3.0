"""Application service for productive NeuroASSIST business workflows and assistants."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ValidationError

from .neuroassist import (
    NeuroAssistCapability,
    get_neuroassist_capabilities,
    get_productive_neuroassist_capabilities,
    resolve_neuroassist_capability,
)
from .agent_ops import AgentBudgetGuardrailExceededError, get_agent_ops_service
from .neuroassist_audit import (
    build_neuroassist_audit_record,
    build_neuroassist_process_audit_entry,
)
from .neuroassist_context import resolve_neuroassist_context
from .neuroassist_inputs import (
    BestellvorschlagRunInput,
    ComplianceCopilotRunInput,
    DataQualityAssistantRunInput,
    FinanceSkontoRunInput,
    OperationsExceptionRunInput,
    validate_capability_input,
)
from .neuroassist_runtime import NeuroAssistRun, build_case_run_projection, build_neuroassist_run
from .neuroassist_workflow_runners import resolve_workflow_runner_for_capability
from .workflows.compliance_copilot import check_compliance
from .workflows.data_quality_assistant import run_data_quality_assistant
from .workflows.operations_exception_assistant import run_operations_exception_assistant
from .workflows.skonto_optimizer import optimize_skonto


class NeuroAssistInputContractError(ValueError):
    """Raised when a generic NeuroASSIST run request violates its input contract."""


class NeuroAssistRunNotFoundError(KeyError):
    """Raised when a generic NeuroASSIST run_id cannot be resolved."""


class NeuroAssistGateActionError(ValueError):
    """Raised when a generic gate action cannot be applied to a run."""


@dataclass(frozen=True)
class _CapabilityRunnerDefinition:
    input_model: type[BaseModel]
    execute_method: str
    status_method: str
    output_schema: str
    workflow_runner_capability_key: str | None = None
    result_fields: tuple[str, ...] = ()
    audit_context_fields: tuple[str, ...] = ()
    audit_context_constants: dict[str, Any] | None = None
    audit_context_nested_fields: dict[str, tuple[str, ...]] | None = None
    runtime_context_fields: tuple[str, ...] = ()
    runtime_context_constants: dict[str, Any] | None = None
    dynamic_result_refs_fields: tuple[str, ...] = ()
    static_result_refs: tuple[str, ...] = ()
    pending_approval_gate_types: tuple[str, ...] = ()
    gate_action_method: str | None = None


class NeuroAssistService:
    """Facade for productive NeuroASSIST capabilities inside the application core."""

    _run_registry: dict[str, dict[str, Any]] = {}
    _runner_registry: dict[str, _CapabilityRunnerDefinition] = {
        "bestellvorschlag_assistant": _CapabilityRunnerDefinition(
            input_model=BestellvorschlagRunInput,
            execute_method="_run_bestellvorschlag_capability",
            status_method="_get_bestellvorschlag_run_status",
            output_schema="BestellvorschlagState",
            workflow_runner_capability_key="bestellvorschlag_assistant",
            result_fields=(
                "current_stage_key",
                "gate_decisions",
                "proposal",
                "approval_requirement",
                "approval_record",
                "command_result",
                "order_id",
                "workflow_id",
            ),
            audit_context_fields=("gate_decisions",),
            audit_context_nested_fields={"approval_requirement": ("requires_human_approval",)},
            runtime_context_fields=("gate_decisions", "approval_requirement"),
            pending_approval_gate_types=("approval_gate",),
            gate_action_method="_apply_bestellvorschlag_gate_action",
        ),
        "finance_skonto_assistant": _CapabilityRunnerDefinition(
            input_model=FinanceSkontoRunInput,
            execute_method="_run_finance_skonto_capability",
            status_method="_get_registered_runtime_status",
            output_schema="SkontoOptimizerState",
            workflow_runner_capability_key=None,
            result_fields=(
                "current_stage_key",
                "gate_decisions",
                "recommendations",
            ),
            audit_context_fields=("gate_decisions",),
            audit_context_constants={"policy_blocked": False},
            runtime_context_fields=("gate_decisions",),
            runtime_context_constants={"policy_blocked": False},
            pending_approval_gate_types=(),
            gate_action_method=None,
        ),
        "compliance_copilot": _CapabilityRunnerDefinition(
            input_model=ComplianceCopilotRunInput,
            execute_method="_run_compliance_capability",
            status_method="_get_registered_runtime_status",
            output_schema="ComplianceCopilotState",
            workflow_runner_capability_key=None,
            result_fields=(
                "current_stage_key",
                "gate_decisions",
                "entity_id",
                "entity_type",
                "violations",
                "risk_score",
                "recommendations",
                "checked_at",
            ),
            audit_context_fields=("gate_decisions",),
            runtime_context_fields=("gate_decisions",),
            runtime_context_constants={"policy_blocked": True},
            pending_approval_gate_types=(),
            gate_action_method=None,
        ),
        "data_quality_assistant": _CapabilityRunnerDefinition(
            input_model=DataQualityAssistantRunInput,
            execute_method="_run_data_quality_capability",
            status_method="_get_registered_runtime_status",
            output_schema="DataQualityAssistantState",
            workflow_runner_capability_key=None,
            result_fields=(
                "current_stage_key",
                "gate_decisions",
                "dq_findings",
                "payload_snapshot",
                "ingestion_context",
                "root_cause_summary",
                "remediation_plan",
            ),
            audit_context_fields=("dq_findings", "gate_decisions"),
            runtime_context_fields=("dq_findings", "gate_decisions"),
            pending_approval_gate_types=("approval_gate",),
            gate_action_method=None,
        ),
        "operations_exception_assistant": _CapabilityRunnerDefinition(
            input_model=OperationsExceptionRunInput,
            execute_method="_run_operations_exception_capability",
            status_method="_get_registered_runtime_status",
            output_schema="OperationsExceptionState",
            workflow_runner_capability_key=None,
            result_fields=(
                "current_stage_key",
                "gate_decisions",
                "exception_code",
                "exception_summary",
                "proposed_actions",
                "escalation_target",
                "process_definition_key",
                "aggregate_type",
                "aggregate_id",
            ),
            audit_context_fields=("gate_decisions", "process_definition_key", "aggregate_type", "aggregate_id"),
            runtime_context_fields=("gate_decisions", "process_definition_key"),
            pending_approval_gate_types=("approval_gate",),
            gate_action_method=None,
        ),
    }

    @staticmethod
    def _resolve_runtime(
        capability_key: str,
        *,
        status: str,
        current_stage_key: str,
        context: dict[str, Any] | None = None,
    ) -> NeuroAssistRun:
        capability = resolve_neuroassist_capability(capability_key)
        return build_neuroassist_run(
            capability,
            status=status,
            current_stage_key=current_stage_key,
            context=context,
        )

    @staticmethod
    def _build_audit_payload(
        capability_key: str,
        *,
        run_id: str,
        tenant_id: str,
        status: str,
        current_stage_key: str,
        output_schema: str,
        context: dict[str, Any] | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        result_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        capability = resolve_neuroassist_capability(capability_key)
        context_resolution = resolve_neuroassist_context(
            capability,
            tenant_id=tenant_id,
            reference_context=context,
        )
        case_run = build_case_run_projection(
            capability,
            run_id=run_id,
            tenant_id=tenant_id,
            status=status,
            current_stage_key=current_stage_key,
            context=context,
            started_at=started_at,
            completed_at=completed_at,
            result_refs=result_refs,
        )
        audit_record = build_neuroassist_audit_record(
            capability=capability,
            case_run=case_run,
            output_schema=output_schema,
            reference_context=context,
        )
        process_audit_entry = build_neuroassist_process_audit_entry(
            capability=capability,
            case_run=case_run,
            audit_record=audit_record,
            context_resolution=context_resolution,
        )
        payload = {
            "audit_record": audit_record.model_dump(mode="json"),
            "context_resolution": context_resolution.model_dump(mode="json"),
        }
        if process_audit_entry is not None:
            payload["process_audit_entry"] = process_audit_entry.model_dump(mode="json")
        return payload

    @classmethod
    def _build_runner_audit_payload(
        cls,
        capability_key: str,
        *,
        run_id: str,
        tenant_id: str,
        status: str,
        result: dict[str, Any],
        started_at: str | None = None,
        completed_at: str | None = None,
        result_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        runner_definition = cls._resolve_runner_definition(capability_key)
        context = cls._build_runner_audit_context(runner_definition, result)
        return cls._build_audit_payload(
            capability_key,
            run_id=run_id,
            tenant_id=tenant_id,
            status=status,
            current_stage_key=result["current_stage_key"],
            output_schema=runner_definition.output_schema,
            context=context,
            started_at=started_at,
            completed_at=completed_at,
            result_refs=result_refs,
        )

    @staticmethod
    def _build_runner_audit_context(
        runner_definition: _CapabilityRunnerDefinition,
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        context: dict[str, Any] = {}
        for field_name in runner_definition.audit_context_fields:
            value = result.get(field_name)
            if field_name == "gate_decisions" and value is None:
                value = []
            elif field_name == "dq_findings" and value is None:
                value = []
            context[field_name] = value
        for source_field, nested_fields in (runner_definition.audit_context_nested_fields or {}).items():
            nested_source = dict(result.get(source_field) or {})
            for field_name in nested_fields:
                context[field_name] = nested_source.get(field_name)
        if runner_definition.audit_context_constants:
            context.update(runner_definition.audit_context_constants)
        return context or None

    @staticmethod
    def _normalize_gate_decision(decision: dict[str, Any]) -> dict[str, Any]:
        gate_type = decision.get("gate_type")
        status = decision.get("status")
        if gate_type == "approval_gate":
            default_reason = (
                "Human approval is still pending before execution."
                if status == "deferred"
                else "Human approval decision has been recorded."
            )
            default_required_role = "human_operator"
        elif gate_type == "policy_gate":
            default_reason = "Policy checks were evaluated for the current orchestration path."
            default_required_role = None
        elif gate_type == "dq_gate":
            default_reason = "Data-quality findings require explicit remediation handling."
            default_required_role = None
        elif gate_type == "process_gate":
            default_reason = "Process guardrails were evaluated for the current orchestration path."
            default_required_role = None
        else:
            default_reason = "Gate decision was evaluated for the current orchestration path."
            default_required_role = None
        return {
            "gate_type": gate_type,
            "status": status,
            "reason": decision.get("reason") or default_reason,
            "required_role": decision.get("required_role", default_required_role),
            "evidence_refs": decision.get("evidence_refs") or [],
            "schema_version": decision.get("schema_version", 1),
        }

    @classmethod
    def _normalize_projection_result(cls, result: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(result)
        if "gate_decisions" in normalized and normalized.get("gate_decisions") is not None:
            normalized["gate_decisions"] = [
                cls._normalize_gate_decision(decision)
                for decision in normalized.get("gate_decisions") or []
            ]
        return normalized

    @staticmethod
    def _build_runner_runtime_context(
        runner_definition: _CapabilityRunnerDefinition,
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        context: dict[str, Any] = {}
        for field_name in runner_definition.runtime_context_fields:
            value = result.get(field_name)
            if field_name in {"gate_decisions", "dq_findings"} and value is None:
                value = []
            context[field_name] = value
        if runner_definition.runtime_context_constants:
            for key, value in runner_definition.runtime_context_constants.items():
                if key == "policy_blocked" and value is True:
                    context[key] = bool(result.get("violations"))
                else:
                    context[key] = value
        return context or None

    @staticmethod
    def _derive_runner_status(
        runner_definition: _CapabilityRunnerDefinition,
        result: dict[str, Any],
    ) -> str:
        if not runner_definition.pending_approval_gate_types:
            return "completed"
        for decision in result.get("gate_decisions") or []:
            if (
                decision.get("gate_type") in runner_definition.pending_approval_gate_types
                and decision.get("status") == "deferred"
            ):
                return "pending_approval"
        return "completed"

    @staticmethod
    def _build_runner_result_refs(
        runner_definition: _CapabilityRunnerDefinition,
        result: dict[str, Any],
    ) -> list[str]:
        refs = list(runner_definition.static_result_refs)
        for field_name in runner_definition.dynamic_result_refs_fields:
            value = result.get(field_name)
            if isinstance(value, str) and value:
                refs.append(value)
        return refs

    @classmethod
    def _project_runner_runtime(
        cls,
        capability_key: str,
        *,
        status: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        result = cls._normalize_projection_result(result)
        runner_definition = cls._resolve_runner_definition(capability_key)
        return cls._resolve_runtime(
            capability_key,
            status=status,
            current_stage_key=result.get("current_stage_key") or "closure",
            context=cls._build_runner_runtime_context(runner_definition, result),
        ).model_dump(mode="json")

    @classmethod
    def _project_runner_result_payload(
        cls,
        capability_key: str,
        *,
        run_id: str,
        tenant_id: str,
        status: str,
        started_at: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        result = cls._normalize_projection_result(result)
        runner_definition = cls._resolve_runner_definition(capability_key)
        payload = {
            key: result.get(key)
            for key in runner_definition.result_fields
        }
        payload.update(
            cls._build_runner_audit_payload(
                capability_key,
                run_id=run_id,
                tenant_id=tenant_id,
                status=status,
                result=result,
                started_at=started_at,
                result_refs=cls._build_runner_result_refs(runner_definition, result),
            )
        )
        return payload

    @classmethod
    def _finalize_registered_sync_run(
        cls,
        capability_key: str,
        *,
        tenant_id: str,
        run_id: str,
        started_at: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        runner_definition = cls._resolve_runner_definition(capability_key)
        status = cls._derive_runner_status(runner_definition, result)
        runtime = cls._project_runner_runtime(
            capability_key,
            status=status,
            result=result,
        )
        payload = cls._project_runner_result_payload(
            capability_key,
            run_id=run_id,
            tenant_id=tenant_id,
            status=status,
            started_at=started_at,
            result=result,
        )
        cls._register_run(
            run_id,
            capability_key=capability_key,
            tenant_id=tenant_id,
            started_at=started_at,
            status=status,
            result=payload,
        )
        cls._record_agent_ops(
            run_id=run_id,
            tenant_id=tenant_id,
            capability_key=capability_key,
            status=status,
            runtime=runtime,
            result=payload,
        )
        return {
            "run_id": run_id,
            "correlation_id": run_id,
            "capability_key": capability_key,
            "status": status,
            "started_at": started_at,
            "runtime": runtime,
            "result": payload,
        }

    def list_capabilities(self, *, productive_only: bool = False) -> tuple[NeuroAssistCapability, ...]:
        if productive_only:
            return get_productive_neuroassist_capabilities()
        return get_neuroassist_capabilities()

    @classmethod
    def _resolve_workflow_runner(cls, capability_key: str):
        runner_definition = cls._resolve_runner_definition(capability_key)
        if runner_definition.workflow_runner_capability_key is None:
            raise NeuroAssistInputContractError(
                f"Capability '{capability_key}' does not expose a workflow runner adapter"
            )
        return resolve_workflow_runner_for_capability(runner_definition.workflow_runner_capability_key)

    @classmethod
    def _resolve_runner_definition(cls, capability_key: str) -> _CapabilityRunnerDefinition:
        definition = cls._runner_registry.get(capability_key)
        if definition is None:
            raise NeuroAssistInputContractError(
                f"No generic NeuroASSIST runner registered for capability '{capability_key}'"
            )
        return definition

    @classmethod
    def _register_run(
        cls,
        run_id: str,
        *,
        capability_key: str,
        tenant_id: str,
        started_at: str,
        status: str,
        result: dict[str, Any],
    ) -> None:
        cls._run_registry[run_id] = {
            "capability_key": capability_key,
            "tenant_id": tenant_id,
            "started_at": started_at,
            "status": status,
            "result": result,
        }

    @classmethod
    def _record_agent_ops(
        cls,
        *,
        run_id: str,
        tenant_id: str,
        capability_key: str,
        status: str,
        runtime: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        capability = resolve_neuroassist_capability(capability_key)
        get_agent_ops_service().record_run(
            tenant_id=tenant_id,
            run_id=run_id,
            capability_key=capability_key,
            role_key=capability.role_key,
            status=status,
            current_stage_key=runtime.get("current_stage_key") or result.get("current_stage_key") or "closure",
            runtime=runtime,
            result=result,
        )

    @classmethod
    def _resolve_registered_run(cls, run_id: str) -> dict[str, Any]:
        run = cls._run_registry.get(run_id)
        if run is None:
            raise NeuroAssistRunNotFoundError(f"NeuroASSIST run '{run_id}' not found")
        return run

    @classmethod
    def _update_registered_run(
        cls,
        run_id: str,
        *,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> None:
        run = cls._resolve_registered_run(run_id)
        run["status"] = status
        if result is not None:
            run["result"] = result

    async def run_capability(
        self,
        capability_key: str,
        *,
        tenant_id: str = "system",
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        correlation_id = str(uuid4())
        started_at = datetime.utcnow().isoformat()
        try:
            contract = validate_capability_input(
                capability_key,
                tenant_id=tenant_id,
                parameters=parameters,
            )
        except (ValidationError, KeyError) as exc:
            raise NeuroAssistInputContractError(str(exc)) from exc

        capability = resolve_neuroassist_capability(capability_key)
        try:
            get_agent_ops_service().enforce_budget(tenant_id, capability_key)
        except AgentBudgetGuardrailExceededError as exc:
            raise NeuroAssistInputContractError(str(exc)) from exc
        # Use generic workflow runner if available, otherwise fall back to direct execution
        try:
            workflow_runner = self._resolve_workflow_runner(capability_key)
            # Use workflow-based execution
            workflow_result = await workflow_runner.trigger(tenant_id, correlation_id)
            # Project the result to NeuroAssistRun
            projected_result = {
                "workflow_id": workflow_result.get("workflow_id", correlation_id),
                "current_stage_key": workflow_result.get("current_stage_key") or "intake",
                "gate_decisions": workflow_result.get("gate_decisions", []),
                "approval_requirement": workflow_result.get("approval_requirement"),
                "approval_record": workflow_result.get("approval_record"),
                "command_result": workflow_result.get("command_result"),
                "order_id": workflow_result.get("order_id"),
                "proposal": workflow_result.get("proposal"),
                "entity_id": workflow_result.get("entity_id"),
                "entity_type": workflow_result.get("entity_type"),
                "violations": workflow_result.get("violations"),
                "risk_score": workflow_result.get("risk_score"),
                "recommendations": workflow_result.get("recommendations"),
                "checked_at": workflow_result.get("checked_at"),
                "payload_snapshot": workflow_result.get("payload_snapshot"),
                "ingestion_context": workflow_result.get("ingestion_context"),
                "dq_findings": workflow_result.get("dq_findings"),
                "root_cause_summary": workflow_result.get("root_cause_summary"),
                "remediation_plan": workflow_result.get("remediation_plan"),
                "exception_code": workflow_result.get("exception_code"),
                "exception_context": workflow_result.get("exception_context"),
                "exception_summary": workflow_result.get("exception_summary"),
                "proposed_actions": workflow_result.get("proposed_actions"),
                "escalation_target": workflow_result.get("escalation_target"),
                "process_definition_key": workflow_result.get("process_definition_key"),
                "aggregate_type": workflow_result.get("aggregate_type"),
                "aggregate_id": workflow_result.get("aggregate_id"),
            }
            # Remove None values
            projected_result = {k: v for k, v in projected_result.items() if v is not None}
            
            payload = self._project_runner_result_payload(
                capability_key,
                run_id=correlation_id,
                tenant_id=tenant_id,
                status=workflow_result.get("status", "pending_approval"),
                started_at=started_at,
                result=projected_result,
            )
            self._register_run(
                correlation_id,
                capability_key=capability_key,
                tenant_id=tenant_id,
                started_at=started_at,
                status=workflow_result.get("status", "pending_approval"),
                result=payload,
            )
            runtime = workflow_result.get("runtime", {})
            self._record_agent_ops(
                run_id=correlation_id,
                tenant_id=tenant_id,
                capability_key=capability_key,
                status=workflow_result.get("status", "pending_approval"),
                runtime=runtime,
                result=payload,
            )
            return {
                "run_id": correlation_id,
                "correlation_id": correlation_id,
                "capability_key": capability_key,
                "status": workflow_result.get("status", "pending_approval"),
                "started_at": started_at,
                "runtime": runtime,
                "result": payload,
            }
        except (KeyError, NeuroAssistInputContractError):
            # Fallback to direct capability-specific execution if no workflow runner is registered
            runner_definition = self._resolve_runner_definition(capability_key)
            execute_handler = getattr(self, runner_definition.execute_method)
            return await execute_handler(
                contract,
                run_id=correlation_id,
                started_at=started_at,
                tenant_id=tenant_id,
            )

    async def get_run_status(self, run_id: str) -> dict[str, Any]:
        run = self._resolve_registered_run(run_id)
        capability_key = run["capability_key"]

        # Try to get status from workflow runner if available
        try:
            workflow_runner = self._resolve_workflow_runner(capability_key)
            workflow_result = await workflow_runner.get_status(run["result"].get("workflow_id", run_id))
            
            # Project the workflow result to our format
            projected_result = {
                "workflow_id": workflow_result.get("workflow_id", run_id),
                "current_stage_key": workflow_result.get("current_stage_key") or "intake",
                "gate_decisions": workflow_result.get("gate_decisions", []),
                "approval_requirement": workflow_result.get("approval_requirement"),
                "approval_record": workflow_result.get("approval_record"),
                "command_result": workflow_result.get("command_result"),
                "order_id": workflow_result.get("order_id"),
                "proposal": workflow_result.get("proposal"),
                "entity_id": workflow_result.get("entity_id"),
                "entity_type": workflow_result.get("entity_type"),
                "violations": workflow_result.get("violations"),
                "risk_score": workflow_result.get("risk_score"),
                "recommendations": workflow_result.get("recommendations"),
                "checked_at": workflow_result.get("checked_at"),
                "payload_snapshot": workflow_result.get("payload_snapshot"),
                "ingestion_context": workflow_result.get("ingestion_context"),
                "dq_findings": workflow_result.get("dq_findings"),
                "root_cause_summary": workflow_result.get("root_cause_summary"),
                "remediation_plan": workflow_result.get("remediation_plan"),
                "exception_code": workflow_result.get("exception_code"),
                "exception_context": workflow_result.get("exception_context"),
                "exception_summary": workflow_result.get("exception_summary"),
                "proposed_actions": workflow_result.get("proposed_actions"),
                "escalation_target": workflow_result.get("escalation_target"),
                "process_definition_key": workflow_result.get("process_definition_key"),
                "aggregate_type": workflow_result.get("aggregate_type"),
                "aggregate_id": workflow_result.get("aggregate_id"),
            }
            # Remove None values
            projected_result = {k: v for k, v in projected_result.items() if v is not None}
            
            payload = self._project_runner_result_payload(
                capability_key,
                run_id=run_id,
                tenant_id=run["tenant_id"],
                status=workflow_result.get("status", run["status"]),
                started_at=run["started_at"],
                result=projected_result,
            )
            return {
                "run_id": run_id,
                "correlation_id": run_id,
                "capability_key": capability_key,
                "status": workflow_result.get("status", run["status"]),
                "started_at": run["started_at"],
                "runtime": workflow_result.get("runtime", {}),
                "result": payload,
            }
        except (KeyError, AttributeError, NeuroAssistInputContractError):
            # Fallback to registered runtime status
            return await self._get_registered_runtime_status(run_id, run)

    async def apply_gate_action(
        self,
        run_id: str,
        *,
        gate_type: str,
        decision: str,
        rejection_reason: str | None = None,
    ) -> dict[str, Any]:
        run = self._resolve_registered_run(run_id)
        runner_definition = self._runner_registry.get(run["capability_key"])
        if runner_definition is None or runner_definition.gate_action_method is None:
            raise NeuroAssistGateActionError(
                f"Capability '{run['capability_key']}' does not expose a generic gate action handler"
            )
        gate_handler = getattr(self, runner_definition.gate_action_method)
        return await gate_handler(
            run_id,
            run=run,
            gate_type=gate_type,
            decision=decision,
            rejection_reason=rejection_reason,
        )

    async def _run_bestellvorschlag_capability(
        self,
        contract: BestellvorschlagRunInput,
        *,
        run_id: str,
        started_at: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        result = await self.trigger_bestellvorschlag(contract.tenant_id, workflow_id=run_id)
        projected_result = {
            "workflow_id": result["workflow_id"],
            "current_stage_key": result["runtime"]["current_stage_key"],
            "gate_decisions": result["runtime"]["gate_decisions"],
            "approval_requirement": result["runtime"].get("approval_requirement"),
            "approval_record": result["runtime"].get("approval_record"),
        }
        payload = self._project_runner_result_payload(
            "bestellvorschlag_assistant",
            run_id=run_id,
            tenant_id=contract.tenant_id,
            status=result["status"],
            started_at=result["started_at"],
            result=projected_result,
        )
        self._register_run(
            run_id,
            capability_key="bestellvorschlag_assistant",
            tenant_id=contract.tenant_id,
            started_at=result["started_at"],
            status=result["status"],
            result=payload,
        )
        self._record_agent_ops(
            run_id=run_id,
            tenant_id=contract.tenant_id,
            capability_key="bestellvorschlag_assistant",
            status=result["status"],
            runtime=result["runtime"],
            result=payload,
        )
        return {
            "run_id": run_id,
            "correlation_id": result["correlation_id"],
            "capability_key": "bestellvorschlag_assistant",
            "status": result["status"],
            "started_at": result["started_at"],
            "runtime": result["runtime"],
            "result": payload,
        }

    async def _run_finance_skonto_capability(
        self,
        contract: FinanceSkontoRunInput,
        *,
        run_id: str,
        started_at: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        result = await self.run_skonto_assistant(
            available_cash=contract.available_cash,
            payment_date=contract.payment_date,
        )
        return self._finalize_registered_sync_run(
            "finance_skonto_assistant",
            tenant_id=tenant_id,
            run_id=run_id,
            started_at=started_at,
            result=result,
        )

    async def _run_compliance_capability(
        self,
        contract: ComplianceCopilotRunInput,
        *,
        run_id: str,
        started_at: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        result = await self.run_compliance_copilot(
            entity_type=contract.entity_type,
            entity_id=contract.entity_id,
            entity_data=contract.entity_data,
        )
        return self._finalize_registered_sync_run(
            "compliance_copilot",
            tenant_id=tenant_id,
            run_id=run_id,
            started_at=started_at,
            result=result,
        )

    async def _run_data_quality_capability(
        self,
        contract: DataQualityAssistantRunInput,
        *,
        run_id: str,
        started_at: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        result = await self.run_data_quality_assistant(
            entity_type=contract.entity_type,
            payload_snapshot=contract.payload_snapshot,
            dq_findings=contract.dq_findings,
            ingestion_context=contract.ingestion_context,
        )
        return self._finalize_registered_sync_run(
            "data_quality_assistant",
            tenant_id=tenant_id,
            run_id=run_id,
            started_at=started_at,
            result=result,
        )

    async def _run_operations_exception_capability(
        self,
        contract: OperationsExceptionRunInput,
        *,
        run_id: str,
        started_at: str,
        tenant_id: str,
    ) -> dict[str, Any]:
        result = await self.run_operations_exception_assistant(
            process_definition_key=contract.process_definition_key,
            exception_code=contract.exception_code,
            exception_context=contract.exception_context,
            aggregate_type=contract.aggregate_type,
            aggregate_id=contract.aggregate_id,
            evidence_refs=contract.evidence_refs,
        )
        return self._finalize_registered_sync_run(
            "operations_exception_assistant",
            tenant_id=tenant_id,
            run_id=run_id,
            started_at=started_at,
            result=result,
        )

    async def _get_bestellvorschlag_run_status(
        self,
        run_id: str,
        run: dict[str, Any],
    ) -> dict[str, Any]:
        if run["status"] in {"completed", "rejected"} and run["result"].get("current_stage_key"):
            payload = run["result"]
            runtime = self._project_runner_runtime(
                "bestellvorschlag_assistant",
                status=run["status"],
                result=payload,
            )
            return {
                "run_id": run_id,
                "correlation_id": run_id,
                "capability_key": "bestellvorschlag_assistant",
                "started_at": run["started_at"],
                "status": run["status"],
                "runtime": runtime,
                "result": payload,
            }

        status_payload = await self.get_bestellvorschlag_status(run_id)
        return {
            "run_id": run_id,
            "correlation_id": run_id,
            "capability_key": "bestellvorschlag_assistant",
            "started_at": run["started_at"],
            "status": status_payload["status"],
            "runtime": status_payload["runtime"],
            "result": self._project_runner_result_payload(
                "bestellvorschlag_assistant",
                run_id=run_id,
                tenant_id=run["tenant_id"],
                status=status_payload["status"],
                started_at=run["started_at"],
                result=status_payload,
            ),
        }

    async def _get_registered_runtime_status(
        self,
        run_id: str,
        run: dict[str, Any],
    ) -> dict[str, Any]:
        capability_key = run["capability_key"]
        capability_result = run["result"]
        current_stage_key = capability_result.get("current_stage_key") or "closure"
        runtime = self._project_runner_runtime(
            capability_key,
            status=run["status"],
            result={
                **capability_result,
                "current_stage_key": current_stage_key,
            },
        )
        return {
            "run_id": run_id,
            "correlation_id": run_id,
            "capability_key": capability_key,
            "started_at": run["started_at"],
            "status": run["status"],
            "runtime": runtime,
            "result": capability_result,
        }

    async def _apply_bestellvorschlag_gate_action(
        self,
        run_id: str,
        *,
        run: dict[str, Any],
        gate_type: str,
        decision: str,
        rejection_reason: str | None = None,
    ) -> dict[str, Any]:
        if gate_type != "approval_gate":
            raise NeuroAssistGateActionError(
                f"Unsupported gate_type '{gate_type}' for capability 'bestellvorschlag_assistant'"
            )
        if decision not in {"approve", "reject"}:
            raise NeuroAssistGateActionError(f"Unsupported gate decision '{decision}'")

        approved = decision == "approve"
        result = await self._resolve_workflow_runner("bestellvorschlag_assistant").resume(
            run_id,
            approved=approved,
            rejection_reason=rejection_reason,
        )
        status = "completed" if result.get("order_id") else "rejected"
        projected_result = {
            "workflow_id": run_id,
            "proposal": result.get("proposal"),
            "approval_requirement": result.get("approval_requirement"),
            "approval_record": result.get("approval_record"),
            "command_result": result.get("command_result"),
            "order_id": result.get("order_id"),
            "created_at": (
                result.get("created_at").isoformat()
                if result.get("created_at") is not None
                else None
            ),
            "current_stage_key": (
                result.get("current_stage_key")
                or ("closure" if status == "completed" else "approval")
            ),
            "stage_transition_log": result.get("stage_transition_log"),
            "gate_decisions": result.get("gate_decisions"),
            "approved": approved,
            "rejection_reason": rejection_reason,
        }
        runtime = self._project_runner_runtime(
            "bestellvorschlag_assistant",
            status=status,
            result=projected_result,
        )
        payload = self._project_runner_result_payload(
            "bestellvorschlag_assistant",
            run_id=run_id,
            tenant_id=run["tenant_id"],
            status=status,
            started_at=run["started_at"],
            result=projected_result,
        )
        self._update_registered_run(run_id, status=status, result=payload)
        self._record_agent_ops(
            run_id=run_id,
            tenant_id=run["tenant_id"],
            capability_key="bestellvorschlag_assistant",
            status=status,
            runtime=runtime,
            result=payload,
        )
        return {
            "run_id": run_id,
            "correlation_id": run_id,
            "capability_key": "bestellvorschlag_assistant",
            "started_at": run["started_at"],
            "status": status,
            "runtime": runtime,
            "result": payload,
        }

    async def trigger_bestellvorschlag(self, tenant_id: str, *, workflow_id: str | None = None) -> dict[str, Any]:
        correlation_id = workflow_id or str(uuid4())
        result = await self._resolve_workflow_runner("bestellvorschlag_assistant").trigger(
            tenant_id,
            correlation_id,
        )
        status = result["status"]
        projected_result = {
            "workflow_id": result["workflow_id"],
            "approval_requirement": result.get("approval_requirement"),
            "approval_record": result.get("approval_record"),
            "gate_decisions": result.get("gate_decisions"),
            "approved": result.get("approved"),
            "rejection_reason": result.get("rejection_reason"),
            "current_stage_key": result.get("current_stage_key"),
        }
        runtime = self._project_runner_runtime(
            "bestellvorschlag_assistant",
            status=status,
            result=projected_result,
        )
        return {
            "workflow_id": correlation_id,
            "correlation_id": correlation_id,
            "status": status,
            "started_at": datetime.utcnow().isoformat(),
            "capability_key": "bestellvorschlag_assistant",
            "runtime": runtime,
        }

    async def approve_bestellvorschlag(
        self,
        workflow_id: str,
        approved: bool,
        rejection_reason: str | None = None,
    ) -> dict[str, Any]:
        decision = "approve" if approved else "reject"
        action = await self.apply_gate_action(
            workflow_id,
            gate_type="approval_gate",
            decision=decision,
            rejection_reason=rejection_reason,
        )
        payload = action["result"]
        return {
            "workflow_id": workflow_id,
            "approved": approved,
            "order_id": payload.get("order_id"),
            "status": action["status"],
            "capability_key": "bestellvorschlag_assistant",
            "runtime": action["runtime"],
        }

    async def get_bestellvorschlag_status(self, workflow_id: str) -> dict[str, Any]:
        status_payload = await self._resolve_workflow_runner("bestellvorschlag_assistant").get_status(
            workflow_id
        )
        projected_result = {
            "workflow_id": status_payload["workflow_id"],
            "proposal": status_payload.get("proposal"),
            "approval_requirement": status_payload.get("approval_requirement"),
            "approval_record": status_payload.get("approval_record"),
            "command_result": status_payload.get("command_result"),
            "order_id": status_payload.get("order_id"),
            "created_at": status_payload.get("created_at"),
            "current_stage_key": status_payload.get("current_stage_key"),
            "stage_transition_log": status_payload.get("stage_transition_log"),
            "gate_decisions": status_payload.get("gate_decisions"),
            "approved": status_payload.get("approved"),
            "rejection_reason": status_payload.get("rejection_reason"),
        }
        runtime = self._project_runner_runtime(
            "bestellvorschlag_assistant",
            status=status_payload["status"],
            result=projected_result,
        )
        return {
            "workflow_id": workflow_id,
            "status": status_payload["status"],
            **projected_result,
            "capability_key": "bestellvorschlag_assistant",
            "runtime": runtime,
        }

    async def list_runs(
        self,
        *,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        runs = sorted(
            self._run_registry.items(),
            key=lambda item: item[1]["started_at"],
            reverse=True,
        )
        payload: list[dict[str, Any]] = []
        for run_id, run in runs:
            if status is not None and run["status"] != status:
                continue
            payload.append(await self.get_run_status(run_id))
            if len(payload) >= limit:
                break
        return payload

    async def run_skonto_assistant(
        self,
        *,
        available_cash: Decimal,
        payment_date: datetime | None = None,
    ) -> dict[str, Any]:
        result = await optimize_skonto(available_cash=available_cash, payment_date=payment_date)
        result["capability_key"] = "finance_skonto_assistant"
        result["runtime"] = self._resolve_runtime(
            "finance_skonto_assistant",
            status="completed",
            current_stage_key=result.get("current_stage_key") or "closure",
            context={
                "policy_blocked": False,
                "gate_decisions": result.get("gate_decisions"),
            },
        ).model_dump(mode="json")
        return result

    async def run_compliance_copilot(
        self,
        *,
        entity_type: str,
        entity_id: str,
        entity_data: dict[str, Any],
    ) -> dict[str, Any]:
        result = await check_compliance(entity_type=entity_type, entity_id=entity_id, entity_data=entity_data)
        result["capability_key"] = "compliance_copilot"
        result["runtime"] = self._resolve_runtime(
            "compliance_copilot",
            status="completed",
            current_stage_key=result.get("current_stage_key") or "closure",
            context={
                "policy_blocked": bool(result.get("violations")),
                "gate_decisions": result.get("gate_decisions"),
            },
        ).model_dump(mode="json")
        return result

    async def run_data_quality_assistant(
        self,
        *,
        entity_type: str,
        payload_snapshot: dict[str, Any],
        dq_findings: list[dict[str, Any]] | None = None,
        ingestion_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = await run_data_quality_assistant(
            entity_type=entity_type,
            payload_snapshot=payload_snapshot,
            dq_findings=dq_findings,
            ingestion_context=ingestion_context,
        )
        status = "pending_approval" if any(
            decision.get("gate_type") == "approval_gate" and decision.get("status") == "deferred"
            for decision in result["gate_decisions"]
        ) else "completed"
        result["capability_key"] = "data_quality_assistant"
        result["runtime"] = self._resolve_runtime(
            "data_quality_assistant",
            status=status,
            current_stage_key=result.get("current_stage_key") or "closure",
            context={
                "dq_findings": result.get("dq_findings"),
                "gate_decisions": result.get("gate_decisions"),
            },
        ).model_dump(mode="json")
        return result

    async def run_operations_exception_assistant(
        self,
        *,
        process_definition_key: str,
        exception_code: str,
        exception_context: dict[str, Any] | None = None,
        aggregate_type: str | None = None,
        aggregate_id: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        result = await run_operations_exception_assistant(
            process_definition_key=process_definition_key,
            exception_code=exception_code,
            exception_context=exception_context,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            evidence_refs=evidence_refs,
        )
        status = "pending_approval" if any(
            decision.get("gate_type") == "approval_gate" and decision.get("status") == "deferred"
            for decision in result["gate_decisions"]
        ) else "completed"
        result["capability_key"] = "operations_exception_assistant"
        result["runtime"] = self._resolve_runtime(
            "operations_exception_assistant",
            status=status,
            current_stage_key=result.get("current_stage_key") or "closure",
            context={
                "process_definition_key": result.get("process_definition_key"),
                "gate_decisions": result.get("gate_decisions"),
            },
        ).model_dump(mode="json")
        return result


_neuroassist_service: NeuroAssistService | None = None


def get_neuroassist_service() -> NeuroAssistService:
    global _neuroassist_service
    if _neuroassist_service is None:
        _neuroassist_service = NeuroAssistService()
    return _neuroassist_service
