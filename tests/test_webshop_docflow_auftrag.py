"""Webshop-Bestellung -> Auftrag als DocFlow-Entwurf (BELEG-052: DocFlow einziger Belegspeicher, 09.11.2026).

Vorher legte ``process_order`` einen Kopf in ``domain_crm.sales_orders`` an: ohne Positionen und mit dem
Bruttobetrag als ``total_amount``. Jetzt entsteht ein Auftrag in DocFlow mit Positionen; der Nettopreis kommt aus
dem Bruttopreis und dem Steuerschluessel der Zeile. Ohne Steuerschluessel bleibt die Bestellung ein Klaerfall.
"""
from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal

pytestmark = pytest.mark.integration

WURZEL = pathlib.Path(__file__).resolve().parent.parent
_TESTSCHLUESSEL = "x" * 12  # kein echter Schluessel; Gitleaks meldete ein Literal


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"scripts/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture(scope="module")
def mandant():
    from test_belege_lesen import AUFRAEUMEN

    tid = f"ws-{uuid.uuid4().hex[:8]}"
    kunde = str(uuid.uuid4())
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, tid, "Webshop Test")
        db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, email) "
                        "VALUES (:id, :t, 'K-WS-1', 'Hof Webshop', 'hof@webshop.example')"), {"id": kunde, "t": tid})
        db.commit()
    yield {"tid": tid, "kunde": kunde}
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in ("DELETE FROM domain_shared.webshop_bestellungen WHERE tenant_id = :t",
                    "DELETE FROM domain_shared.webshop_sync_log WHERE tenant_id = :t",
                    "DELETE FROM domain_crm.customers WHERE tenant_id = :t", *AUFRAEUMEN):
            db.execute(text(sql), {"t": tid})
        db.commit()


def _bestellung(nr: str, steuerschluessel: str | None) -> dict:
    zeile = {"artikel_nr": "SAAT-1", "bezeichnung": "Saatgut", "menge": 2, "preis_brutto": 119.0}
    if steuerschluessel:
        zeile["steuerschluessel"] = steuerschluessel
    return {"externe_bestellnr": nr, "shop_system": "CUSTOM", "kunde_email": "hof@webshop.example",
            "kunde_name": "Hof Webshop", "artikel_positionen": [zeile], "gesamtbetrag_brutto": 238.0,
            "bestelldatum": "2026-11-09"}


def test_bestellung_wird_docflow_auftrag_mit_nettopreis(mandant):
    from app.services.webshop_integration_service import WebshopIntegrationService

    nr = f"WS-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        dienst = WebshopIntegrationService(db, mandant["tid"])
        dienst.import_orders([_bestellung(nr, "3")])
        ergebnis = dienst.process_order(nr)
        assert ergebnis["verarbeitet"] is True, ergebnis
        kopf = db.execute(text("SELECT doc_type, status, customer_id, source_system, source_ref, total_net "
                               "FROM domain_docflow.document_headers WHERE id = :id AND tenant_id = :t"),
                          {"id": ergebnis["auftrag_id"], "t": mandant["tid"]}).mappings().one()
        assert (kopf["doc_type"], kopf["status"], kopf["customer_id"]) == ("sales_order", "draft", mandant["kunde"])
        assert (kopf["source_system"], kopf["source_ref"]) == ("webshop", nr)
        assert float(kopf["total_net"]) == pytest.approx(200.0)  # 2 x 119 brutto bei 19 %
        # Kein zweiter Auftrag daneben (domain_crm.sales_orders ist seit BELEG-052 die Sicht auf DocFlow).
        alt = db.execute(text("SELECT count(*) FROM domain_crm.sales_orders WHERE tenant_id = :t AND id <> :id"),
                         {"t": mandant["tid"], "id": ergebnis["auftrag_id"]}).scalar()
        assert alt == 0
        # Wiederholt: derselbe Auftrag, kein zweiter.
        assert dienst.process_order(nr)["auftrag_nr"] == ergebnis["auftrag_nr"]


def test_ohne_steuerschluessel_kein_auftrag(mandant):
    from app.services.webshop_integration_service import WebshopIntegrationService

    nr = f"WS-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        dienst = WebshopIntegrationService(db, mandant["tid"])
        dienst.import_orders([_bestellung(nr, None)])
        ergebnis = dienst.process_order(nr)
    assert ergebnis["verarbeitet"] is False and "LINE_1_TAX_KEY_MISSING" in ergebnis["blockers"]


@pytest.fixture()
def client(mandant):
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "verkauf-ws", "roles": ["SALES_BEARBEITEN",
                                                                                         "SALES_LESEN"]}
    yield TestClient(app, raise_server_exceptions=False)
    if vorher is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = vorher


def test_studio_listen_anbinden_und_verarbeiten(client, mandant):
    """admin/webshop + admin/webshop-bestellungen (09.11.2026): Kommandowege statt der handgebauten Seite."""
    from app.services.webshop_integration_service import WebshopIntegrationService

    kopf = {"X-Tenant-Id": mandant["tid"], "Authorization": "Bearer dev-token"}
    ohne_https = client.post("/api/v1/webshop/konfigurationen/actions/anlegen", headers=kopf, json={
        "shop_url": "shop.example", "shop_system": "SHOPWARE6", "api_key": _TESTSCHLUESSEL}).json()
    assert ohne_https["success"] is False
    angebunden = client.post("/api/v1/webshop/konfigurationen/actions/anlegen", headers=kopf, json={
        "shop_url": "https://shop.example", "shop_system": "SHOPWARE6", "api_key": _TESTSCHLUESSEL}).json()
    assert angebunden["success"] is True, angebunden
    [anbindung] = client.get("/api/v1/webshop/konfigurationen", headers=kopf).json()
    assert "api_key" not in anbindung  # nur maskiert gespeichert, nie zurueckgegeben

    gut, ohne_steuer = f"WS-{uuid.uuid4().hex[:6]}", f"WS-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        WebshopIntegrationService(db, mandant["tid"]).import_orders([_bestellung(gut, "3"), _bestellung(ohne_steuer, None)])
    zeilen = {z["externe_bestellnr"]: z for z in client.get("/api/v1/webshop/bestellungen/liste", headers=kopf).json()}
    assert zeilen[gut]["status"] == "NEU" and zeilen[gut]["erp_order_number"] is None
    erledigt = client.post(f"/api/v1/webshop/bestellungen/{zeilen[gut]['id']}/actions/verarbeiten",
                           headers=kopf, json={}).json()
    assert erledigt["success"] is True, erledigt
    nochmal = client.post(f"/api/v1/webshop/bestellungen/{gut}/actions/verarbeiten", headers=kopf, json={}).json()
    assert nochmal["success"] is False and "bereits" in nochmal["error"]
    blockiert = client.post(f"/api/v1/webshop/bestellungen/{ohne_steuer}/actions/verarbeiten",
                            headers=kopf, json={}).json()
    assert blockiert["success"] is False and "TAX_KEY" in blockiert["error"]
    weg = client.post(f"/api/v1/webshop/konfigurationen/{anbindung['id']}/actions/entfernen", headers=kopf,
                      json={"_auditReason": "Shop abgeschaltet"}).json()
    assert weg["success"] is True, weg
    with SessionLocal() as db:
        db.execute(text("DELETE FROM domain_shared.webshop_configs WHERE tenant_id = :t"), {"t": mandant["tid"]})
        db.commit()
