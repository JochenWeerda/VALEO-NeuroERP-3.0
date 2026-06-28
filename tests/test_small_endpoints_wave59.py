"""Wave 59 — Tests fuer agent_context_api und agrar_wetter."""

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
# agent_context_api  /api/v1/agent-context/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_agent_context_delete_nonexistent_returns_404() -> None:
    resp = _client.delete("/api/v1/agent-context/nonexistent-ctx-xyz", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_agent_context_dispatch_nonexistent_returns_404() -> None:
    payload = {
        "command_name": "CreateOrder",
        "resource_tenant_id": "T001",
        "resource_type": "agent_command",
        "issuer_role": "agent",
    }
    resp = _client.post("/api/v1/agent-context/nonexistent-ctx-xyz/dispatch", json=payload, headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_agent_context_knowledge_pack_nonexistent_returns_404() -> None:
    payload = {"rolle": "verkauf", "kanal": "CHAT", "query": "Getreide"}
    resp = _client.post(
        "/api/v1/agent-context/nonexistent-ctx-xyz/knowledge-pack",
        json=payload,
        headers=_HEADERS,
    )
    assert resp.status_code == 404


@pytest.mark.unit
def test_agent_context_create_missing_fields() -> None:
    resp = _client.post("/api/v1/agent-context", json={}, headers=_HEADERS)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# agrar_wetter  /api/v1/agrar/wetter/*
# ---------------------------------------------------------------------------

_FAKE_WEATHER = {
    "weather": {"timestamp": "2026-06-27T10:00:00+00:00", "temperature": 22.5, "condition": "dry"},
    "sources": [{"id": 1, "station_name": "Muster-Station", "dwd_station_id": "01234"}],
}

_FAKE_FORECAST = {
    "hourly": {
        "time": ["2026-06-27T10:00", "2026-06-27T11:00"],
        "temperature_2m": [22.0, 23.5],
    },
    "hourly_units": {"temperature_2m": "°C"},
}


@pytest.mark.unit
def test_agrar_wetter_aktuell_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.agrar_wetter as ep_mod

    async def _fake_cached_get(url: str, params: dict, cache_ttl: int = 300) -> dict:
        return _FAKE_WEATHER

    monkeypatch.setattr(ep_mod, "_cached_get", _fake_cached_get)
    resp = _client.get(
        "/api/v1/agrar/wetter/aktuell",
        params={"lat": 51.5, "lon": 10.0},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_agrar_wetter_prognose_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.agrar_wetter as ep_mod

    async def _fake_cached_get(url: str, params: dict, cache_ttl: int = 300) -> dict:
        return _FAKE_FORECAST

    monkeypatch.setattr(ep_mod, "_cached_get", _fake_cached_get)
    resp = _client.get(
        "/api/v1/agrar/wetter/prognose",
        params={"lat": 51.5, "lon": 10.0},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_agrar_wetter_stunden_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.agrar_wetter as ep_mod

    async def _fake_cached_get(url: str, params: dict, cache_ttl: int = 300) -> dict:
        return {
            "weather": [{"timestamp": "2026-06-27T10:00:00+00:00", "temperature": 22.5}],
            "sources": [{"id": 1}],
        }

    monkeypatch.setattr(ep_mod, "_cached_get", _fake_cached_get)
    resp = _client.get(
        "/api/v1/agrar/wetter/stunden",
        params={"lat": 51.5, "lon": 10.0},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_agrar_wetter_warnungen_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.agrar_wetter as ep_mod

    async def _fake_cached_get(url: str, params: dict, cache_ttl: int = 300) -> dict:
        return {"alerts": []}

    monkeypatch.setattr(ep_mod, "_cached_get", _fake_cached_get)
    resp = _client.get(
        "/api/v1/agrar/wetter/warnungen",
        params={"lat": 51.5, "lon": 10.0},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_agrar_wetter_boden_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.agrar_wetter as ep_mod

    async def _fake_cached_get(url: str, params: dict, cache_ttl: int = 300) -> dict:
        return _FAKE_FORECAST

    monkeypatch.setattr(ep_mod, "_cached_get", _fake_cached_get)
    resp = _client.get(
        "/api/v1/agrar/wetter/boden",
        params={"lat": 51.5, "lon": 10.0},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
