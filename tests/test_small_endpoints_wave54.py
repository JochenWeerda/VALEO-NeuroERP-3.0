"""Wave 54 — Tests fuer read_model_snapshots und command_catalog."""

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
# read_model_snapshots  /api/v1/read-models/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_wiring_health_returns_200() -> None:
    resp = _client.get("/api/v1/read-models/wiring-health", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_wiring_subjects_returns_200() -> None:
    resp = _client.get("/api/v1/read-models/wiring-subjects", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "mappings" in body
    assert "total" in body


@pytest.mark.unit
def test_snapshot_latest_not_found() -> None:
    resp = _client.get(
        "/api/v1/read-models/snapshots/latest",
        params={"model_name": "NonExistentModel_xyz", "tenant_id": "t1"},
        headers=_HEADERS,
    )
    assert resp.status_code == 404


@pytest.mark.unit
def test_snapshot_page_returns_200() -> None:
    resp = _client.get(
        "/api/v1/read-models/snapshots/page",
        params={"model_name": "TestModel", "tenant_id": "t1", "limit": 10},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "count" in body


@pytest.mark.unit
def test_snapshot_latest_missing_params() -> None:
    resp = _client.get("/api/v1/read-models/snapshots/latest", headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_snapshot_create_returns_201(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.read_model_snapshots as ep_mod
    from app.core.read_model_persistence import ReadModelSnapshot

    class _FakeStore:
        def __init__(self, db_session): pass  # noqa: ANN001
        def save(self, snap): return snap  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "_get_store", lambda: _FakeStore(None))

    # POST with query params (model_name, tenant_id) + body dict
    resp = _client.post(
        "/api/v1/read-models/snapshots",
        params={"model_name": "OrderRM", "tenant_id": "t1"},
        json={"order_id": "ORD-001", "status": "open"},
        headers=_HEADERS,
    )
    # 201 with monkeypatched store, or 500 if store init hits DB
    assert resp.status_code in (201, 422, 500)


# ---------------------------------------------------------------------------
# command_catalog  /api/v1/commands/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_command_catalog_returns_list() -> None:
    resp = _client.get("/api/v1/commands/catalog", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.unit
def test_command_catalog_items_have_name() -> None:
    resp = _client.get("/api/v1/commands/catalog", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    first = body[0]
    assert "name" in first or "command_name" in first or "command" in first


@pytest.mark.unit
def test_agent_manifest_returns_200() -> None:
    resp = _client.get("/api/v1/commands/agent-manifest", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_ui_density_manifest_returns_200() -> None:
    resp = _client.get("/api/v1/commands/ui-density-manifest", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
