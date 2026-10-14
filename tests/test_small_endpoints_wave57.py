"""Wave 57 — Tests fuer portal_intelligence und wf_trigger."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


# portal_intelligence: seit 14.10.2026 persistent, Tests in tests/test_portal_lohndienst_persistenz.py.


# ---------------------------------------------------------------------------
# wf_trigger  /api/v1/wf-trigger/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_wf_trigger_map_returns_200() -> None:
    resp = _client.get("/api/v1/wf-trigger/map", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "trigger_map" in body


@pytest.mark.unit
def test_wf_trigger_fire_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.wf_trigger as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def fire(self, entity_type, entity_id, new_status, context):  # noqa: ANN001
            return []

    monkeypatch.setattr(ep_mod, "WfTriggerService", _FakeSvc)
    payload = {
        "entity_type": "order",
        "entity_id": "ORD-001",
        "new_status": "confirmed",
    }
    resp = _client.post("/api/v1/wf-trigger", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["entity_type"] == "order"
    assert body["new_status"] == "confirmed"


@pytest.mark.unit
def test_wf_trigger_fire_missing_fields() -> None:
    resp = _client.post("/api/v1/wf-trigger", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_wf_trigger_log_returns_200() -> None:
    resp = _client.get("/api/v1/wf-trigger/log", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body or "log" in body or isinstance(body, dict)
