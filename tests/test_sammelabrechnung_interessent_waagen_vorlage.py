"""Unit tests for Rohware-Sammelabrechnung, Interessenten, eBilanz/ELSTER, Waagenvorlagen."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# ---------------------------------------------------------------------------
# Helpers — create minimal test apps per router to avoid full app startup
# ---------------------------------------------------------------------------

def _mock_db():
    """Return a MagicMock that mimics a SQLAlchemy Session."""
    db = MagicMock()
    # execute().mappings().all() → []
    exec_mock = MagicMock()
    exec_mock.mappings.return_value.all.return_value = []
    exec_mock.mappings.return_value.first.return_value = None
    exec_mock.first.return_value = None
    db.execute.return_value = exec_mock
    db.commit.return_value = None
    db.rollback.return_value = None
    return db


TENANT_ID = "00000000-0000-0000-0000-000000000001"


def _app_sammelabrechnung():
    from app.api.v1.endpoints.rohware_sammelabrechnung import router
    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    app = FastAPI()
    app.include_router(router)
    db = _mock_db()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: TENANT_ID
    return app, db


def _app_customers():
    from app.api.v1.endpoints.customers import router
    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    app = FastAPI()
    app.include_router(router, prefix="/customers")
    db = _mock_db()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: TENANT_ID
    return app, db


def _app_ebilanz():
    from app.api.v1.endpoints.ebilanz_elster import router
    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    app = FastAPI()
    app.include_router(router)
    db = _mock_db()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: TENANT_ID
    return app, db


def _app_waagen():
    from app.api.v1.endpoints.waagen_vorlagen import router
    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    app = FastAPI()
    app.include_router(router)
    db = _mock_db()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: TENANT_ID
    return app, db


# ===========================================================================
# Sammelabrechnung Tests
# ===========================================================================

@pytest.mark.unit
def test_sammelabrechnung_create_returns_id():
    app, _ = _app_sammelabrechnung()
    client = TestClient(app)
    resp = client.post("/agrar/sammelabrechnung", json={
        "bezeichnung": "Abrechnung Aug 2026",
        "abrechnungsperiode": "2026-08",
        "harvest_acceptance_ids": ["id-001", "id-002"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert len(data["id"]) > 0
    assert data["status"] == "ENTWURF"


@pytest.mark.unit
def test_sammelabrechnung_requires_min_2_ids():
    app, _ = _app_sammelabrechnung()
    client = TestClient(app)
    resp = client.post("/agrar/sammelabrechnung", json={
        "bezeichnung": "Test",
        "abrechnungsperiode": "2026-08",
        "harvest_acceptance_ids": ["only-one"],
    })
    assert resp.status_code == 422


@pytest.mark.unit
def test_sammelabrechnung_berechnen_graceful_missing_table():
    """When DB tables are missing, berechnen must still return status=BERECHNET with summe=0."""
    app, db = _app_sammelabrechnung()
    # Make all DB calls raise (simulates missing table)
    db.execute.side_effect = Exception("relation does not exist")

    client = TestClient(app)
    resp = client.post("/agrar/sammelabrechnung/some-id/berechnen")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "BERECHNET"
    assert data["summe_menge_kg"] == 0.0
    assert data["summe_betrag_eur"] == 0.0


@pytest.mark.unit
def test_sammelabrechnung_buchen_sets_gebucht():
    app, _ = _app_sammelabrechnung()
    client = TestClient(app)
    resp = client.post("/agrar/sammelabrechnung/some-id/buchen")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gebucht"] is True
    assert "buchungsnr" in data


@pytest.mark.unit
def test_sammelabrechnung_delete_entwurf_ok():
    app, db = _app_sammelabrechnung()

    # Mock: first execute for SELECT status → return a row with status=ENTWURF
    select_mock = MagicMock()
    select_mock.mappings.return_value.first.return_value = {"status": "ENTWURF"}
    delete_mock = MagicMock()

    call_count = [0]

    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return select_mock
        return delete_mock

    db.execute.side_effect = side_effect

    client = TestClient(app)
    resp = client.delete("/agrar/sammelabrechnung/some-id")
    assert resp.status_code == 204


# ===========================================================================
# Interessenten Tests
# ===========================================================================

@pytest.mark.unit
def test_interessent_create_generates_nr():
    app, db = _app_customers()

    # COUNT query returns 0
    count_mock = MagicMock()
    count_mock.first.return_value = (0,)
    insert_mock = MagicMock()

    call_count = [0]

    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return count_mock
        return insert_mock

    db.execute.side_effect = side_effect

    client = TestClient(app)
    resp = client.post("/customers/interessenten", json={
        "name": "Mustermann GmbH",
        "email": "info@mustermann.de",
        "herkunft": "WEBSITE",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["interessenten_nr"].startswith("INT-")


@pytest.mark.unit
def test_interessent_konvertieren_returns_kunden_nr():
    app, db = _app_customers()

    interessent_row = {
        "id": "int-001",
        "interessenten_nr": "INT-2026-00001",
        "name": "Mustermann GmbH",
        "email": "info@mustermann.de",
        "telefon": None,
        "status": "INTERESSENT",
    }
    load_mock = MagicMock()
    load_mock.mappings.return_value.first.return_value = interessent_row
    update_mock = MagicMock()

    call_count = [0]

    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return load_mock
        return update_mock

    db.execute.side_effect = side_effect

    client = TestClient(app)
    resp = client.post("/customers/interessenten/int-001/konvertieren")
    assert resp.status_code == 200
    data = resp.json()
    assert "kunden_nr" in data
    assert data["kunden_nr"].startswith("KD-")
    assert data["status"] == "KUNDE"


# ===========================================================================
# eBilanz / ELSTER Tests
# ===========================================================================

@pytest.mark.unit
def test_ebilanz_export_taxonomie_67():
    app, _ = _app_ebilanz()
    client = TestClient(app)
    resp = client.post("/ebilanz/export/erstellen", json={
        "wirtschaftsjahr": 2025,
        "bilanzart": "HGB",
        "berichtsperiode_von": "2025-01-01",
        "berichtsperiode_bis": "2025-12-31",
        "steuernummer": "123/456/78901",
        "finanzamt_nr": "2845",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["taxonomie_version"] == "6.7"
    assert "export_id" in data
    assert data["status"] == "ERSTELLT"


@pytest.mark.unit
def test_ebilanz_validieren_returns_hinweise():
    app, _ = _app_ebilanz()
    client = TestClient(app)
    resp = client.post("/ebilanz/export/some-export-id/validieren")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "VALIDIERT"
    assert "hinweise" in data
    assert len(data["hinweise"]) > 0


@pytest.mark.unit
def test_ebilanz_uebertragen_returns_ticket():
    app, _ = _app_ebilanz()
    client = TestClient(app)
    resp = client.post("/ebilanz/export/some-export-id/uebertragen")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "UEBERTRAGEN"
    ticket = data["elster_transfer_ticket"]
    assert len(ticket) == 16
    assert ticket == ticket.upper()
    assert ticket.isalnum()


# ===========================================================================
# Waagenvorlagen Tests
# ===========================================================================

@pytest.mark.unit
def test_waagen_vorlage_create_and_apply():
    app, db = _app_waagen()

    created_id = None

    # Track calls: first is INSERT (create), second is SELECT (anwenden)
    insert_mock = MagicMock()
    vorlage_data = {
        "id": "vorlage-001",
        "name": "Standard Weizen",
        "waage_id": "W01",
        "kontrakt_nr": "KNR-2026-001",
        "lieferant_nr": "LF-001",
        "fahrer_name": "Hans Müller",
        "kfz_kennzeichen": "MÜ-AB-123",
        "lager_id": "LAG-01",
        "silo_id": "SILO-03",
        "sorte_nr": "WZ001",
        "artikel_nr": "ART-WZ",
        "charge_nr": None,
        "ist_aktiv": True,
        "verwendungen_count": 5,
    }
    select_mock = MagicMock()
    select_mock.mappings.return_value.first.return_value = vorlage_data
    update_mock = MagicMock()

    call_count = [0]

    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return insert_mock
        elif call_count[0] == 2:
            return select_mock
        return update_mock

    db.execute.side_effect = side_effect

    client = TestClient(app)

    # Create
    resp_create = client.post("/waagen/vorlagen", json={
        "name": "Standard Weizen",
        "waage_id": "W01",
        "kontrakt_nr": "KNR-2026-001",
        "lieferant_nr": "LF-001",
    })
    assert resp_create.status_code == 201
    created = resp_create.json()
    assert "id" in created

    # Apply
    resp_apply = client.post(f"/waagen/vorlagen/vorlage-001/anwenden")
    assert resp_apply.status_code == 200
    data = resp_apply.json()
    assert "vorausgefuellt" in data
    assert data["vorausgefuellt"]["waage_id"] == "W01"
    assert "hinweis" in data


@pytest.mark.unit
def test_waagen_vorlage_soft_delete():
    app, db = _app_waagen()
    client = TestClient(app)
    resp = client.delete("/waagen/vorlagen/vorlage-001")
    assert resp.status_code == 204
    # Verify an UPDATE was issued (ist_aktiv=FALSE) — inspect the TextClause text directly
    db.execute.assert_called()
    first_call = db.execute.call_args_list[0]
    # first positional arg is the sqlalchemy TextClause
    sql_clause = first_call[0][0]
    sql_text = str(sql_clause).lower()
    assert "ist_aktiv" in sql_text
