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


@pytest.mark.unit
def test_get_elster_gate_has_faellig_status() -> None:
    resp = _client.get("/api/v1/external-gates/elster", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["system_id"] == "elster"
    assert body["status"] == "faellig"
    assert body["kategorie"] == "steuer"


@pytest.mark.unit
def test_get_bank_sepa_gate_has_warning_status() -> None:
    resp = _client.get("/api/v1/external-gates/bank_sepa", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["system_id"] == "bank_sepa"
    assert body["status"] == "warning"


@pytest.mark.unit
def test_get_tse_gate_has_ok_status() -> None:
    resp = _client.get("/api/v1/external-gates/tse", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "signatur_zaehler" in body


@pytest.mark.unit
def test_get_dms_gate_has_ok_status() -> None:
    resp = _client.get("/api/v1/external-gates/dms", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "nicht_archivierte_belege" in body


@pytest.mark.unit
def test_get_dsfinvk_gate() -> None:
    resp = _client.get("/api/v1/external-gates/dsfinvk", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["system_id"] == "dsfinvk"
    assert body["kategorie"] == "pos"


@pytest.mark.unit
def test_all_gates_status_summary_keys() -> None:
    resp = _client.get("/api/v1/external-gates/", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    summary = body["status_zusammenfassung"]
    all_statuses = {g["status"] for g in body["gates"]}
    assert set(summary.keys()) == all_statuses
    assert sum(summary.values()) == body["gesamt"]


@pytest.mark.unit
def test_all_gates_have_abgerufen_am_field() -> None:
    resp = _client.get("/api/v1/external-gates/", headers=_HEADERS)
    assert resp.status_code == 200
    for gate in resp.json()["gates"]:
        assert "abgerufen_am" in gate
        assert gate["simulated"] is True
