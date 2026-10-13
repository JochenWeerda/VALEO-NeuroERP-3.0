"""DocFlow Phase 0.4 und 0.5: Einkaufsbelege, Buchung der Eingangsrechnung und der Gutschriften ueber Finance.

Entscheidung vom 13.10.2026: DocFlow fuehrt die Belege, der Einkauf verantwortet die Eingangsrechnung fachlich,
Finance bucht. Bis dahin kannte DocFlow nur Verkaufs- und Kassenbelege, eine Gutschrift liess sich „buchen“,
ohne dass eine Buchung entstand, und ein Auftrag liess sich direkt und zusaetzlich ueber seine Lieferscheine
berechnen.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import docflow
from app.core.database import SessionLocal
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from freigabehilfe import sichere_freigabe
from testgrenze import ersetze_mandant, ersetze_nutzer


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"de-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        # SKR03: 3 (USt 19 %, 1776, 8400), 9 (VSt 19 %, 1576, Wareneingang 3400), 8 (VSt 7 %, 1571, 3300); 1600 Kreditoren.
        richte_skr03_ein(db, mandant)
        for nr, name, art in (("1400", "Forderungen aus Lieferungen und Leistungen", "asset"), ("4980", "Betriebsbedarf", "expense")):
            db.execute(text(
                "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
                "VALUES (:id, :t, :nr, :name, :art, true)"), {"id": f"{mandant}-{nr}", "t": mandant, "nr": nr, "name": name, "art": art})
        db.execute(text(
            "INSERT INTO domain_erp.tax_keys (id, tenant_id, code, bezeichnung, steuersatz, gueltig_von, debit_account) "
            "VALUES (:id, :t, '7', 'Vorsteuer 19 % ohne Aufwandskonto', 19, DATE '2021-01-01', '1576')"),
            {"id": f"{mandant}-sk7", "t": mandant})
        db.commit()
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    app = FastAPI()
    app.include_router(docflow.router, prefix="/docflow")
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "admin")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"lauf": lauf, "mandant": mandant, "client": client, "t": {"tenant_id": mandant}}
    finally:
        with SessionLocal() as db:
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            for sql in (
                "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.approvals WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_links WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_header_links WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_postings WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
                "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _beleg(haus, doc_type: str, positionen, partner="lieferant-1"):
    """``positionen`` = (Steuerschluessel, Menge, Preis[, Aufwandskonto])."""
    einkauf = doc_type.startswith("purchase") or doc_type == "goods_receipt"
    zeilen = []
    for nr, p in enumerate(positionen, 1):
        zeile = {"article_number": f"A-{nr}", "quantity": p[1], "unit_price": p[2]}
        if p[0] is not None:
            zeile["tax_code"] = p[0]
        if len(p) > 3:
            zeile["expense_account"] = p[3]
        zeilen.append(zeile)
    rumpf = {"doc_type": doc_type, "doc_number": f"B-{haus['lauf']}-{uuid.uuid4().hex[:5]}", "status": "open", "items": zeilen}
    if partner:
        rumpf["supplier_id" if einkauf else "customer_id"] = partner
    return haus["client"].post("/docflow/", params=haus["t"], json=rumpf)


def _wandle(haus, doc_id: str, ziel: str, mengen=None):
    rumpf = {"target_doc_type": ziel, "idempotency_key": f"wandeln-{uuid.uuid4().hex}"}
    if mengen is not None:
        rumpf["quantities_by_source_item_id"] = mengen
    return haus["client"].post(f"/docflow/{doc_id}/convert", params=haus["t"], json=rumpf)


def _buche(haus, doc_id: str):
    # Braucht die Buchung eine zweite Person (APPROVAL-001), erteilt sie hier eine zweite Kennung.
    sichere_freigabe(haus["mandant"], doc_id, "post")
    return haus["client"].post(f"/docflow/{doc_id}/post", params=haus["t"], json={"idempotency_key": f"buchen-{doc_id}"})


def _storniere(haus, doc_id: str):
    sichere_freigabe(haus["mandant"], doc_id, "reverse")
    return haus["client"].post(f"/docflow/{doc_id}/reverse", params=haus["t"],
                               json={"idempotency_key": f"storno-{doc_id}", "reason": "Falscher Lieferant"})


def _buchungen(mandant: str) -> list[tuple[str, str, Decimal, Decimal]]:
    """(Buchungsnummer, Konto, Soll, Haben), nach Entstehung und Konto."""
    with SessionLocal() as db:
        return [(z[0], z[1], Decimal(str(z[2])), Decimal(str(z[3]))) for z in db.execute(text(
            "SELECT e.entry_number, k.account_number, l.debit, l.credit FROM domain_erp.journal_entry_lines l "
            "JOIN domain_erp.chart_of_accounts k ON k.id = l.account_id "
            "JOIN domain_erp.journal_entries e ON e.id = l.journal_entry_id "
            "WHERE e.tenant_id = :t ORDER BY e.created_at, k.account_number"), {"t": mandant}).fetchall()]


def _konten(mandant: str, vorsatz: str) -> list[tuple[str, Decimal, Decimal]]:
    return [(k, s, h) for nr, k, s, h in _buchungen(mandant) if nr.startswith(vorsatz)]


def _status(doc_id: str) -> str:
    with SessionLocal() as db:
        return db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"), {"id": doc_id}).scalar()


def _op(mandant: str, typ: str) -> list[tuple[Decimal, str]]:
    with SessionLocal() as db:
        return [(Decimal(str(z[0])), z[1]) for z in db.execute(text(
            "SELECT offen, op_status FROM domain_erp.offene_posten WHERE tenant_id = :t AND konto_typ = :typ"),
            {"t": mandant, "typ": typ}).fetchall()]


N = Decimal("0.00")


# --- 0.4 Einkaufskette ------------------------------------------------------------------------

def test_bestellung_zwei_wareneingaenge_eingangsrechnung_bucht_ueber_finance(haus):
    bestellung = _beleg(haus, "purchase_order", [("9", 10, 100)])
    assert bestellung.status_code == 200, bestellung.text
    pos = bestellung.json()["items"][0]["id"]
    # Der Satz der Position kommt aus dem Vorsteuerschluessel.
    assert (bestellung.json()["items"][0]["tax_code"], bestellung.json()["items"][0]["tax_rate"]) == ("9", 19.0)
    erster = _wandle(haus, bestellung.json()["id"], "goods_receipt", {pos: 6})
    zweiter = _wandle(haus, bestellung.json()["id"], "goods_receipt", {pos: 4})
    assert (erster.status_code, zweiter.status_code) == (200, 200), (erster.text, zweiter.text)
    rechnung = _wandle(haus, erster.json()["target_doc_id"], "purchase_invoice")
    assert rechnung.status_code == 200, rechnung.text
    antwort = _buche(haus, rechnung.json()["target_doc_id"])
    assert antwort.status_code == 200, antwort.text
    # Aufwand und Vorsteuer im Soll, Kreditor im Haben — fuer die sechs gelieferten Tonnen.
    assert _konten(haus["mandant"], "AP-") == [
        ("1576", Decimal("114.00"), N), ("1600", N, Decimal("714.00")), ("3400", Decimal("600.00"), N)]
    assert _op(haus["mandant"], "kreditoren") == [(Decimal("714.00"), "offen")]
    assert _status(rechnung.json()["target_doc_id"]) == "posted"
    assert antwort.json()["payload"]["journal_entry_id"]


@pytest.mark.parametrize("doc_type,code,meldung", [
    ("purchase_invoice", "3", "Steuerschlüssel 3 ist für Eingangsbelege nicht bekannt oder nicht gültig"),
    ("purchase_order", "3", "für Eingangsbelege"),
    ("sales_invoice", "9", "Steuerschlüssel 9 ist für Verkaufsbelege nicht bekannt oder nicht gültig"),
])
def test_der_steuerschluessel_muss_zur_belegart_passen(haus, doc_type, code, meldung):
    antwort = _beleg(haus, doc_type, [(code, 1, 100)])
    assert antwort.status_code in (400, 422), antwort.text
    assert meldung in antwort.text


@pytest.mark.parametrize("positionen,meldung", [
    ([(None, 1, 100)], "Position 1 hat keinen Steuerschlüssel"),
    ([("7", 1, 100)], "kein Aufwandskonto"),
])
def test_unklare_eingangsrechnung_wird_nicht_gebucht(haus, positionen, meldung):
    rechnung = _beleg(haus, "purchase_invoice", positionen).json()
    antwort = _buche(haus, rechnung["id"])
    assert antwort.status_code == 409, antwort.text
    assert "nicht gebucht, bitte prüfen" in antwort.json()["detail"] and meldung in antwort.json()["detail"]
    assert _buchungen(haus["mandant"]) == [] and _status(rechnung["id"]) == "open"


def test_das_aufwandskonto_der_position_geht_vor_und_teilt_die_buchung(haus):
    rechnung = _beleg(haus, "purchase_invoice", [("7", 1, 100, "4980"), ("9", 1, 200), ("9", 1, 50, "4980")]).json()
    assert _buche(haus, rechnung["id"]).status_code == 200
    # Je Steuerschluessel und Aufwandskonto eine Gruppe: Aufwand netto und die Vorsteuer dieser Positionen.
    assert sorted(_konten(haus["mandant"], "AP-")) == sorted([
        ("4980", Decimal("100.00"), N), ("1576", Decimal("19.00"), N),   # Schluessel 7, Konto der Position
        ("3400", Decimal("200.00"), N), ("1576", Decimal("38.00"), N),   # Schluessel 9, Konto des Schluessels
        ("4980", Decimal("50.00"), N), ("1576", Decimal("9.50"), N),     # Schluessel 9, Konto der Position
        ("1600", N, Decimal("416.50")),
    ])


def test_eingangsrechnung_ohne_lieferant_wird_nicht_gebucht(haus):
    rechnung = _beleg(haus, "purchase_invoice", [("9", 1, 100)], partner=None).json()
    antwort = _buche(haus, rechnung["id"])
    assert antwort.status_code == 400 and "nur mit Lieferant" in antwort.json()["detail"]
    assert _buchungen(haus["mandant"]) == []


def test_beleg_und_buchung_der_eingangsrechnung_stimmen_auf_den_cent(haus):
    rechnung = _beleg(haus, "purchase_invoice", [("9", 1, 0.33)] * 3).json()
    assert (rechnung["total_net"], rechnung["total_tax"], rechnung["total_gross"]) == (0.99, 0.18, 1.17)
    assert _buche(haus, rechnung["id"]).status_code == 200
    assert _konten(haus["mandant"], "AP-") == [
        ("1576", Decimal("0.18"), N), ("1600", N, Decimal("1.17")), ("3400", Decimal("0.99"), N)]


def test_storno_der_eingangsrechnung_bucht_gegen_und_storniert_den_posten(haus):
    rechnung = _beleg(haus, "purchase_invoice", [("9", 1, 100)]).json()
    assert _buche(haus, rechnung["id"]).status_code == 200
    antwort = _storniere(haus, rechnung["id"])
    assert antwort.status_code == 200, antwort.text
    assert _konten(haus["mandant"], "STORNO-") == [
        ("1576", N, Decimal("19.00")), ("1600", Decimal("119.00"), N), ("3400", N, Decimal("100.00"))]
    assert _op(haus["mandant"], "kreditoren") == [(N, "storniert")]
    assert _status(rechnung["id"]) == "reversed"


# --- 0.5 Gutschriften -------------------------------------------------------------------------

def test_verkaufsgutschrift_bucht_und_mindert_den_posten_der_rechnung(haus):
    rechnung = _beleg(haus, "sales_invoice", [("3", 10, 100)], partner="kunde-1").json()
    assert _buche(haus, rechnung["id"]).status_code == 200
    assert _op(haus["mandant"], "debitoren") == [(Decimal("1190.00"), "offen")]
    gutschrift = _wandle(haus, rechnung["id"], "sales_credit_memo", {rechnung["items"][0]["id"]: 2})
    assert gutschrift.status_code == 200, gutschrift.text
    antwort = _buche(haus, gutschrift.json()["target_doc_id"])
    assert antwort.status_code == 200, antwort.text
    # Erloes netto und Umsatzsteuer im Soll, Forderung brutto im Haben.
    assert _konten(haus["mandant"], "GS-") == [
        ("1400", N, Decimal("238.00")), ("1776", Decimal("38.00"), N), ("8400", Decimal("200.00"), N)]
    assert _op(haus["mandant"], "debitoren") == [(Decimal("952.00"), "teilweise")]


def test_einkaufsgutschrift_bucht_und_mindert_die_verbindlichkeit(haus):
    rechnung = _beleg(haus, "purchase_invoice", [("9", 10, 100)]).json()
    assert _buche(haus, rechnung["id"]).status_code == 200
    gutschrift = _wandle(haus, rechnung["id"], "purchase_credit_memo", {rechnung["items"][0]["id"]: 3})
    assert gutschrift.status_code == 200, gutschrift.text
    assert _buche(haus, gutschrift.json()["target_doc_id"]).status_code == 200
    # Kreditor im Soll, Aufwand und Vorsteuer im Haben.
    assert _konten(haus["mandant"], "EG-") == [
        ("1576", N, Decimal("57.00")), ("1600", Decimal("357.00"), N), ("3400", N, Decimal("300.00"))]
    assert _op(haus["mandant"], "kreditoren") == [(Decimal("833.00"), "teilweise")]


def test_gutschrift_ohne_steuerschluessel_wird_nicht_gebucht(haus):
    gutschrift = _beleg(haus, "sales_credit_memo", [(None, 1, 100)], partner="kunde-1").json()
    antwort = _buche(haus, gutschrift["id"])
    assert antwort.status_code == 409 and "keinen Steuerschlüssel" in antwort.json()["detail"]
    assert _buchungen(haus["mandant"]) == [] and _status(gutschrift["id"]) == "open"


def test_eine_gebuchte_gutschrift_wird_nicht_ohne_gegenbuchung_storniert(haus):
    gutschrift = _beleg(haus, "sales_credit_memo", [("3", 1, 100)], partner="kunde-1").json()
    assert _buche(haus, gutschrift["id"]).status_code == 200
    antwort = _storniere(haus, gutschrift["id"])
    assert antwort.status_code == 400 and "Gegenbuchung" in antwort.json()["detail"]
    assert _status(gutschrift["id"]) == "posted"


# --- Keine Doppelberechnung -------------------------------------------------------------------

@pytest.mark.parametrize("auftragsart,lieferart,rechnungsart,code,partner", [
    ("sales_order", "sales_delivery", "sales_invoice", "3", "kunde-1"),
    ("purchase_order", "goods_receipt", "purchase_invoice", "9", "lieferant-1"),
])
def test_ein_auftrag_mit_lieferung_wird_nicht_direkt_berechnet(haus, auftragsart, lieferart, rechnungsart, code, partner):
    auftrag = _beleg(haus, auftragsart, [(code, 10, 100)], partner=partner).json()
    pos = auftrag["items"][0]["id"]
    assert _wandle(haus, auftrag["id"], lieferart, {pos: 4}).status_code == 200
    antwort = _wandle(haus, auftrag["id"], rechnungsart, {pos: 6})
    assert antwort.status_code == 409 and "aus der Lieferung" in antwort.json()["detail"]


def test_ein_direkt_berechneter_auftrag_wird_nicht_noch_ueber_die_lieferung_berechnet(haus):
    auftrag = _beleg(haus, "sales_order", [("3", 10, 100)], partner="kunde-1").json()
    pos = auftrag["items"][0]["id"]
    assert _wandle(haus, auftrag["id"], "sales_invoice", {pos: 10}).status_code == 200
    lieferschein = _wandle(haus, auftrag["id"], "sales_delivery", {pos: 10})
    assert lieferschein.status_code == 200, lieferschein.text
    antwort = _wandle(haus, lieferschein.json()["target_doc_id"], "sales_invoice")
    assert antwort.status_code == 409 and "Doppelberechnung" in antwort.json()["detail"]
