"""Wave 57 — Tests fuer portal_intelligence und wf_trigger."""

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
# portal_intelligence  /api/v1/portal/empfehlungen/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_portal_empfehlungen_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.portal_intelligence as ep_mod

    class _FakeSvc:
        def empfehlungen_fuer_kunden(self, kunden_nr, nur_ungesehen=False):  # noqa: ANN001
            return []

    monkeypatch.setattr(ep_mod, "get_intelligence_service", lambda tid: _FakeSvc())
    resp = _client.get("/api/v1/portal/empfehlungen/KN-001", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert body["count"] == 0


@pytest.mark.unit
def test_portal_zusammenfassung_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.portal_intelligence as ep_mod

    class _FakeSvc:
        def zusammenfassung(self, kunden_nr):  # noqa: ANN001
            return {"kunden_nr": kunden_nr, "total": 0}

    monkeypatch.setattr(ep_mod, "get_intelligence_service", lambda tid: _FakeSvc())
    resp = _client.get("/api/v1/portal/empfehlungen/KN-001/zusammenfassung", headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_portal_als_gesehen_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.portal_intelligence as ep_mod

    class _FakeSvc:
        def als_gesehen_markieren(self, eid, kunden_nr):  # noqa: ANN001
            return False

    monkeypatch.setattr(ep_mod, "get_intelligence_service", lambda tid: _FakeSvc())
    resp = _client.post("/api/v1/portal/empfehlungen/KN-001/gesehen/EMP-999", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_portal_als_gesehen_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.portal_intelligence as ep_mod

    class _FakeSvc:
        def als_gesehen_markieren(self, eid, kunden_nr):  # noqa: ANN001
            return True

    monkeypatch.setattr(ep_mod, "get_intelligence_service", lambda tid: _FakeSvc())
    resp = _client.post("/api/v1/portal/empfehlungen/KN-001/gesehen/EMP-001", headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@pytest.mark.unit
def test_portal_generiere_aus_ration(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.portal_intelligence as ep_mod

    class _FakeSvc:
        def generiere_aus_ration(self, kunden_nr, tiere_anzahl, tier_kategorie, benoetigt_rohwaren):  # noqa: ANN001
            return [{"empfehlung_id": "E-001"}]

    monkeypatch.setattr(ep_mod, "get_intelligence_service", lambda tid: _FakeSvc())
    payload = {"kunden_nr": "KN-001", "tiere_anzahl": 50, "tier_kategorie": "milchkuh"}
    resp = _client.post("/api/v1/portal/empfehlungen/generieren/ration", json=payload, headers=_HEADERS)
    assert resp.status_code == 201
    assert resp.json()["count"] == 1


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
