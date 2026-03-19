"""Runtime read models for NeuroASSIST stage and gate execution."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from .neuroassist import NeuroAssistCapability
from .neuroassist_contracts import (
    CaseRun,
    CaseStageTransition,
    GateDecision,
    StageDefinition,
    build_case_run,
    get_stage_definitions,
)

StageRunStatus = Literal["pending", "in_progress", "completed", "blocked", "skipped"]


class StageRun(BaseModel):
    """Runtime status for one configured stage in a workflow run."""

    stage_key: str
    title: str = Field(min_length=2)
    status: StageRunStatus
    allows_side_effects: bool = False
    schema_version: int = 1


class NeuroAssistRun(BaseModel):
    """Runtime projection for one NeuroASSIST workflow/assistant run."""

    capability_key: str = Field(min_length=3)
    workflow_schema_key: str = Field(min_length=3)
    role_key: str = Field(min_length=3)
    orchestration_pattern: str = Field(min_length=3)
    current_stage_key: str = Field(min_length=3)
    status: str = Field(min_length=3)
    stage_runs: list[StageRun] = Field(default_factory=list)
    gate_decisions: list[GateDecision] = Field(default_factory=list)
    schema_version: int = 1


def _build_case_transitions(
    sequence: list[str],
    current_index: int,
    *,
    terminal_status: bool,
    status: str,
) -> list[CaseStageTransition]:
    transitions: list[CaseStageTransition] = []
    for index, stage_key in enumerate(sequence):
        if terminal_status and status == "completed":
            transition_status = "completed"
        elif terminal_status and status == "rejected":
            if index < current_index:
                transition_status = "completed"
            elif index == current_index:
                transition_status = "blocked"
            else:
                transition_status = "skipped"
        elif index < current_index:
            transition_status = "completed"
        elif index == current_index:
            transition_status = "entered"
        else:
            break
        transitions.append(
            CaseStageTransition(
                stage_key=stage_key,  # type: ignore[arg-type]
                timestamp=f"1970-01-{index + 1:02d}T00:00:00",
                status=transition_status,  # type: ignore[arg-type]
            )
        )
    return transitions


_STAGE_INDEX: dict[str, StageDefinition] = {
    stage.stage_key: stage for stage in get_stage_definitions()
}


def _build_stage_run(stage_key: str, status: StageRunStatus) -> StageRun:
    stage = _STAGE_INDEX[stage_key]
    return StageRun(
        stage_key=stage.stage_key,
        title=stage.title,
        status=status,
        allows_side_effects=stage.allows_side_effects,
    )


def _gate_reason(
    gate_type: str,
    context: dict[str, Any],
    capability: NeuroAssistCapability,
) -> tuple[str, str, str | None]:
    if gate_type == "approval_gate":
        approval_requirement = context.get("approval_requirement") or {}
        approval_record = context.get("approval_record") or {}
        if not approval_requirement.get("requires_human_approval"):
            return ("allowed", "No explicit human approval required for this run.", None)
        decision = approval_record.get("decision")
        if decision == "GENEHMIGT" or context.get("approved") is True:
            return ("allowed", "Human approval granted for the proposed action.", "human_operator")
        if decision == "ABGELEHNT" or context.get("rejection_reason"):
            return ("blocked", "Human approval rejected the proposed action.", "human_operator")
        return ("deferred", "Human approval is still pending before execution.", "human_operator")

    if gate_type == "policy_gate":
        if context.get("policy_blocked"):
            return ("blocked", "Policy checks blocked the run before execution.", None)
        return ("allowed", "Policy checks allow the current orchestration path.", None)

    if gate_type == "dq_gate":
        if context.get("dq_blocked"):
            return ("blocked", "Data quality findings block further progression.", None)
        return ("allowed", "No blocking data-quality findings are present.", None)

    if gate_type == "process_gate":
        return (
            "allowed",
            f"Process contract scopes resolved for {', '.join(capability.process_scopes)}.",
            None,
        )

    if gate_type == "role_gate":
        return (
            "allowed",
            f"Role contract '{capability.role_key}' authorizes the exposed actions.",
            capability.role_key,
        )

    return ("allowed", "Gate evaluated without explicit blocker.", None)


def build_gate_decisions(
    capability: NeuroAssistCapability,
    *,
    context: dict[str, Any] | None = None,
) -> list[GateDecision]:
    """Project runtime gate decisions from the capability contract and current state."""

    runtime_context = context or {}
    persisted_gate_decisions = runtime_context.get("gate_decisions") or []
    if persisted_gate_decisions:
        return [GateDecision.model_validate(decision) for decision in persisted_gate_decisions]
    decisions: list[GateDecision] = []
    for gate_type in capability.capability_pack.required_gates:
        status, reason, required_role = _gate_reason(gate_type, runtime_context, capability)
        evidence_refs = [capability.capability_key, capability.role_key]
        if gate_type == "approval_gate" and runtime_context.get("approval_record"):
            evidence_refs.append("approval_record")
        decisions.append(
            GateDecision(
                gate_type=gate_type,
                status=status,  # type: ignore[arg-type]
                reason=reason,
                required_role=required_role,
                evidence_refs=evidence_refs,
            )
        )
    return decisions


def build_neuroassist_run(
    capability: NeuroAssistCapability,
    *,
    status: str,
    current_stage_key: str,
    context: dict[str, Any] | None = None,
) -> NeuroAssistRun:
    """Build a runtime projection from the default stage sequence and gate state."""

    sequence = list(capability.default_stage_sequence)
    if current_stage_key not in sequence:
        raise ValueError(
            f"Current stage '{current_stage_key}' is not part of capability "
            f"'{capability.capability_key}' sequence"
        )

    current_index = sequence.index(current_stage_key)
    stage_runs: list[StageRun] = []
    terminal_status = status in {"completed", "rejected", "failed"}

    for index, stage_key in enumerate(sequence):
        if terminal_status and status == "completed":
            stage_status: StageRunStatus = "completed"
        elif terminal_status and status == "rejected":
            if index < current_index:
                stage_status = "completed"
            elif index == current_index:
                stage_status = "blocked"
            else:
                stage_status = "skipped"
        elif index < current_index:
            stage_status = "completed"
        elif index == current_index:
            stage_status = "in_progress"
        else:
            stage_status = "pending"
        stage_runs.append(_build_stage_run(stage_key, stage_status))

    return NeuroAssistRun(
        capability_key=capability.capability_key,
        workflow_schema_key=capability.workflow_schema_key,
        role_key=capability.role_key,
        orchestration_pattern=capability.orchestration_pattern,
        current_stage_key=current_stage_key,
        status=status,
        stage_runs=stage_runs,
        gate_decisions=build_gate_decisions(capability, context=context),
    )


def build_case_run_projection(
    capability: NeuroAssistCapability,
    *,
    run_id: str,
    tenant_id: str,
    status: str,
    current_stage_key: str,
    context: dict[str, Any] | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
    result_refs: list[str] | None = None,
) -> CaseRun:
    runtime_context = context or {}
    sequence = list(capability.default_stage_sequence)
    current_index = sequence.index(current_stage_key)
    persisted_transitions = runtime_context.get("stage_transition_log") or []
    if persisted_transitions:
        stage_transition_log = []
        for index, transition in enumerate(persisted_transitions):
            normalized_transition = dict(transition)
            normalized_transition.setdefault("timestamp", f"1970-01-{index + 1:02d}T00:00:00")
            normalized_transition.setdefault("status", "entered")
            stage_transition_log.append(CaseStageTransition.model_validate(normalized_transition))
    else:
        stage_transition_log = _build_case_transitions(
            sequence,
            current_index,
            terminal_status=status in {"completed", "rejected", "failed"},
            status=status,
        )
    return build_case_run(
        run_id=run_id,
        capability_key=capability.capability_key,
        workflow_schema_key=capability.workflow_schema_key,
        tenant_id=tenant_id,
        status=status,  # type: ignore[arg-type]
        current_stage_key=current_stage_key,  # type: ignore[arg-type]
        gate_decisions=build_gate_decisions(capability, context=runtime_context),
        stage_transition_log=stage_transition_log,
        result_refs=result_refs or [capability.capability_key],
        started_at=started_at,
        completed_at=completed_at,
    )
