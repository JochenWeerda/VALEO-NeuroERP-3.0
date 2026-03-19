"""Workflow-runner adapters for NeuroASSIST capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from .langgraph_server import get_bestellvorschlag_workflow, invoke_bestellvorschlag, resume_bestellvorschlag
from .neuroassist import resolve_neuroassist_capability


class NeuroAssistWorkflowRunner(Protocol):
    """Contract for async/checkpoint-capable workflow runners."""

    async def trigger(self, tenant_id: str, workflow_id: str) -> dict[str, Any]:
        """Start a workflow-backed capability run."""

    async def resume(
        self,
        workflow_id: str,
        *,
        approved: bool,
        rejection_reason: str | None = None,
    ) -> dict[str, Any]:
        """Resume a paused workflow-backed capability run."""

    async def get_status(self, workflow_id: str) -> dict[str, Any]:
        """Read workflow-backed capability status."""


class BestellvorschlagWorkflowRunner:
    """Adapter around the productive Bestellvorschlag LangGraph workflow."""

    async def trigger(self, tenant_id: str, workflow_id: str) -> dict[str, Any]:
        result = await invoke_bestellvorschlag(tenant_id, workflow_id)
        status = "completed" if result.get("order_id") else "pending_approval"
        return {
            "workflow_id": workflow_id,
            "correlation_id": workflow_id,
            "status": status,
            "started_at": datetime.utcnow().isoformat(),
            "approval_requirement": result.get("approval_requirement"),
            "approval_record": result.get("approval_record"),
            "gate_decisions": result.get("gate_decisions"),
            "approved": result.get("approved"),
            "rejection_reason": result.get("rejection_reason"),
            "current_stage_key": (
                result.get("current_stage_key")
                or ("verification" if status == "completed" else "approval")
            ),
        }

    async def resume(
        self,
        workflow_id: str,
        *,
        approved: bool,
        rejection_reason: str | None = None,
    ) -> dict[str, Any]:
        return await resume_bestellvorschlag(workflow_id, approved, rejection_reason)

    async def get_status(self, workflow_id: str) -> dict[str, Any]:
        workflow = get_bestellvorschlag_workflow()
        config = {"configurable": {"thread_id": workflow_id}}
        state = await workflow.aget_state(config)
        if state is None:
            raise ValueError(f"Workflow {workflow_id} not found")

        approval_record = state.values.get("approval_record") or {}
        if state.values.get("order_id"):
            status = "completed"
        elif approval_record.get("decision") == "ABGELEHNT":
            status = "rejected"
        elif (state.values.get("approval_requirement") or {}).get("requires_human_approval"):
            status = "pending_approval"
        else:
            status = "running"

        return {
            "workflow_id": workflow_id,
            "status": status,
            "proposal": state.values.get("proposal"),
            "approval_requirement": state.values.get("approval_requirement"),
            "approval_record": state.values.get("approval_record"),
            "command_result": state.values.get("command_result"),
            "order_id": state.values.get("order_id"),
            "created_at": (
                state.values.get("created_at").isoformat()
                if state.values.get("created_at") is not None
                else None
            ),
            "current_stage_key": state.values.get("current_stage_key") or "approval",
            "stage_transition_log": state.values.get("stage_transition_log"),
            "gate_decisions": state.values.get("gate_decisions"),
            "approved": state.values.get("approved"),
            "rejection_reason": state.values.get("rejection_reason"),
        }


@dataclass(frozen=True)
class WorkflowRunnerRegistration:
    """Registry entry for one workflow-runner adapter."""

    runner_key: str
    capability_key: str
    factory: Any


_WORKFLOW_RUNNER_REGISTRATIONS: tuple[WorkflowRunnerRegistration, ...] = (
    WorkflowRunnerRegistration(
        runner_key="bestellvorschlag_workflow_runner",
        capability_key="bestellvorschlag_assistant",
        factory=BestellvorschlagWorkflowRunner,
    ),
)

_workflow_runner_instances: dict[str, NeuroAssistWorkflowRunner] = {}


def get_workflow_runner(runner_key: str) -> NeuroAssistWorkflowRunner:
    if runner_key in _workflow_runner_instances:
        return _workflow_runner_instances[runner_key]

    for registration in _WORKFLOW_RUNNER_REGISTRATIONS:
        if registration.runner_key == runner_key:
            runner = registration.factory()
            _workflow_runner_instances[runner_key] = runner
            return runner
    raise KeyError(f"Unknown NeuroASSIST workflow runner '{runner_key}'")


def resolve_workflow_runner_for_capability(capability_key: str) -> NeuroAssistWorkflowRunner:
    for registration in _WORKFLOW_RUNNER_REGISTRATIONS:
        if registration.capability_key == capability_key:
            return get_workflow_runner(registration.runner_key)
    raise KeyError(f"No NeuroASSIST workflow runner registered for capability '{capability_key}'")


def list_workflow_runner_registrations() -> tuple[WorkflowRunnerRegistration, ...]:
    return _WORKFLOW_RUNNER_REGISTRATIONS


def validate_workflow_runner_registrations() -> list[str]:
    errors: list[str] = []
    seen_runner_keys: set[str] = set()
    seen_capability_keys: set[str] = set()
    for registration in _WORKFLOW_RUNNER_REGISTRATIONS:
        if registration.runner_key in seen_runner_keys:
            errors.append(f"Duplicate NeuroASSIST workflow runner key: {registration.runner_key}")
        seen_runner_keys.add(registration.runner_key)
        if registration.capability_key in seen_capability_keys:
            errors.append(
                f"Multiple NeuroASSIST workflow runners registered for capability: {registration.capability_key}"
            )
        seen_capability_keys.add(registration.capability_key)
        try:
            resolve_neuroassist_capability(registration.capability_key)
        except KeyError:
            errors.append(
                "Workflow runner registered for unknown NeuroASSIST capability: "
                f"{registration.capability_key}"
            )
        runner = registration.factory()
        for method_name in ("trigger", "resume", "get_status"):
            if not hasattr(runner, method_name):
                errors.append(
                    f"Workflow runner '{registration.runner_key}' is missing method '{method_name}'"
                )
    return errors
