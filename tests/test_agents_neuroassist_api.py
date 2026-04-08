from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.agents import get_agent_ops_service
from app.agents.neuroassist_service import NeuroAssistService
from app.api.v1.endpoints import agents
from app.integrations.services.superglue_quarantine import append_quarantine_entry


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(agents.router, prefix="/api/v1/agents")
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset_agent_ops_state(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agents.agent_ops_persistence.settings.AGENT_OPS_STATE_PATH", str(tmp_path / "agent-ops-state.json"))
    monkeypatch.setattr("app.agents.agent_ops_persistence.settings.AGENT_OPS_HISTORY_PATH", str(tmp_path / "agent-ops-history.jsonl"))
    get_agent_ops_service().reset()
    NeuroAssistService._run_registry.clear()


def test_neuroassist_capabilities_endpoint_lists_productive_capabilities():
    client = _client()

    response = client.get("/api/v1/agents/neuroassist/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert [item["capability_key"] for item in payload] == [
        "bestellvorschlag_assistant",
        "finance_skonto_assistant",
        "compliance_copilot",
        "data_quality_assistant",
        "operations_exception_assistant",
    ]
    assert payload[0]["role_key"] == "procurement_assistant"
    assert payload[0]["orchestration_pattern"] == "decision_workflow"
    assert payload[0]["default_stage_sequence"] == [
        "intake",
        "analysis",
        "proposal",
        "approval",
        "execution",
        "verification",
        "closure",
    ]
    assert payload[3]["orchestration_pattern"] == "ingestion_workflow"
    assert payload[4]["orchestration_pattern"] == "exception_workflow"


def test_neuroassist_run_endpoint_surfaces_bestellvorschlag_runtime_projection(
    monkeypatch: pytest.MonkeyPatch,
):
    async def _fake_run(capability_key: str, tenant_id: str = "system", parameters: dict | None = None):
        return {
            "run_id": "wf-1",
            "correlation_id": "wf-1",
            "status": "pending_approval",
            "started_at": "2026-03-16T00:00:00",
            "capability_key": capability_key,
            "runtime": {
                "capability_key": capability_key,
                "role_key": "procurement_assistant",
                "orchestration_pattern": "decision_workflow",
                "current_stage_key": "approval",
                "status": "pending_approval",
                "stage_runs": [],
                "gate_decisions": [
                    {
                        "gate_type": "approval_gate",
                        "status": "deferred",
                        "reason": "Human approval is still pending before execution.",
                        "required_role": "human_operator",
                        "evidence_refs": ["bestellvorschlag_assistant"],
                        "schema_version": 1,
                    }
                ],
                "schema_version": 1,
            },
            "result": {"workflow_id": "wf-1"},
        }

    monkeypatch.setattr(agents.neuroassist_service, "run_capability", _fake_run)
    client = _client()

    response = client.post(
        "/api/v1/agents/neuroassist/runs",
        json={"capability_key": "bestellvorschlag_assistant", "tenant_id": "tenant-1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime"]["current_stage_key"] == "approval"
    assert payload["runtime"]["gate_decisions"][0]["status"] == "deferred"

def test_neuroassist_run_status_endpoint_surfaces_persisted_bestellvorschlag_stage_projection(
    monkeypatch: pytest.MonkeyPatch,
):
    async def _fake_status(workflow_id: str):
        return {
            "run_id": workflow_id,
            "correlation_id": workflow_id,
            "status": "pending_approval",
            "capability_key": "bestellvorschlag_assistant",
            "started_at": "2026-03-16T00:00:00",
            "runtime": {
                "capability_key": "bestellvorschlag_assistant",
                "role_key": "procurement_assistant",
                "orchestration_pattern": "decision_workflow",
                "current_stage_key": "approval",
                "status": "pending_approval",
                "stage_runs": [],
                "gate_decisions": [],
                "schema_version": 1,
            },
            "result": {
                "proposal": {"items": []},
                "approval_requirement": {"requires_human_approval": True},
                "approval_record": None,
                "command_result": None,
                "order_id": None,
                "created_at": None,
                "current_stage_key": "approval",
                "stage_transition_log": [
                    {"stage_key": "intake", "timestamp": "2026-03-16T00:00:00+00:00"},
                    {"stage_key": "analysis", "timestamp": "2026-03-16T00:00:01+00:00"},
                    {"stage_key": "proposal", "timestamp": "2026-03-16T00:00:02+00:00"},
                    {"stage_key": "approval", "timestamp": "2026-03-16T00:00:03+00:00"},
                ],
                "gate_decisions": [
                    {
                        "gate_type": "approval_gate",
                        "status": "deferred",
                        "reason": "Human approval is still pending before execution.",
                        "required_role": "human_operator",
                        "schema_version": 1,
                    }
                ],
            },
        }

    monkeypatch.setattr(agents.neuroassist_service, "get_run_status", _fake_status)
    client = _client()

    response = client.get("/api/v1/agents/neuroassist/runs/wf-1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["current_stage_key"] == "approval"
    assert payload["result"]["stage_transition_log"][-1]["stage_key"] == "approval"


def test_neuroassist_runs_endpoint_dispatches_generic_capability(monkeypatch: pytest.MonkeyPatch):
    async def _fake_run(capability_key: str, tenant_id: str = "system", parameters: dict | None = None):
        return {
            "run_id": "run-1",
            "correlation_id": "run-1",
            "capability_key": capability_key,
            "status": "completed",
            "started_at": "2026-03-16T00:00:00",
            "runtime": {
                "capability_key": capability_key,
                "role_key": "finance_action_assistant",
                "orchestration_pattern": "review_workflow",
                "current_stage_key": "closure",
                "status": "completed",
                "stage_runs": [],
                "gate_decisions": [
                    {
                        "gate_type": "policy_gate",
                        "status": "allowed",
                        "reason": "Policy checks allow the current orchestration path.",
                        "required_role": None,
                        "evidence_refs": ["finance_skonto_assistant", "finance_action_assistant"],
                        "schema_version": 1,
                    }
                ],
                "schema_version": 1,
            },
            "result": {
                "total_discount": 400.0,
            },
        }

    monkeypatch.setattr(agents.neuroassist_service, "run_capability", _fake_run)
    client = _client()

    response = client.post(
        "/api/v1/agents/neuroassist/runs",
        json={
            "capability_key": "finance_skonto_assistant",
            "parameters": {"available_cash": "10000.00"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["capability_key"] == "finance_skonto_assistant"
    assert payload["runtime"]["current_stage_key"] == "closure"
    assert payload["result"]["total_discount"] == 400.0


def test_neuroassist_run_status_endpoint_reads_generic_status(monkeypatch: pytest.MonkeyPatch):
    async def _fake_status(run_id: str):
        return {
            "run_id": run_id,
            "correlation_id": run_id,
            "capability_key": "finance_skonto_assistant",
            "started_at": "2026-03-16T00:00:00",
            "status": "completed",
            "runtime": {
                "capability_key": "finance_skonto_assistant",
                "role_key": "finance_action_assistant",
                "orchestration_pattern": "review_workflow",
                "current_stage_key": "closure",
                "status": "completed",
                "stage_runs": [],
                "gate_decisions": [],
                "schema_version": 1,
            },
            "result": {"total_discount": 400.0},
        }

    monkeypatch.setattr(agents.neuroassist_service, "get_run_status", _fake_status)
    client = _client()

    response = client.get("/api/v1/agents/neuroassist/runs/run-1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["capability_key"] == "finance_skonto_assistant"
    assert payload["result"]["total_discount"] == 400.0


def test_neuroassist_gate_action_endpoint_dispatches_generic_approval(monkeypatch: pytest.MonkeyPatch):
    async def _fake_apply(run_id: str, gate_type: str, decision: str, rejection_reason: str | None = None):
        return {
            "run_id": run_id,
            "correlation_id": run_id,
            "capability_key": "bestellvorschlag_assistant",
            "started_at": "2026-03-16T00:00:00",
            "status": "completed",
            "runtime": {
                "capability_key": "bestellvorschlag_assistant",
                "role_key": "procurement_assistant",
                "orchestration_pattern": "decision_workflow",
                "current_stage_key": "closure",
                "status": "completed",
                "stage_runs": [],
                "gate_decisions": [],
                "schema_version": 1,
            },
            "result": {"order_id": "PO-1"},
        }

    monkeypatch.setattr(agents.neuroassist_service, "apply_gate_action", _fake_apply)
    client = _client()

    response = client.post(
        "/api/v1/agents/neuroassist/runs/run-1/gates",
        json={"gate_type": "approval_gate", "decision": "approve"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["capability_key"] == "bestellvorschlag_assistant"
    assert payload["result"]["order_id"] == "PO-1"


def test_neuroassist_gate_endpoint_rejects_bestellvorschlag_via_generic_contract(
    monkeypatch: pytest.MonkeyPatch,
):
    async def _fake_apply(run_id: str, gate_type: str, decision: str, rejection_reason: str | None = None):
        return {
            "run_id": run_id,
            "correlation_id": run_id,
            "capability_key": "bestellvorschlag_assistant",
            "started_at": "2026-03-16T00:00:00",
            "status": "rejected",
            "runtime": {
                "capability_key": "bestellvorschlag_assistant",
                "role_key": "procurement_assistant",
                "orchestration_pattern": "decision_workflow",
                "current_stage_key": "approval",
                "status": "rejected",
                "stage_runs": [],
                "gate_decisions": [],
                "schema_version": 1,
            },
            "result": {"order_id": None},
        }

    monkeypatch.setattr(agents.neuroassist_service, "apply_gate_action", _fake_apply)
    client = _client()

    response = client.post(
        "/api/v1/agents/neuroassist/runs/run-1/gates",
        json={
            "gate_type": "approval_gate",
            "decision": "reject",
            "rejection_reason": "too expensive",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["order_id"] is None
    assert payload["status"] == "rejected"


def test_neuroassist_runs_endpoint_rejects_invalid_input_contract(monkeypatch: pytest.MonkeyPatch):
    async def _fake_run(capability_key: str, tenant_id: str = "system", parameters: dict | None = None):
        raise ValueError("available_cash\n  Field required")

    monkeypatch.setattr(agents.neuroassist_service, "run_capability", _fake_run)
    client = _client()

    response = client.post(
        "/api/v1/agents/neuroassist/runs",
        json={
            "capability_key": "finance_skonto_assistant",
            "parameters": {},
        },
    )

    assert response.status_code == 422
    assert "available_cash" in response.json()["detail"]


def test_neuroassist_ops_overview_endpoint_surfaces_budgeting_and_tickets(monkeypatch: pytest.MonkeyPatch):
    async def _fake_run(capability_key: str, tenant_id: str = "system", parameters: dict | None = None):
        return {
            "run_id": "run-1",
            "correlation_id": "run-1",
            "capability_key": capability_key,
            "status": "pending_approval",
            "started_at": "2026-03-16T00:00:00",
            "runtime": {
                "capability_key": capability_key,
                "role_key": "finance_action_assistant",
                "orchestration_pattern": "review_workflow",
                "current_stage_key": "analysis",
                "status": "pending_approval",
                "stage_runs": [{"stage_key": "analysis", "title": "Analyse", "status": "in_progress"}],
                "gate_decisions": [],
                "schema_version": 1,
            },
            "result": {"current_stage_key": "analysis"},
        }

    monkeypatch.setattr(agents.neuroassist_service, "run_capability", _fake_run)
    client = _client()

    run_response = client.post(
        "/api/v1/agents/neuroassist/runs",
        json={"capability_key": "finance_skonto_assistant"},
    )
    assert run_response.status_code == 200

    monkeypatch.undo()
    from app.agents import get_neuroassist_service

    service = get_neuroassist_service()
    service._record_agent_ops(
        run_id="run-1",
        tenant_id="system",
        capability_key="finance_skonto_assistant",
        status="pending_approval",
        runtime=run_response.json()["runtime"],
        result=run_response.json()["result"],
    )

    response = client.get("/api/v1/agents/neuroassist/ops/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["monthly_run_count"] >= 1
    assert payload["budget_summaries"]
    assert payload["heartbeats"]
    assert payload["roles"]
    assert payload["goals"]


def test_neuroassist_ops_budget_update_and_ticket_listing_endpoints():
    ops = get_agent_ops_service()
    ops.record_run(
        tenant_id="system",
        run_id="run-ops",
        capability_key="operations_exception_assistant",
        role_key="operations_exception_assistant",
        status="pending_approval",
        current_stage_key="approval",
        runtime={"current_stage_key": "approval", "stage_runs": [], "gate_decisions": []},
        result={"exception_summary": "needs review"},
    )
    client = _client()

    budget_response = client.post(
        "/api/v1/agents/neuroassist/ops/budgets/finance_skonto_assistant",
        json={"tenant_id": "system", "monthly_budget_cents": 999},
    )
    tickets_response = client.get("/api/v1/agents/neuroassist/ops/tickets")

    assert budget_response.status_code == 200
    assert budget_response.json()["monthly_budget_cents"] == 999
    assert tickets_response.status_code == 200
    assert tickets_response.json()[0]["capability_key"] == "operations_exception_assistant"


def test_neuroassist_ops_dashboard_intervention_template_and_boundary_endpoints():
    ops = get_agent_ops_service()
    ops.record_run(
        tenant_id="system",
        run_id="run-ops",
        capability_key="operations_exception_assistant",
        role_key="operations_exception_assistant",
        status="pending_approval",
        current_stage_key="approval",
        runtime={"current_stage_key": "approval", "stage_runs": [], "gate_decisions": []},
        result={"exception_summary": "needs review"},
    )
    ticket_id = ops.list_tickets()[0].ticket_id
    client = _client()

    intervention_response = client.post(
        f"/api/v1/agents/neuroassist/ops/tickets/{ticket_id}/interventions",
        json={"tenant_id": "system", "action": "pause", "requested_by": "tester", "note": "hold"},
    )
    dashboard_response = client.get("/api/v1/agents/neuroassist/ops/dashboard")
    mobile_response = client.get("/api/v1/agents/neuroassist/ops/mobile-overview")
    interventions_response = client.get("/api/v1/agents/neuroassist/ops/interventions")
    template_response = client.get("/api/v1/agents/neuroassist/ops/templates/export")
    skill_packs_response = client.get("/api/v1/agents/neuroassist/ops/skill-packs")
    boundary_response = client.get("/api/v1/agents/neuroassist/ops/plugin-boundary-review")

    assert intervention_response.status_code == 200
    assert intervention_response.json()["resulting_status"] == "paused"
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["intervention_count"] == 1
    assert mobile_response.status_code == 200
    assert mobile_response.json()["top_actions"]
    assert interventions_response.status_code == 200
    assert interventions_response.json()[0]["action"] == "pause"
    assert template_response.status_code == 200
    assert template_response.json()["budgets"]
    assert skill_packs_response.status_code == 200
    assert skill_packs_response.json()[0]["skill_pack_key"].endswith(".pack")
    assert boundary_response.status_code == 200
    assert boundary_response.json()["forbidden_patterns"]


def test_neuroassist_control_center_and_config_revision_endpoints():
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
    client = _client()

    budget_response = client.post(
        "/api/v1/agents/neuroassist/ops/budgets/finance_skonto_assistant",
        json={"tenant_id": "system", "monthly_budget_cents": 1100, "changed_by": "ops-admin"},
    )
    heartbeat_response = client.post(
        "/api/v1/agents/neuroassist/ops/heartbeats/finance_skonto_assistant",
        json={"tenant_id": "system", "cadence": "hourly", "stale_after_hours": 2, "changed_by": "ops-admin"},
    )
    profile_response = client.post(
        "/api/v1/agents/neuroassist/ops/profiles/finance_skonto_assistant",
        json={
            "tenant_id": "system",
            "review_sla_hours": 2,
            "stale_after_hours": 2,
            "allowed_actions": ["approve", "pause", "escalate"],
            "changed_by": "ops-admin",
        },
    )
    skill_pack_response = client.post(
        "/api/v1/agents/neuroassist/ops/skill-packs/finance_action_assistant.pack",
        json={
            "tenant_id": "system",
            "skills": ["policy_guardrails", "cost_control"],
            "changed_by": "ops-admin",
        },
    )
    control_center_response = client.get("/api/v1/agents/neuroassist/ops/control-center")
    revisions_response = client.get("/api/v1/agents/neuroassist/ops/config-revisions")

    assert budget_response.status_code == 200
    assert budget_response.json()["version"] == 2
    assert heartbeat_response.status_code == 200
    assert heartbeat_response.json()["cadence"] == "hourly"
    assert profile_response.status_code == 200
    assert profile_response.json()["review_sla_hours"] == 2
    assert skill_pack_response.status_code == 200
    assert skill_pack_response.json()["version"] == 2
    assert control_center_response.status_code == 200
    control_center = control_center_response.json()
    assert control_center["dashboard"]["review_queue_count"] >= 1
    assert control_center["tickets"][0]["requires_review"] is True
    assert control_center["tickets"][0]["owner_role"] == "finance_action_assistant"
    assert control_center["chain_of_command"]
    assert control_center["config_revisions"]
    assert revisions_response.status_code == 200
    assert any(item["config_type"] == "budget" and item["changed_by"] == "ops-admin" for item in revisions_response.json())


def test_neuroassist_persistence_status_endpoint_persists_snapshot():
    ops = get_agent_ops_service()
    ops.record_run(
        tenant_id="system",
        run_id="run-persisted",
        capability_key="finance_skonto_assistant",
        role_key="finance_action_assistant",
        status="pending_approval",
        current_stage_key="analysis",
        runtime={"current_stage_key": "analysis", "stage_runs": [], "gate_decisions": []},
        result={"current_stage_key": "analysis"},
    )
    client = _client()

    response = client.get("/api/v1/agents/neuroassist/ops/persistence")

    assert response.status_code == 200
    body = response.json()
    assert body["persisted"] is True
    assert body["snapshot_counts"]["ticket_count"] >= 1
    assert body["history_count"] >= 1


def test_neuroassist_control_center_planning_and_incidents(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.agents.agent_control_center.settings.AGENT_OPS_PLAN_PATH", str(tmp_path / "planning.json"))
    monkeypatch.setattr("app.integrations.services.superglue_quarantine.settings.SUPERGLUE_QUARANTINE_LOG_PATH", str(tmp_path / "quarantine.jsonl"))

    ops = get_agent_ops_service()
    ops.record_run(
        tenant_id="system",
        run_id="run-incident",
        capability_key="finance_skonto_assistant",
        role_key="finance_action_assistant",
        status="pending_approval",
        current_stage_key="analysis",
        runtime={"current_stage_key": "analysis", "stage_runs": [], "gate_decisions": [{"gate_type": "approval_gate", "status": "deferred"}]},
        result={"current_stage_key": "analysis"},
    )
    append_quarantine_entry(
        tenant_id="system",
        tool_id="system.sg.document.search",
        execution_mode="read",
        outcome="degraded",
        reason="temporary backend outage",
    )
    client = _client()

    upsert_response = client.post(
        "/api/v1/agents/neuroassist/ops/planning/items",
        json={
            "tenant_id": "system",
            "plan_id": "manual:test-slot",
            "title": "Daily Review",
            "kind": "manual_ops",
            "owner": "tenant_operations_lead",
            "scheduled_for": "2026-04-09T09:00:00Z",
            "status": "planned",
            "notes": "control center",
        },
    )
    planning_response = client.get("/api/v1/agents/neuroassist/ops/planning")
    incidents_response = client.get("/api/v1/agents/neuroassist/ops/incidents")

    assert upsert_response.status_code == 200
    assert planning_response.status_code == 200
    planning = planning_response.json()
    assert planning["planned_items"][0]["plan_id"] == "manual:test-slot"
    assert incidents_response.status_code == 200
    incidents = incidents_response.json()
    assert incidents["incident_count"] >= 2
    assert any(item["source"] == "agent_ops" for item in incidents["incidents"])
    assert any(item["source"] == "superglue_quarantine" for item in incidents["incidents"])

    quarantine_incident = next(item for item in incidents["incidents"] if item["source"] == "superglue_quarantine")
    resolve_response = client.post(
        f"/api/v1/agents/neuroassist/ops/incidents/{quarantine_incident['incident_id']}/actions",
        json={"tenant_id": "system", "action": "resolve", "requested_by": "ops-admin"},
    )
    agent_incident = next(item for item in incidents["incidents"] if item["source"] == "agent_ops")
    escalate_response = client.post(
        f"/api/v1/agents/neuroassist/ops/incidents/{agent_incident['incident_id']}/actions",
        json={"tenant_id": "system", "action": "escalate", "requested_by": "ops-admin"},
    )

    assert resolve_response.status_code == 200
    assert escalate_response.status_code == 200
    assert escalate_response.json()["result"]["resulting_status"] == "escalated"
