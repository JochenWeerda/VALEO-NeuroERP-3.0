from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api.v1.endpoints import agents


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(agents.router, prefix="/api/v1/agents")
    return TestClient(app)


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
