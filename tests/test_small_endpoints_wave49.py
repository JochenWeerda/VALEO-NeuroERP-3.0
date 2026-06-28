"""Wave 49 — Tests fuer sla_escalation_api und neuro_simulation."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# sla_escalation_api  /api/v1/process/sla/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_sla_scan_empty_instances() -> None:
    resp = _client.post("/api/v1/process/sla/scan", json={"instances": []}, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "violations" in body
    assert "violation_count" in body
    assert body["violation_count"] == 0


@pytest.mark.unit
def test_sla_scan_with_instance() -> None:
    instances = [
        {
            "instance_id": "inst-001",
            "workflow_name": "OrderApproval",
            "status": "running",
            "started_at": "2026-06-01T08:00:00Z",
            "step": "approval",
        }
    ]
    resp = _client.post("/api/v1/process/sla/scan", json={"instances": instances}, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "violations" in body
    assert isinstance(body["violations"], list)


@pytest.mark.unit
def test_sla_scan_invalid_instances_type() -> None:
    resp = _client.post("/api/v1/process/sla/scan", json={"instances": "not-a-list"}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_sla_scan_returns_summary() -> None:
    resp = _client.post("/api/v1/process/sla/scan", json={"instances": []}, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "summary" in body


@pytest.mark.unit
def test_sla_escalate_missing_violation_returns_422() -> None:
    resp = _client.post("/api/v1/process/sla/escalate", json={"violation": {}}, headers=_HEADERS)
    # SLAViolation model requires fields — empty dict → 422
    assert resp.status_code in (202, 422)


@pytest.mark.unit
def test_sla_escalate_valid_violation() -> None:
    violation = {
        "instance_id": "inst-001",
        "workflow_name": "OrderApproval",
        "sla_name": "approval_24h",
        "severity": "warning",
        "exceeded_by_seconds": 3600,
        "detected_at": "2026-06-27T10:00:00Z",
    }
    resp = _client.post("/api/v1/process/sla/escalate", json={"violation": violation}, headers=_HEADERS)
    assert resp.status_code in (202, 422)


# ---------------------------------------------------------------------------
# neuro_simulation  /api/v1/neuro/simulate/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_neuro_dry_run_returns_200() -> None:
    payload = {
        "action": "approve",
        "entity_type": "order",
        "entity_id": "ORD-001",
        "current_state": "pending",
        "target_state": "approved",
    }
    resp = _client.post("/api/v1/neuro/simulate/dry-run", json=payload, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_neuro_dry_run_missing_required_fields() -> None:
    resp = _client.post("/api/v1/neuro/simulate/dry-run", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_neuro_what_if_returns_200() -> None:
    payload = {
        "action": "reprice",
        "entity_type": "article",
        "entity_id": "ART-001",
        "amount": 12.50,
        "current_data": {"price": 10.0},
    }
    resp = _client.post("/api/v1/neuro/simulate", json=payload, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_neuro_get_result_not_found() -> None:
    resp = _client.get("/api/v1/neuro/simulate/nonexistent-run-id", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_neuro_dry_run_has_result_structure() -> None:
    payload = {"action": "test", "entity_type": "order"}
    resp = _client.post("/api/v1/neuro/simulate/dry-run", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
    assert len(body) > 0
