from __future__ import annotations

from app.agents import (
    build_case_run_projection,
    build_neuroassist_run,
    resolve_neuroassist_capability,
)


def test_build_neuroassist_run_marks_pending_approval_gate_as_deferred():
    capability = resolve_neuroassist_capability("bestellvorschlag_assistant")

    runtime = build_neuroassist_run(
        capability,
        status="pending_approval",
        current_stage_key="approval",
        context={
            "approval_requirement": {"requires_human_approval": True},
            "approval_record": None,
            "approved": False,
        },
    )

    assert runtime.current_stage_key == "approval"
    assert [stage.status for stage in runtime.stage_runs[:4]] == [
        "completed",
        "completed",
        "completed",
        "in_progress",
    ]
    approval_gate = next(
        decision for decision in runtime.gate_decisions if decision.gate_type == "approval_gate"
    )
    assert approval_gate.status == "deferred"


def test_build_neuroassist_run_marks_rejected_approval_as_blocked():
    capability = resolve_neuroassist_capability("bestellvorschlag_assistant")

    runtime = build_neuroassist_run(
        capability,
        status="rejected",
        current_stage_key="approval",
        context={
            "approval_requirement": {"requires_human_approval": True},
            "approval_record": {"decision": "ABGELEHNT"},
            "approved": False,
            "rejection_reason": "too expensive",
        },
    )

    assert runtime.stage_runs[3].status == "blocked"
    assert runtime.stage_runs[4].status == "skipped"
    approval_gate = next(
        decision for decision in runtime.gate_decisions if decision.gate_type == "approval_gate"
    )
    assert approval_gate.status == "blocked"


def test_build_case_run_projection_binds_runtime_to_workflow_schema():
    capability = resolve_neuroassist_capability("finance_skonto_assistant")

    case_run = build_case_run_projection(
        capability,
        run_id="run-1",
        tenant_id="tenant-1",
        status="completed",
        current_stage_key="closure",
        context={"gate_decisions": []},
        started_at="2026-03-16T00:00:00",
    )

    assert case_run.workflow_schema_key == "review_workflow"
    assert case_run.current_stage_key == "closure"
    assert case_run.result_refs == ["finance_skonto_assistant"]
    assert case_run.stage_transition_log[-1].stage_key == "closure"
