"""Tests fuer Policy Manager API (RBAC-Policies CRUD + Simulator)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)

_SAMPLE_RULE = {
    "id": "test-policy-wave46",
    "when": {"kpiId": "cpu.usage", "severity": ["crit"]},
    "action": "sales.notify",
    "params": {"channel": "slack"},
    "autoExecute": False,
    "autoSuggest": True,
}


@pytest.mark.unit
def test_list_policies_returns_200() -> None:
    resp = _client.get("/api/v1/mcp/policy/list", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body or "success" in body


@pytest.mark.unit
def test_test_policy_simulator() -> None:
    test_payload = {
        "alert": {
            "id": "alert-sim-1",
            "kpiId": "cpu.usage",
            "title": "CPU hoch",
            "message": "CPU > 95%",
            "severity": "crit",
        },
        "roles": ["admin", "ops"],
    }
    resp = _client.post("/api/v1/mcp/policy/test", json=test_payload, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "ok" in body
    assert "decision" in body
    assert "explainability" in body


@pytest.mark.unit
def test_export_policies_returns_json() -> None:
    resp = _client.get("/api/v1/mcp/policy/export", headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_resolve_tenant_policy_override_helper() -> None:
    from app.api.v1.endpoints.policies import resolve_tenant_policy_override
    result = resolve_tenant_policy_override(db=None, tenant_id="t1", rule_id="rule-42", base_params={"key": "val"})
    assert result.rule_id == "rule-42"
    assert result.effective_params == {"key": "val"}
    assert result.effective_enabled is True


@pytest.mark.unit
def test_resolve_tenant_policy_override_no_rule_id() -> None:
    from app.api.v1.endpoints.policies import resolve_tenant_policy_override
    result = resolve_tenant_policy_override(db=None, tenant_id="t1", rule_id=None)
    assert result.rule_id == "policy.default"
    assert result.effective_params == {}
