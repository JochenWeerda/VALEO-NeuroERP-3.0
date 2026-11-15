"""Einkaufs-Lesewege auf DocFlow (BELEG-052 Phase 3a, 10.11.2026).

MCP ``einkauf.bestellung.list``/``status`` lasen ``domain_einkauf.bestellungen``; die Belegkontrolle las
``domain_procurement.purchase_orders`` - eine Tabelle, die keine Migration anlegt, die Projektion fand nie eine
Bestellung - und den stillgelegten Lieferscheinspeicher. Jetzt lesen alle DocFlow: Bestellung offen, teilgeliefert
(Wareneingang entstanden) oder abgeschlossen; Lieferschein ohne Rechnung. Gegen echtes Schema, zurueckgerollt.
"""
from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


@pytest.fixture
def w():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t = f"ek-{uuid.uuid4().hex[:8]}"
    v = verbindung  # Testdaten an der Verbindung: das Werkzeug rollt seine eigene Sitzung zurueck, nicht sie
    v.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    v.execute(sa.text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                      "VALUES (:id, :t, 'L-7', 'Saatzucht Nord')"), {"id": str(uuid.uuid4()), "t": t})
    v.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                      "VALUES (:id, :t, 'K-7', 'Hof Projektion')"), {"id": str(uuid.uuid4()), "t": t})
    try:
        yield {"db": s, "v": v, "t": t}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _beleg(w, art: str, nummer: str, status: str, *, lieferant=None, kunde=None) -> str:
    kennung = str(uuid.uuid4())
    w["v"].execute(sa.text(
        "INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, status, source_system, "
        "customer_id, supplier_id, currency, total_net, total_tax, total_gross, document_date, version, created_at, "
        "updated_at) VALUES (:id, :t, :a, :nr, :st, 'test', :k, :l, 'EUR', 100, 7, 107, NOW(), 1, NOW(), NOW())"),
        {"id": kennung, "t": w["t"], "a": art, "nr": nummer, "st": status, "k": kunde, "l": lieferant})
    return kennung


def _folge(w, von: str, nach: str, relation: str) -> None:
    w["v"].execute(sa.text(
        "INSERT INTO domain_docflow.document_links (id, tenant_id, from_header_id, to_header_id, relation_type) "
        "VALUES (:id, :t, :v, :n, :r)"), {"id": str(uuid.uuid4()), "t": w["t"], "v": von, "n": nach, "r": relation})


def _mcp(w, werkzeug: str, parameter: dict):
    from app.services.mcp_execution_service import ToolExecutionRequest, _bestellung_list, _bestellung_status

    anfrage = ToolExecutionRequest(tool_name=werkzeug, parameters=parameter, mode="dryRun")
    funktion = _bestellung_list if werkzeug.endswith(".list") else _bestellung_status
    return funktion(w["db"], anfrage, "agent", w["t"])


def test_bestellungen_offen_teilgeliefert_abgeschlossen(w):
    offen = _beleg(w, "purchase_order", "B-1", "open", lieferant="L-7")
    teil = _beleg(w, "purchase_order", "B-2", "open", lieferant="L-7")
    _folge(w, teil, _beleg(w, "goods_receipt", "WE-2", "open", lieferant="L-7"), "order_to_receipt")
    _beleg(w, "purchase_order", "B-3", "completed", lieferant="L-7")

    alle = _mcp(w, "einkauf.bestellung.list", {})
    assert {z["bestellung_id"] for z in alle["items"]} >= {offen, teil}
    assert alle["count"] == 3
    assert [z["bestellung_id"] for z in _mcp(w, "einkauf.bestellung.list", {"status": "teilgeliefert"})["items"]] == [teil]
    assert _mcp(w, "einkauf.bestellung.list", {"status": "abgeschlossen"})["count"] == 1
    erste = _mcp(w, "einkauf.bestellung.list", {"status": "offen"})["items"][0]
    assert erste["lieferant"] == "Saatzucht Nord"
    assert erste["route_path"] == f"/belege/purchase_order/{offen}"
    assert erste["screen_id"] == "beleg/purchase-order"

    stand = _mcp(w, "einkauf.bestellung.status", {"bestellung_id": "B-2"})
    assert (stand["bestellung_id"], stand["status"], stand["phase"]) == (teil, "open", "teilgeliefert")


def test_bestellstatus_fremder_mandant_ist_404(w):
    from fastapi import HTTPException

    _beleg(w, "purchase_order", "B-9", "open")
    w["t"] = "anderer-mandant"
    with pytest.raises(HTTPException) as fehler:
        _mcp(w, "einkauf.bestellung.status", {"bestellung_id": "B-9"})
    assert fehler.value.status_code == 404


def test_belegkontrolle_projiziert_aus_docflow(w):
    from app.services.document_control_projection import (
        collect_missing_inbound_documents, collect_open_purchase_orders, collect_uninvoiced_delivery_notes)

    ohne_we = _beleg(w, "purchase_order", "B-1", "open", lieferant="L-7")
    mit_we = _beleg(w, "purchase_order", "B-2", "open", lieferant="L-7")
    _folge(w, mit_we, _beleg(w, "goods_receipt", "WE-2", "open"), "order_to_receipt")
    _beleg(w, "purchase_order", "B-0", "draft")
    ls_offen = _beleg(w, "sales_delivery", "LS-1", "open", kunde="K-7")
    ls_fakturiert = _beleg(w, "sales_delivery", "LS-2", "open", kunde="K-7")
    _folge(w, ls_fakturiert, _beleg(w, "sales_invoice", "R-2", "open", kunde="K-7"), "delivery_to_invoice")
    ls_storniert = _beleg(w, "sales_delivery", "LS-3", "open", kunde="K-7")
    _folge(w, ls_storniert, _beleg(w, "sales_invoice", "R-3", "reversed", kunde="K-7"), "delivery_to_invoice")

    assert {f["document_ref"] for f in collect_open_purchase_orders(w["db"], w["t"])} == {ohne_we, mit_we}
    fehlend = collect_missing_inbound_documents(w["db"], w["t"])
    assert [f["document_ref"] for f in fehlend] == [ohne_we]
    assert fehlend[0]["partner_name"] == "Saatzucht Nord"
    assert fehlend[0]["source_route"] == f"/belege/purchase_order/{ohne_we}"
    ls = collect_uninvoiced_delivery_notes(w["db"], w["t"])
    assert {f["document_ref"] for f in ls} == {ls_offen, ls_storniert}
    assert {f["partner_name"] for f in ls} == {"Hof Projektion"}


def test_eingangsrechnung_fuer_freigabevorschlag_aus_docflow(w):
    from fastapi import HTTPException

    from app.services.mcp_execution_service import _ap_invoice_preview, _load_ap_invoice

    kennung = _beleg(w, "purchase_invoice", "ER-5", "open", lieferant="L-7")
    rechnung = _load_ap_invoice(w["db"], "ER-5", w["t"])
    vorschau = _ap_invoice_preview(rechnung, rechnung["id"])
    assert (vorschau["invoice_id"], vorschau["invoice_number"], vorschau["status"]) == (kennung, "ER-5", "open")
    assert vorschau["brutto_eur"] == 107.0
    assert vorschau["route_path"] == f"/belege/purchase_invoice/{kennung}"
    with pytest.raises(HTTPException) as fehler:
        _load_ap_invoice(w["db"], "ER-5", "anderer-mandant")
    assert fehler.value.status_code == 404
