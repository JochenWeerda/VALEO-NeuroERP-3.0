"""Tests for webshop_integration, atlas_zollausfuhr, saatzucht, o2c_uat_scaffold endpoints."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.api.v1.endpoints import (
    webshop_integration,
    atlas_zollausfuhr,
    saatzucht,
    o2c_uat_scaffold,
)
from app.services.webshop_integration_service import _ORDER_STORE


# ── Client factories ──────────────────────────────────────────────────────────

def _mock_db():
    db = MagicMock()
    db.execute.return_value.fetchall.return_value = []
    db.execute.return_value.fetchone.return_value = None
    db.commit.return_value = None
    db.rollback.return_value = None
    return db


def _webshop_client() -> TestClient:
    app = FastAPI()
    db = _mock_db()
    app.dependency_overrides[webshop_integration.get_db] = lambda: db
    app.dependency_overrides[webshop_integration.get_tenant_id] = lambda: "test-tenant"
    app.include_router(webshop_integration.router)
    return TestClient(app)


def _atlas_client() -> TestClient:
    app = FastAPI()
    db = _mock_db()
    app.dependency_overrides[atlas_zollausfuhr.get_db] = lambda: db
    app.dependency_overrides[atlas_zollausfuhr.get_tenant_id] = lambda: "test-tenant"
    app.include_router(atlas_zollausfuhr.router)
    return TestClient(app)


def _saatzucht_client() -> TestClient:
    app = FastAPI()
    db = _mock_db()
    app.dependency_overrides[saatzucht.get_db] = lambda: db
    app.dependency_overrides[saatzucht.get_tenant_id] = lambda: "test-tenant"
    app.include_router(saatzucht.router)
    return TestClient(app)


def _uat_client() -> TestClient:
    app = FastAPI()
    db = _mock_db()
    app.dependency_overrides[o2c_uat_scaffold.get_db] = lambda: db
    app.dependency_overrides[o2c_uat_scaffold.get_tenant_id] = lambda: "test-tenant"
    app.include_router(o2c_uat_scaffold.router)
    return TestClient(app)


# ── Webshop tests ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_webshop_sync_status_bereit():
    client = _webshop_client()
    resp = client.get("/webshop/sync-status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "BEREIT"


@pytest.mark.unit
def test_webshop_bestellung_import_counts():
    _ORDER_STORE.clear()
    client = _webshop_client()
    bestellungen = [
        {
            "externe_bestellnr": "ORD-001",
            "shop_system": "SHOPWARE6",
            "kunde_email": "a@example.com",
            "kunde_name": "Anna Müller",
            "artikel_positionen": [{"artikel_nr": "ART-1", "menge": 2, "preis_brutto": 10.0}],
            "gesamtbetrag_brutto": 20.0,
            "bestelldatum": "2026-05-01",
            "status": "NEU",
        },
        {
            "externe_bestellnr": "ORD-002",
            "shop_system": "SHOPWARE6",
            "kunde_email": "b@example.com",
            "kunde_name": "Bob Schmidt",
            "artikel_positionen": [{"artikel_nr": "ART-2", "menge": 1, "preis_brutto": 50.0}],
            "gesamtbetrag_brutto": 50.0,
            "bestelldatum": "2026-05-02",
            "status": "NEU",
        },
    ]
    resp = client.post("/webshop/bestellungen/import", json=bestellungen)
    assert resp.status_code == 200
    body = resp.json()
    assert body["neue_bestellungen"] == 2
    assert body["fehler"] == 0
    assert body["duplikate"] == []


@pytest.mark.unit
def test_webshop_bestellung_import_is_idempotent_by_external_order_number():
    _ORDER_STORE.clear()
    client = _webshop_client()
    bestellung = {
        "externe_bestellnr": "ORD-IDEMP-001",
        "shop_system": "SHOPWARE6",
        "kunde_email": "kunde@example.com",
        "kunde_name": "Kunde GmbH",
        "artikel_positionen": [{"artikel_nr": "ART-1", "menge": 2, "preis_brutto": 10.0}],
        "gesamtbetrag_brutto": 20.0,
        "bestelldatum": "2026-05-01",
        "status": "NEU",
    }

    first = client.post("/webshop/bestellungen/import", json=[bestellung])
    second = client.post("/webshop/bestellungen/import", json=[bestellung])

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["neue_bestellungen"] == 1
    assert second.json()["neue_bestellungen"] == 0
    assert second.json()["duplikate"] == ["ORD-IDEMP-001"]


@pytest.mark.unit
def test_webshop_bestellung_import_reports_business_blockers():
    _ORDER_STORE.clear()
    client = _webshop_client()
    bestellung = {
        "externe_bestellnr": "ORD-BLOCK-001",
        "shop_system": "WOOCOMMERCE",
        "kunde_email": "",
        "kunde_name": "",
        "artikel_positionen": [{"artikel_nr": "ART-1", "menge": 2, "preis_brutto": 10.0}],
        "gesamtbetrag_brutto": 99.0,
        "bestelldatum": "2026-05-01",
        "status": "NEU",
    }

    resp = client.post("/webshop/bestellungen/import", json=[bestellung])

    assert resp.status_code == 200
    body = resp.json()
    assert body["neue_bestellungen"] == 1
    assert body["fehler"] == 1
    blockers = body["blockierte_bestellungen"][0]["blockers"]
    assert "CUSTOMER_CONTEXT_MISSING" in blockers
    assert "ORDER_TOTAL_MISMATCH" in blockers


@pytest.mark.unit
def test_webshop_bestellung_verarbeiten_blocks_invalid_import():
    _ORDER_STORE.clear()
    client = _webshop_client()
    bestellung = {
        "externe_bestellnr": "ORD-BLOCK-002",
        "shop_system": "SHOPIFY",
        "kunde_email": "",
        "kunde_name": "",
        "artikel_positionen": [{"artikel_nr": "ART-1", "menge": 1, "preis_brutto": 10.0}],
        "gesamtbetrag_brutto": 10.0,
        "bestelldatum": "2026-05-01",
        "status": "NEU",
    }
    client.post("/webshop/bestellungen/import", json=[bestellung])

    resp = client.post("/webshop/bestellungen/ORD-BLOCK-002/verarbeiten")

    assert resp.status_code == 200
    body = resp.json()
    assert body["verarbeitet"] is False
    assert body["auftrag_nr"] is None
    assert "CUSTOMER_CONTEXT_MISSING" in body["blockers"]


@pytest.mark.unit
def test_webshop_bestellung_verarbeiten():
    _ORDER_STORE.clear()
    client = _webshop_client()
    resp = client.post("/webshop/bestellungen/some-id/verarbeiten")
    assert resp.status_code == 200
    body = resp.json()
    assert body["verarbeitet"] is True
    assert body["auftrag_nr"].startswith("WS-")


# ── ATLAS tests ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_atlas_anmeldung_create_entwurf():
    # Clear in-memory store before test
    atlas_zollausfuhr._store.clear()
    client = _atlas_client()
    payload = {
        "referenz_nr": "REF-2026-001",
        "ausfuhrland_code": "DE",
        "bestimmungsland_code": "FR",
        "anmelder_eori": "DE123456789",
        "waren_positionen": [
            {
                "warennummer_hs8": "10019900",
                "bezeichnung": "Weizen",
                "menge": 100.0,
                "einheit": "t",
                "statistischer_wert_eur": 20000.0,
                "ursprungsland": "DE",
            }
        ],
        "befoerderungsart": 30,
        "ausfuehrender_nr": "LF-001",
        "ausfuhrdatum": "2026-06-01",
        "lieferbedingung": "FCA",
    }
    resp = client.post("/zoll/ausfuhranmeldungen", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "ENTWURF"


@pytest.mark.unit
def test_atlas_uebermitteln_mrn_format():
    atlas_zollausfuhr._store.clear()
    # Seed one record directly into the store
    from uuid import uuid4
    from datetime import datetime
    rec_id = str(uuid4())
    atlas_zollausfuhr._store[rec_id] = {
        "id": rec_id,
        "referenz_nr": "REF-X",
        "ausfuhrland_code": "DE",
        "bestimmungsland_code": "PL",
        "anmelder_eori": "DE999",
        "waren_positionen": [],
        "befoerderungsart": 30,
        "ausfuehrender_nr": "LF-X",
        "ausfuhrdatum": "2026-06-01",
        "lieferbedingung": "FOB",
        "status": "ENTWURF",
        "atlas_mrn": None,
        "erstellt_am": datetime.utcnow().isoformat(),
    }

    client = _atlas_client()
    resp = client.post(f"/zoll/ausfuhranmeldungen/{rec_id}/uebermitteln")
    assert resp.status_code == 200
    body = resp.json()
    assert body["uebermittelt"] is True
    assert body["atlas_mrn"].startswith("DE")


@pytest.mark.unit
def test_atlas_warennummern_suche_weizen():
    client = _atlas_client()
    resp = client.get("/zoll/warennummern/suche", params={"q": "weizen"})
    assert resp.status_code == 200
    body = resp.json()
    hs_codes = [item["hs8"] for item in body]
    assert "10019900" in hs_codes


# ── Saatzucht tests ───────────────────────────────────────────────────────────

@pytest.mark.unit
def test_saatzucht_partie_auto_nr():
    saatzucht._store.clear()
    saatzucht._seq.clear()
    client = _saatzucht_client()
    payload = {
        "sorte_bezeichnung": "Akteur",
        "art_code": "WW",
        "z_stufe": "Z1",
        "vermehrungsbetrieb": "Betrieb Müller",
        "anbauflaeche_ha": 10.5,
        "saatgutmenge_kg": 5000.0,
        "status": "ANBAU",
    }
    resp = client.post("/saatzucht/partien", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["partie_nr"].startswith("SZ-")


@pytest.mark.unit
def test_saatzucht_etikett_felder():
    saatzucht._store.clear()
    saatzucht._seq.clear()
    client = _saatzucht_client()
    # Create a partie first
    payload = {
        "sorte_bezeichnung": "Tobak",
        "art_code": "WR",
        "z_stufe": "Z2",
        "vermehrungsbetrieb": "Betrieb Schulz",
        "anbauflaeche_ha": 8.0,
        "saatgutmenge_kg": 4000.0,
        "keimfaehigkeit_prozent": 92.0,
        "status": "ANERKANNT",
        "anerkennungsnr": "ANK-2026-001",
    }
    create_resp = client.post("/saatzucht/partien", json=payload)
    assert create_resp.status_code == 201
    partie_id = create_resp.json()["id"]

    resp = client.post(f"/saatzucht/partien/{partie_id}/etikett")
    assert resp.status_code == 200
    body = resp.json()
    assert "partie_nr" in body
    assert "sorte" in body
    assert "z_stufe" in body
    assert body["netto_kg"] == 4000.0


@pytest.mark.unit
def test_saatzucht_kontrollprotokoll_bestanden():
    saatzucht._store.clear()
    saatzucht._seq.clear()
    client = _saatzucht_client()
    payload = {
        "sorte_bezeichnung": "Gourmet",
        "art_code": "WG",
        "z_stufe": "Z1",
        "vermehrungsbetrieb": "Betrieb Koch",
        "anbauflaeche_ha": 5.0,
        "saatgutmenge_kg": 2500.0,
        "keimfaehigkeit_prozent": 90.0,
        "status": "ANERKANNT",
    }
    create_resp = client.post("/saatzucht/partien", json=payload)
    partie_id = create_resp.json()["id"]

    resp = client.get(f"/saatzucht/partien/{partie_id}/kontrollprotokoll")
    assert resp.status_code == 200
    body = resp.json()
    assert body["bewertung"] == "BESTANDEN"


@pytest.mark.unit
def test_saatzucht_kontrollprotokoll_nicht_bestanden():
    saatzucht._store.clear()
    saatzucht._seq.clear()
    client = _saatzucht_client()
    payload = {
        "sorte_bezeichnung": "Batis",
        "art_code": "WW",
        "z_stufe": "Z2",
        "vermehrungsbetrieb": "Betrieb Weber",
        "anbauflaeche_ha": 3.0,
        "saatgutmenge_kg": 1500.0,
        "keimfaehigkeit_prozent": 80.0,
        "status": "AUFBEREITUNG",
    }
    create_resp = client.post("/saatzucht/partien", json=payload)
    partie_id = create_resp.json()["id"]

    resp = client.get(f"/saatzucht/partien/{partie_id}/kontrollprotokoll")
    assert resp.status_code == 200
    body = resp.json()
    assert body["bewertung"] == "NICHT BESTANDEN"


# ── O2C UAT tests ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_o2c_uat_szenario_7_schritte():
    o2c_uat_scaffold._store.clear()
    client = _uat_client()
    payload = {
        "szenario_name": "Weizen-Vollkette Q2/2026",
        "rohwarengruppe": "GETREIDE",
        "region": "NRW",
        "test_menge_t": 100.0,
        "test_preis_eur_t": 220.0,
    }
    resp = client.post("/uat/o2c/szenarien", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["schritte"]) == 7
    assert body["gesamtstatus"] == "OFFEN"


@pytest.mark.unit
def test_o2c_uat_schritt_bestanden():
    o2c_uat_scaffold._store.clear()
    client = _uat_client()
    # Create scenario
    create_resp = client.post("/uat/o2c/szenarien", json={
        "szenario_name": "Test NDS",
        "rohwarengruppe": "OELFRUECHTE",
        "region": "NDS",
    })
    szenario_id = create_resp.json()["id"]

    # Mark step 1 as BESTANDEN
    resp = client.post(
        f"/uat/o2c/szenarien/{szenario_id}/schritt/1/ausfuehren",
        json={"status": "BESTANDEN", "dauer_ms": 120},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["schritt_nr"] == 1
    assert body["status"] == "BESTANDEN"


@pytest.mark.unit
def test_o2c_uat_alle_bestanden_gesamtstatus():
    o2c_uat_scaffold._store.clear()
    client = _uat_client()
    create_resp = client.post("/uat/o2c/szenarien", json={
        "szenario_name": "Volltest BY",
        "rohwarengruppe": "LEGUMINOSEN",
        "region": "BY",
    })
    szenario_id = create_resp.json()["id"]

    # Mark all 7 steps as BESTANDEN
    for nr in range(1, 8):
        resp = client.post(
            f"/uat/o2c/szenarien/{szenario_id}/schritt/{nr}/ausfuehren",
            json={"status": "BESTANDEN"},
        )
        assert resp.status_code == 200

    final = resp.json()
    assert final["gesamtstatus"] == "BESTANDEN"


@pytest.mark.unit
def test_o2c_uat_bericht_deckungsgrad():
    o2c_uat_scaffold._store.clear()
    client = _uat_client()
    create_resp = client.post("/uat/o2c/szenarien", json={
        "szenario_name": "Teiltest SH",
        "rohwarengruppe": "HACKFRUECHTE",
        "region": "SH",
    })
    szenario_id = create_resp.json()["id"]

    # Mark 3 of 7 steps as BESTANDEN
    for nr in range(1, 4):
        client.post(
            f"/uat/o2c/szenarien/{szenario_id}/schritt/{nr}/ausfuehren",
            json={"status": "BESTANDEN"},
        )

    resp = client.get(f"/uat/o2c/szenarien/{szenario_id}/bericht")
    assert resp.status_code == 200
    body = resp.json()
    summary = body["zusammenfassung"]
    assert summary["bestanden"] == 3
    assert abs(summary["deckungsgrad_prozent"] - 42.86) < 0.01
