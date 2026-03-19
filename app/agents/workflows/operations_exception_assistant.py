"""NeuroASSIST workflow for operational exception handling across process chains."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _mark_stage(state: dict[str, Any], stage_key: str, detail: str) -> None:
    state["current_stage_key"] = stage_key
    state["stage_transition_log"].append(
        {
            "stage_key": stage_key,
            "timestamp": datetime.utcnow().isoformat(),
            "detail": detail,
        }
    )


def _set_gate(
    state: dict[str, Any],
    *,
    gate_type: str,
    status: str,
    reason: str,
    required_role: str | None = None,
    evidence_refs: list[str] | None = None,
) -> None:
    state["gate_decisions"] = [
        decision for decision in state.get("gate_decisions", []) if decision.get("gate_type") != gate_type
    ]
    state["gate_decisions"].append(
        {
            "gate_type": gate_type,
            "status": status,
            "reason": reason,
            "required_role": required_role,
            "evidence_refs": list(evidence_refs or []),
            "schema_version": 1,
        }
    )


async def run_operations_exception_assistant(
    *,
    process_definition_key: str,
    exception_code: str,
    exception_context: dict[str, Any] | None = None,
    aggregate_type: str | None = None,
    aggregate_id: str | None = None,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    context = dict(exception_context or {})
    resolved_evidence_refs = list(evidence_refs or [])
    if aggregate_type:
        resolved_evidence_refs.append(aggregate_type)
    if exception_code not in resolved_evidence_refs:
        resolved_evidence_refs.append(exception_code)

    escalation_target = "operations_lead"
    if process_definition_key == "quality_to_settlement":
        escalation_target = "settlement_supervisor"
    elif process_definition_key == "intake_to_quality":
        escalation_target = "quality_manager"

    state: dict[str, Any] = {
        "process_definition_key": process_definition_key,
        "exception_code": exception_code,
        "exception_context": context,
        "aggregate_type": aggregate_type,
        "aggregate_id": aggregate_id,
        "exception_summary": "",
        "proposed_actions": [],
        "escalation_target": escalation_target,
        "current_stage_key": "intake",
        "stage_transition_log": [
            {
                "stage_key": "intake",
                "timestamp": datetime.utcnow().isoformat(),
                "detail": "Operational exception run created",
            }
        ],
        "gate_decisions": [],
    }

    _mark_stage(state, "analysis", "Analyze operational exception against process context")
    aggregate_label = aggregate_type or "unknown_aggregate"
    state["exception_summary"] = (
        f"Operational exception '{exception_code}' on process '{process_definition_key}' "
        f"for aggregate '{aggregate_label}'."
    )

    _mark_stage(state, "proposal", "Build structured exception handling proposal")
    state["proposed_actions"] = [
        f"Kontext fuer {exception_code} gegen Prozess {process_definition_key} vervollstaendigen.",
        f"Fall an {escalation_target} zur priorisierten Bewertung uebergeben.",
        "Freigabe- oder Prozesssperre erst nach dokumentierter Ursache aufloesen.",
    ]

    _set_gate(
        state,
        gate_type="process_gate",
        status="escalated",
        reason="Die Prozesskette darf erst nach geklaerter Ausnahmeursache fortgesetzt werden.",
        required_role=escalation_target,
        evidence_refs=[process_definition_key, *resolved_evidence_refs],
    )

    _mark_stage(state, "approval", "Prepare human approval handover for exception owner")
    _set_gate(
        state,
        gate_type="approval_gate",
        status="deferred",
        reason="Eine verantwortliche Fachrolle muss die vorgeschlagene Ausnahmebehandlung freigeben.",
        required_role=escalation_target,
        evidence_refs=[process_definition_key, exception_code],
    )

    _mark_stage(state, "execution", "Emit exception runbook instead of forcing process transition")
    _mark_stage(state, "verification", "Verify that exception proposal preserves process contract boundaries")
    _mark_stage(state, "closure", "Close exception run with documented escalation path")

    return {
        "process_definition_key": process_definition_key,
        "exception_code": exception_code,
        "exception_context": context,
        "aggregate_type": aggregate_type,
        "aggregate_id": aggregate_id,
        "exception_summary": state["exception_summary"],
        "proposed_actions": state["proposed_actions"],
        "escalation_target": escalation_target,
        "current_stage_key": state["current_stage_key"],
        "stage_transition_log": state["stage_transition_log"],
        "gate_decisions": state["gate_decisions"],
    }
