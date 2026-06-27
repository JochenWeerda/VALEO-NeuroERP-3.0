"""Wave 52 — Tests fuer geo, bedarfsdeckung, crm_auto_capture, pricing_governance."""

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
# geo  /api/v1/geo/map-points
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_geo_map_points_returns_geojson(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.geo as ep_mod

    monkeypatch.setattr(
        ep_mod, "get_map_points",
        lambda db, only_geocoded=True: {"type": "FeatureCollection", "features": []},
    )
    resp = _client.get("/api/v1/geo/map-points", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["type"] == "FeatureCollection"
    assert isinstance(body["features"], list)


@pytest.mark.unit
def test_geo_map_points_all_points(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.geo as ep_mod

    received = {}

    def _fake(db, only_geocoded=True):  # noqa: ANN001
        received["only_geocoded"] = only_geocoded
        return {"type": "FeatureCollection", "features": []}

    monkeypatch.setattr(ep_mod, "get_map_points", _fake)
    _client.get("/api/v1/geo/map-points", params={"only_geocoded": "false"}, headers=_HEADERS)
    assert received.get("only_geocoded") is False


# ---------------------------------------------------------------------------
# bedarfsdeckung  /api/v1/crm/bedarfsdeckung/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_bedarfsdeckung_pipeline_returns_list(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.bedarfsdeckung as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def pipeline(self, limit): return [{"kunden_nr": "KN-001", "chance": 0.8}]  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "BedarfsdeckungService", _FakeSvc)
    resp = _client.get("/api/v1/crm/bedarfsdeckung/pipeline", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body[0]["kunden_nr"] == "KN-001"


@pytest.mark.unit
def test_bedarfsdeckung_pipeline_limit_validation() -> None:
    resp = _client.get("/api/v1/crm/bedarfsdeckung/pipeline", params={"limit": 0}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_bedarfsdeckung_cockpit_found(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.bedarfsdeckung as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def cockpit(self, kunden_nr): return {"kunden_nr": kunden_nr, "gesamt_chance": 0.7}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "BedarfsdeckungService", _FakeSvc)
    resp = _client.get("/api/v1/crm/bedarfsdeckung/KN-001", headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["kunden_nr"] == "KN-001"


@pytest.mark.unit
def test_bedarfsdeckung_cockpit_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.bedarfsdeckung as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def cockpit(self, kunden_nr): return None  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "BedarfsdeckungService", _FakeSvc)
    resp = _client.get("/api/v1/crm/bedarfsdeckung/UNKNOWN", headers=_HEADERS)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# crm_auto_capture  /api/v1/crm/kim/auto-capture
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_auto_capture_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_auto_capture as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def capture(self, **kw): return {"status": "captured", "kontakt_id": "KT-001"}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmAutoCaptureService", _FakeSvc)
    payload = {
        "channel": "telefon",
        "direction": "incoming",
        "peer": "+49123456789",
        "content": "Kunde fragte nach Getreidepreisen",
    }
    resp = _client.post("/api/v1/crm/kim/auto-capture", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "captured"


@pytest.mark.unit
def test_auto_capture_missing_channel() -> None:
    resp = _client.post("/api/v1/crm/kim/auto-capture", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_auto_capture_all_channels(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_auto_capture as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def capture(self, **kw): return {"status": "captured", "channel": kw.get("channel")}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmAutoCaptureService", _FakeSvc)
    for channel in ("telefon", "email", "whatsapp", "persoenlich", "brief", "fax"):
        payload = {"channel": channel, "content": f"Test via {channel}"}
        resp = _client.post("/api/v1/crm/kim/auto-capture", json=payload, headers=_HEADERS)
        assert resp.status_code == 200, f"channel={channel} failed: {resp.status_code}"


# ---------------------------------------------------------------------------
# pricing_governance  /api/v1/pricing/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_pricing_sources_returns_list(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.pricing_governance as ep_mod
    from app.core.pricing_governance import build_default_pricing_sources

    monkeypatch.setattr(ep_mod, "_get_sources", lambda tid, db: build_default_pricing_sources())
    resp = _client.get("/api/v1/pricing/sources", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


@pytest.mark.unit
def test_pricing_governance_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.pricing_governance as ep_mod
    from app.core.pricing_governance import build_default_pricing_sources

    monkeypatch.setattr(ep_mod, "_get_sources", lambda tid, db: build_default_pricing_sources())
    resp = _client.get("/api/v1/pricing/governance", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "sources" in body
    assert "tenant_id" in body
