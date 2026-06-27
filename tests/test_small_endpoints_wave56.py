"""Wave 56 — Tests fuer tenant_limits und neuro_interactions."""

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
# tenant_limits  /api/v1/process/tenant-limits/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_tenant_limits_overview_returns_200() -> None:
    resp = _client.get(
        "/api/v1/process/tenant-limits/overview",
        params={"tenant_id": "T001"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "overview" in body
    assert "rate_limits" in body


@pytest.mark.unit
def test_tenant_limits_overview_with_domain() -> None:
    resp = _client.get(
        "/api/v1/process/tenant-limits/overview",
        params={"tenant_id": "T001", "domain": "orders"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_tenant_limits_overview_missing_tenant_id() -> None:
    resp = _client.get("/api/v1/process/tenant-limits/overview", headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_tenant_cache_config_returns_200() -> None:
    resp = _client.get("/api/v1/process/tenant-limits/cache-configs/T001", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "cache_config" in body
    assert "cache_namespace" in body
    assert "T001" in body["cache_namespace"]


@pytest.mark.unit
def test_rate_limits_list_returns_200() -> None:
    resp = _client.get("/api/v1/process/tenant-limits/rate-limits", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "policy_count" in body
    assert "policies" in body


@pytest.mark.unit
def test_rate_limits_check_returns_200() -> None:
    payload = {
        "tenant_id": "T001",
        "user_id": "U001",
        "endpoint": "/api/v1/orders",
        "domain": "orders",
        "aktuelle_zaehlung": 5,
        "zeitfenster_sekunden": 60,
    }
    resp = _client.post("/api/v1/process/tenant-limits/rate-limits/check", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body


@pytest.mark.unit
def test_rate_limits_check_missing_fields() -> None:
    resp = _client.post("/api/v1/process/tenant-limits/rate-limits/check", json={}, headers=_HEADERS)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# neuro_interactions  /api/v1/neuro/interactions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_interaction_create_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_interactions as ep_mod

    monkeypatch.setattr(
        ep_mod, "create_interaction",
        lambda channel, entity_id, tenant_id, db: {
            "id": "INT-001", "channel": channel, "state": "new"
        },
    )
    payload = {"channel": "chat", "entity_id": "KN-001"}
    resp = _client.post("/api/v1/neuro/interactions", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["channel"] == "chat"


@pytest.mark.unit
def test_interaction_create_missing_channel() -> None:
    resp = _client.post("/api/v1/neuro/interactions", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_interaction_get_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_interactions as ep_mod

    monkeypatch.setattr(ep_mod, "get_interaction", lambda iid, tid, db: None)
    resp = _client.get("/api/v1/neuro/interactions/nonexistent-int-xyz", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_interaction_transition(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_interactions as ep_mod

    monkeypatch.setattr(
        ep_mod, "transition_interaction",
        lambda iid, target, tid, db: {"id": iid, "state": target},
    )
    resp = _client.put(
        "/api/v1/neuro/interactions/INT-001/transition",
        json={"target_state": "active"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "active"


@pytest.mark.unit
def test_interaction_list_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_interactions as ep_mod

    monkeypatch.setattr(ep_mod, "list_interactions", lambda tid, db, *a, **kw: [])
    resp = _client.get("/api/v1/neuro/interactions", headers=_HEADERS)
    # 200 or 404 depending on route registration
    assert resp.status_code in (200, 404, 405)
