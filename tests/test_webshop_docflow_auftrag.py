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
        alt = db.execute(text("SELECT count(*) FROM domain_crm.sales_orders WHERE tenant_id = :t"),
                         {"t": mandant["tid"]}).scalar()
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
