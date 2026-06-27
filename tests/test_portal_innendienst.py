"""Tests fuer PORTAL-INNENDIENST-001 — Innendienst-Schlaege, Massnahmen, Potential."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_NO_TENANT = {"Authorization": "Bearer dev-token"}

_client = TestClient(app, raise_server_exceptions=False)


@pytest.mark.unit
def test_kunden_schlaege_returns_structure() -> None:
    resp = _client.get("/api/v1/innendienst/kunden/K-001/schlaege", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["kunden_nr"] == "K-001"
    assert "schlaege" in body
    assert isinstance(body["count"], int)
    assert "hinweis" in body


@pytest.mark.unit
def test_kunden_schlaege_empty_for_unknown_customer() -> None:
    resp = _client.get("/api/v1/innendienst/kunden/UNKNOWN-9999/schlaege", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["kunden_nr"] == "UNKNOWN-9999"
    assert body["schlaege"] == []
    assert body["count"] == 0


@pytest.mark.unit
def test_kunden_massnahmen_returns_structure() -> None:
    resp = _client.get("/api/v1/innendienst/kunden/K-001/massnahmen", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["kunden_nr"] == "K-001"
    assert "massnahmen" in body
    assert isinstance(body["count"], int)


@pytest.mark.unit
def test_kunden_massnahmen_with_schlag_filter() -> None:
    resp = _client.get(
        "/api/v1/innendienst/kunden/K-001/massnahmen?schlag_id=schlag-1",
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["kunden_nr"] == "K-001"


@pytest.mark.unit
def test_kunden_massnahmen_with_typ_filter() -> None:
    resp = _client.get(
        "/api/v1/innendienst/kunden/K-001/massnahmen?massnahme_typ=Spritzung",
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["massnahmen"], list)


@pytest.mark.unit
def test_potential_analyse_returns_gap_types() -> None:
    resp = _client.get("/api/v1/innendienst/potential", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "gap_analyse" in body
    assert isinstance(body["gap_analyse"], list)
    assert len(body["gap_analyse"]) >= 3
    assert "schlag_kunden_count" in body
    assert "hinweis" in body


@pytest.mark.unit
def test_potential_analyse_gap_types_have_required_keys() -> None:
    resp = _client.get("/api/v1/innendienst/potential", headers=_HEADERS)
    assert resp.status_code == 200
    for gap in resp.json()["gap_analyse"]:
        assert "gap_typ" in gap
        assert "titel" in gap
        assert "kunden" in gap
        assert "potential_eur_je_kunde" in gap


@pytest.mark.unit
def test_missing_tenant_header_returns_400() -> None:
    resp = _client.get("/api/v1/innendienst/kunden/K-001/schlaege", headers=_NO_TENANT)
    assert resp.status_code in {400, 422}


@pytest.mark.unit
def test_missing_tenant_header_massnahmen_returns_400() -> None:
    resp = _client.get("/api/v1/innendienst/kunden/K-001/massnahmen", headers=_NO_TENANT)
    assert resp.status_code in {400, 422}


@pytest.mark.unit
def test_missing_tenant_header_potential_returns_400() -> None:
    resp = _client.get("/api/v1/innendienst/potential", headers=_NO_TENANT)
    assert resp.status_code in {400, 422}
