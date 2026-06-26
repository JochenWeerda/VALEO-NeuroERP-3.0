"""Tests fuer externe Gate-Dashboard API (ADMIN-EXTERNAL-GATES-001)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


@pytest.mark.unit
def test_get_all_external_gates_returns_overview() -> None:
    resp = _client.get("/api/v1/external-gates/", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["gesamt"] >= 5
    assert "gates" in body
    assert len(body["gates"]) == body["gesamt"]
    assert "status_zusammenfassung" in body
    assert body["tenant_id"]


@pytest.mark.unit
def test_get_single_external_gate_ok() -> None:
    resp = _client.get("/api/v1/external-gates/datev", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["system_id"] == "datev"
    assert body["label"]
    assert body["status"] in {"ok", "warning", "faellig", "fehler", "unbekannt"}
    assert body["simulated"] is True


@pytest.mark.unit
def test_get_unknown_external_gate_returns_404() -> None:
    resp = _client.get("/api/v1/external-gates/unknown-system", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_gate_status_helper_covers_all_meta_systems() -> None:
    from app.api.v1.endpoints.external_gates import _SYSTEM_META, _gate_status

    for sid in _SYSTEM_META:
        status = _gate_status(sid, "tenant-test")
        assert status["system_id"] == sid
        assert status["label"]
        assert status["kategorie"]
        assert status["abgerufen_am"]
