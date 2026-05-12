from __future__ import annotations

import asyncio
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.agents import get_agent_ops_service
from app.agents.neuroassist_service import NeuroAssistService


@pytest.fixture(autouse=True)
def _reset_agent_ops_state():
    with patch("app.agents.agent_ops.load_agent_ops_tenant_snapshot", return_value=None):
        get_agent_ops_service().reset()
        NeuroAssistService._run_registry.clear()
        yield


def test_neuroassist_service_lists_productive_capabilities():
    service = NeuroAssistService()

    capabilities = service.list_capabilities(productive_only=True)

    assert [cap.capability_key for cap in capabilities] == [
        "bestellvorschlag_assistant",
        "finance_skonto_assistant",
        "compliance_copilot",
        "data_quality_assistant",
        "operations_exception_assistant",
    ]
    assert capabilities[0].role_key == "procurement_assistant"
    assert capabilities[0].orchestration_pattern == "decision_workflow"


def test_neuroassist_service_runs_skonto_assistant():
    service = NeuroAssistService()

    result = asyncio.run(service.run_skonto_assistant(available_cash=Decimal("10000.00")))

    assert result["capability_key"] == "finance_skonto_assistant"
    assert result["runtime"]["current_stage_key"] == "closure"
    assert result["runtime"]["stage_runs"][-1]["status"] == "completed"
    assert result["gate_decisions"][0]["gate_type"] == "policy_gate"
    assert "recommendations" in result


def test_neuroassist_service_runs_compliance_copilot():
    service = NeuroAssistService()

    result = asyncio.run(
        service.run_compliance_copilot(
            entity_type="customer",
            entity_id="C-1",
            entity_data={"name": "Demo Kunde", "psm_sachkundenachweis": False},
        )
    )

    assert result["capability_key"] == "compliance_copilot"
    assert result["runtime"]["orchestration_pattern"] == "review_workflow"
    assert result["current_stage_key"] == "closure"
    assert result["gate_decisions"][0]["gate_type"] == "policy_gate"
    assert result["entity_id"] == "C-1"
    assert result["violations"]


def test_neuroassist_service_trigger_bestellvorschlag_projects_pending_approval_runtime(
    monkeypatch: pytest.MonkeyPatch,
):
    class _FakeRunner:
        async def trigger(self, tenant_id: str, workflow_id: str):
            return {
                "workflow_id": workflow_id,
                "correlation_id": workflow_id,
                "status": "pending_approval",
                "started_at": "2026-03-16T00:00:00",
                "approval_requirement": {"requires_human_approval": True},
                "approval_record": None,
                "gate_decisions": [
                    {
                        "gate_type": "approval_gate",
                        "status": "deferred",
                        "reason": "Human approval is still pending before execution.",
                        "required_role": "human_operator",
                        "schema_version": 1,
                    }
                ],
                "approved": False,
                "rejection_reason": None,
                "current_stage_key": "approval",
            }

    monkeypatch.setattr(
        NeuroAssistService,
        "_resolve_workflow_runner",
        classmethod(lambda cls, capability_key: _FakeRunner()),
    )
    service = NeuroAssistService()

    result = asyncio.run(service.trigger_bestellvorschlag("tenant-1"))

    assert result["status"] == "pending_approval"
    assert result["runtime"]["current_stage_key"] == "approval"
    approval_gate = next(
        decision
        for decision in result["runtime"]["gate_decisions"]
        if decision["gate_type"] == "approval_gate"
    )
    assert approval_gate["status"] == "deferred"


def test_neuroassist_service_runs_generic_finance_capability():
    service = NeuroAssistService()

    result = asyncio.run(
        service.run_capability(
            "finance_skonto_assistant",
            parameters={"available_cash": "10000.00"},
        )
    )

    assert result["capability_key"] == "finance_skonto_assistant"
    assert result["status"] == "completed"
    assert result["runtime"]["current_stage_key"] == "closure"
    assert result["result"]["gate_decisions"][0]["gate_type"] == "policy_gate"
    assert result["result"]["audit_record"]["workflow_schema_key"] == "review_workflow"
    assert result["result"]["context_resolution"]["status"] == "partially_resolved"
    assert result["result"]["context_resolution"]["process_definition_key"] == "settlement_to_finance"
    assert "process_audit_entry" not in result["result"]

    overview = get_agent_ops_service().build_overview("system")
    assert overview.monthly_run_count == 1
    assert overview.spent_total_cents > 0
    assert overview.cost_ledger[0].capability_key == "finance_skonto_assistant"
    assert any(heartbeat.last_run_id == result["run_id"] for heartbeat in overview.heartbeats)


def test_neuroassist_service_runs_data_quality_capability():
    service = NeuroAssistService()

    result = asyncio.run(
        service.run_capability(
            "data_quality_assistant",
            parameters={
                "entity_type": "Artikel",
                "payload_snapshot": {"artikelnummer": "A-1"},
                "dq_findings": [{"feld": "mehrwertsteuer_prozent", "severity": "FEHLER", "meldung": "ungueltig"}],
                "ingestion_context": {"source": "csv_import"},
            },
        )
    )

    assert result["capability_key"] == "data_quality_assistant"
    assert result["status"] == "pending_approval"
    assert result["runtime"]["orchestration_pattern"] == "ingestion_workflow"
    assert result["result"]["gate_decisions"][0]["gate_type"] == "dq_gate"
    assert result["result"]["audit_record"]["workflow_schema_key"] == "ingestion_workflow"
    assert result["result"]["context_resolution"]["status"] == "unmappable"


def test_neuroassist_service_runs_operations_exception_capability():
    service = NeuroAssistService()

    result = asyncio.run(
        service.run_capability(
            "operations_exception_assistant",
            parameters={
                "process_definition_key": "quality_to_settlement",
                "exception_code": "SETTLEMENT_MISMATCH",
                "aggregate_type": "agrar_settlement",
                "aggregate_id": "SET-1",
                "exception_context": {"deviation": "weight_mismatch"},
            },
        )
    )

    assert result["capability_key"] == "operations_exception_assistant"
    assert result["status"] == "pending_approval"
    assert result["runtime"]["orchestration_pattern"] == "exception_workflow"
    assert any(
        decision["gate_type"] == "process_gate" and decision["status"] == "escalated"
        for decision in result["result"]["gate_decisions"]
    )
    assert result["result"]["audit_record"]["workflow_schema_key"] == "exception_workflow"
    assert result["result"]["context_resolution"]["status"] == "resolved"
    assert result["result"]["process_audit_entry"]["process_definition_key"] == "quality_to_settlement"
    assert result["result"]["process_audit_entry"]["aggregate_type"] == "agrar_settlement"

    tickets = get_agent_ops_service().list_tickets()
    assert tickets
    assert tickets[0].goal_key == "operations_exception_assistant.goal"
    assert tickets[0].capability_key == "operations_exception_assistant"


def test_neuroassist_service_reads_generic_run_status_for_sync_capability():
    service = NeuroAssistService()
    run = asyncio.run(
        service.run_capability(
            "finance_skonto_assistant",
            parameters={"available_cash": "10000.00"},
        )
    )

    status = asyncio.run(service.get_run_status(run["run_id"]))

    assert status["capability_key"] == "finance_skonto_assistant"
    assert status["status"] == "completed"
    assert status["result"]["current_stage_key"] == "closure"
    assert status["result"]["audit_record"]["capability_key"] == "finance_skonto_assistant"
    assert status["result"]["context_resolution"]["workflow_ref"]["process_definition_key"] == "settlement_to_finance"
    assert "process_audit_entry" not in status["result"]


def test_neuroassist_service_reads_generic_run_status_for_bestellvorschlag(
    monkeypatch: pytest.MonkeyPatch,
):
    class _FakeRunner:
        async def trigger(self, tenant_id: str, workflow_id: str):
            return {
                "workflow_id": workflow_id,
                "correlation_id": workflow_id,
                "status": "pending_approval",
                "started_at": "2026-03-16T00:00:00",
                "approval_requirement": {"requires_human_approval": True},
                "approval_record": None,
                "gate_decisions": [],
                "approved": False,
                "rejection_reason": None,
                "current_stage_key": "approval",
            }

        async def get_status(self, workflow_id: str):
            return {
                "workflow_id": workflow_id,
                "status": "pending_approval",
                "proposal": {"items": []},
                "approval_requirement": {"requires_human_approval": True},
                "approval_record": None,
                "command_result": None,
                "order_id": None,
                "created_at": None,
                "current_stage_key": "approval",
                "stage_transition_log": [{"stage_key": "approval"}],
                "gate_decisions": [{"gate_type": "approval_gate", "status": "deferred"}],
                "approved": False,
                "rejection_reason": None,
            }

    monkeypatch.setattr(
        NeuroAssistService,
        "_resolve_workflow_runner",
        classmethod(lambda cls, capability_key: _FakeRunner()),
    )
    service = NeuroAssistService()

    run = asyncio.run(
        service.run_capability(
            "bestellvorschlag_assistant",
            tenant_id="tenant-1",
        )
    )
    status = asyncio.run(service.get_run_status(run["run_id"]))

    assert status["capability_key"] == "bestellvorschlag_assistant"
    assert status["status"] == "pending_approval"
    assert status["result"]["current_stage_key"] == "approval"


def test_neuroassist_service_applies_generic_gate_action_for_bestellvorschlag(
    monkeypatch: pytest.MonkeyPatch,
):
    class _FakeRunner:
        async def resume(self, workflow_id: str, *, approved: bool, rejection_reason: str | None = None):
            return {
                "proposal": {"items": []},
                "approval_requirement": {"requires_human_approval": True},
                "approval_record": {"decision": "GENEHMIGT" if approved else "ABGELEHNT"},
                "command_result": {"status": "executed"} if approved else None,
                "order_id": "PO-1" if approved else None,
                "created_at": None,
                "current_stage_key": "closure" if approved else "approval",
                "stage_transition_log": [{"stage_key": "closure" if approved else "approval"}],
                "gate_decisions": [
                    {
                        "gate_type": "approval_gate",
                        "status": "allowed" if approved else "blocked",
                        "reason": (
                            "Human approval granted for the proposed action."
                            if approved
                            else "Human approval rejected the proposed action."
                        ),
                        "required_role": "human_operator",
                        "schema_version": 1,
                    }
                ],
            }

    monkeypatch.setattr(
        NeuroAssistService,
        "_resolve_workflow_runner",
        classmethod(lambda cls, capability_key: _FakeRunner()),
    )
    service = NeuroAssistService()
    service._register_run(
        "run-1",
        capability_key="bestellvorschlag_assistant",
        tenant_id="tenant-1",
        started_at="2026-03-16T00:00:00",
        status="pending_approval",
        result={"workflow_id": "run-1"},
    )

    result = asyncio.run(
        service.apply_gate_action(
            "run-1",
            gate_type="approval_gate",
            decision="approve",
        )
    )

    assert result["status"] == "completed"
    assert result["result"]["order_id"] == "PO-1"
    status = asyncio.run(service.get_run_status("run-1"))
    assert status["status"] == "completed"


def test_neuroassist_service_rejects_unsupported_gate_action():
    service = NeuroAssistService()
    service._register_run(
        "run-unsupported",
        capability_key="finance_skonto_assistant",
        tenant_id="tenant-1",
        started_at="2026-03-16T00:00:00",
        status="completed",
        result={"current_stage_key": "closure", "gate_decisions": []},
    )

    with pytest.raises(ValueError, match="does not expose a generic gate action handler"):
        asyncio.run(
            service.apply_gate_action(
                "run-unsupported",
                gate_type="approval_gate",
                decision="approve",
            )
        )


def test_neuroassist_service_rejects_invalid_generic_input_contract():
    service = NeuroAssistService()

    with pytest.raises(ValueError, match="available_cash"):
        asyncio.run(
            service.run_capability(
                "finance_skonto_assistant",
                parameters={},
            )
        )


def test_neuroassist_service_blocks_run_when_budget_is_exhausted():
    service = NeuroAssistService()
    get_agent_ops_service().set_budget("system", "finance_skonto_assistant", 10)

    with pytest.raises(ValueError, match="would be exceeded"):
        asyncio.run(
            service.run_capability(
                "finance_skonto_assistant",
                parameters={"available_cash": "10000.00"},
            )
        )


def test_agent_ops_service_supports_interventions_templates_and_mobile_views():
    service = NeuroAssistService()
    run = asyncio.run(
        service.run_capability(
            "operations_exception_assistant",
            parameters={
                "process_definition_key": "quality_to_settlement",
                "exception_code": "SETTLEMENT_MISMATCH",
                "aggregate_type": "agrar_settlement",
                "aggregate_id": "SET-1",
                "exception_context": {"deviation": "weight_mismatch"},
            },
        )
    )
    ops = get_agent_ops_service()
    ticket = ops.list_tickets()[0]

    intervention = ops.apply_intervention(
        "system",
        ticket.ticket_id,
        action="escalate",
        requested_by="tester",
        note="Need owner review",
    )
    dashboard = ops.build_dashboard("system")
    mobile = ops.build_mobile_overview("system")
    template = ops.export_template("system", template_key="default")
    imported = ops.import_template("system", template)
    skill_packs = ops.list_skill_packs("system")
    boundary = ops.build_plugin_boundary_review("system")

    assert intervention.resulting_status == "escalated"
    assert dashboard.intervention_count == 1
    assert mobile.urgent_ticket_count >= 1
    assert imported.template_key == "default"
    assert skill_packs
    assert any("second agent orchestrator" in item for item in boundary.forbidden_patterns)


def test_agent_ops_service_builds_control_center_and_config_revisions():
    ops = get_agent_ops_service()
    ops.record_run(
        tenant_id="system",
        run_id="run-control-center",
        capability_key="finance_skonto_assistant",
        role_key="finance_action_assistant",
        status="pending_approval",
        current_stage_key="analysis",
        runtime={
            "current_stage_key": "analysis",
            "stage_runs": [{"stage_key": "analysis", "status": "completed"}],
            "gate_decisions": [{"gate_type": "approval_gate", "status": "deferred"}],
        },
        result={"current_stage_key": "analysis"},
    )

    budget = ops.set_budget("system", "finance_skonto_assistant", 1100, changed_by="ops-admin")
    heartbeat = ops.set_heartbeat("system", "finance_skonto_assistant", cadence="hourly", stale_after_hours=2, changed_by="ops-admin")
    profile = ops.set_profile(
        "system",
        "finance_skonto_assistant",
        review_sla_hours=2,
        stale_after_hours=2,
        allowed_actions=["approve", "pause", "escalate"],
        changed_by="ops-admin",
    )
    skill_pack = ops.update_skill_pack(
        "system",
        "finance_action_assistant.pack",
        skills=["policy_guardrails", "cost_control"],
        changed_by="ops-admin",
    )
    control_center = ops.build_control_center("system")

    assert budget.version == 2
    assert heartbeat.version == 2
    assert profile.version == 2
    assert skill_pack.version == 2
    assert control_center.dashboard.review_queue_count >= 1
    assert control_center.dashboard.open_blocker_count >= 1
    assert control_center.tickets[0].requires_review is True
    assert control_center.tickets[0].owner_role == "finance_action_assistant"
    assert control_center.chain_of_command[0].can_intervene is True
    assert any(revision.config_type == "budget" and revision.changed_by == "ops-admin" for revision in control_center.config_revisions)
