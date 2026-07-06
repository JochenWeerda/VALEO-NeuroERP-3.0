"""Tests fuer PORTAL-INNENDIENST-001 — Innendienst-Schlaege, Massnahmen, Potential."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import portal_innendienst as innendienst_endpoint
from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_NO_TENANT = {"Authorization": "Bearer dev-token"}

_client = TestClient(app, raise_server_exceptions=False)


class _Row:
    def __init__(self, **values):
        self._mapping = values


class _Result:
    def __init__(self, rows=None):
        self._rows = rows or []

    def fetchall(self):
        return self._rows


class _PortalDb:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.calls: list[tuple[str, dict]] = []

    def execute(self, statement, params=None):
        if self.fail:
            raise RuntimeError("simulated db failure")
        sql = str(statement)
        params = params or {}
        self.calls.append((sql, params))
        if "feldbuch_schlaege" in sql and "GROUP BY" not in sql:
            return _Result([
                _Row(
                    id="schlag-1",
                    name="Nordfeld",
                    flik="DENI123",
                    flaeche=12.5,
                    kultur="Winterweizen",
                    vorkultur="Raps",
                    gemeinde="Aurich",
                    gemarkung="Mitte",
                    bodenart="Lehm",
                    ackerzahl=58,
                    status="aktiv",
                    customer_id=params["kunden_nr"],
                )
            ])
        if "feldbuch_massnahmen" in sql:
            return _Result([
                _Row(
                    id="massnahme-1",
                    datum="2026-04-03",
                    typ=params.get("typ") or "Spritzung",
                    schlag_id=params.get("schlag_id") or "schlag-1",
                    schlag_name="Nordfeld",
                    mittel="Muster PSM",
                    menge=2.4,
                    einheit="l/ha",
                    fahrer="MA-1",
                    bemerkung="ok",
                    customer_id=params["kunden_nr"],
                )
            ])
        if "feldbuch_schlaege" in sql and "GROUP BY" in sql:
            return _Result([
                _Row(kunden_nr="K-001", kulturen=["Winterweizen", "Raps"], gesamt_ha=32.5),
                _Row(kunden_nr="K-002", kulturen=["Gruenland"], gesamt_ha=14.0),
            ])
        return _Result([])


@pytest.fixture
def portal_db_override():
    db = _PortalDb()
    app.dependency_overrides[innendienst_endpoint.get_db] = lambda: db
    yield db
    app.dependency_overrides.pop(innendienst_endpoint.get_db, None)


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
def test_kunden_schlaege_returns_db_rows(portal_db_override) -> None:
    resp = _client.get("/api/v1/innendienst/kunden/K-001/schlaege", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["schlaege"][0]["name"] == "Nordfeld"
    assert body["schlaege"][0]["customer_id"] == "K-001"


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
def test_kunden_massnahmen_combined_filters_reach_query_params(portal_db_override) -> None:
    resp = _client.get(
        "/api/v1/innendienst/kunden/K-001/massnahmen?schlag_id=schlag-1&massnahme_typ=Spritzung",
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["massnahmen"][0]["typ"] == "Spritzung"
    _sql, params = portal_db_override.calls[-1]
    assert params["schlag_id"] == "schlag-1"
    assert params["typ"] == "Spritzung"


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
def test_potential_analyse_uses_culture_rows_for_gap_customers(portal_db_override) -> None:
    resp = _client.get("/api/v1/innendienst/potential", headers=_HEADERS)
    assert resp.status_code == 200
    gaps = {gap["gap_typ"]: gap for gap in resp.json()["gap_analyse"]}
    assert gaps["ankauf_kein_kontrakt"]["kunden"] == ["K-001"]
    assert gaps["lohnspritz_kein_auftrag"]["kunden"] == ["K-001", "K-002"]


@pytest.mark.unit
def test_db_failures_return_empty_fallbacks() -> None:
    failing_db = _PortalDb(fail=True)
    app.dependency_overrides[innendienst_endpoint.get_db] = lambda: failing_db
    try:
        schlaege = _client.get("/api/v1/innendienst/kunden/K-001/schlaege", headers=_HEADERS)
        massnahmen = _client.get("/api/v1/innendienst/kunden/K-001/massnahmen", headers=_HEADERS)
        potential = _client.get("/api/v1/innendienst/potential", headers=_HEADERS)
    finally:
        app.dependency_overrides.pop(innendienst_endpoint.get_db, None)
    assert schlaege.status_code == 200
    assert schlaege.json()["schlaege"] == []
    assert massnahmen.status_code == 200
    assert massnahmen.json()["massnahmen"] == []
    assert potential.status_code == 200
    assert potential.json()["schlag_kunden_count"] == 0


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
