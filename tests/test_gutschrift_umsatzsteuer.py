"""Gutschrift: Umsatzsteuer je Position, Erloes netto, Steuer getrennt, Forderung brutto.

Fachliche Entscheidung vom 12.10.2026:
1. Steuersatz je Position, nicht pauschal je Gutschrift.
2. Netto, Umsatzsteuer und Brutto getrennt fuehren; der Belegbetrag ist brutto.
3. Das Erloeskonto wird nur netto belastet.
4. Die Umsatzsteuer wird auf dem passenden Steuerkonto berichtigt.
5. Keine stillschweigende Steuerannahme: Fehlt eine Angabe oder widersprechen sich Angaben, wird nicht
   gebucht, sondern zur Pruefung vorgelegt.

Bis dahin ging der Gesamtbetrag ungeteilt gegen 8400, und die Position trug den Satz 19 als Vorgabe.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import sales_credit_notes
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from testgrenze import ersetze_mandant, ersetze_nutzer

AUFRAEUMEN = (
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
    "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
    "DELETE FROM domain_sales.sales_credit_note_lines WHERE credit_note_id IN "
    "(SELECT id FROM domain_sales.sales_credit_notes WHERE tenant_id = :t)",
    "DELETE FROM domain_sales.sales_credit_notes WHERE tenant_id = :t",
    "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
    "DELETE FROM vat_codes WHERE tenant_id = :t",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"gu-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        # Der gemeinsame Rahmen kennt 1400, 1776, 8400. Die Konten fuer 7 % legt das Haus selbst an.
        for nummer, name, art in (("8300", "Erlöse 7 % USt", "revenue"), ("1771", "Umsatzsteuer 7 %", "liability")):
            db.execute(text(
                "INSERT INTO domain_erp.chart_of_accounts "
                "(id, account_number, account_name, account_type, category, tenant_id, is_active) "
                "VALUES (:id, :nr, :name, :art, 'test', :t, true)"),
                {"id": f"gu-{lauf}-{nummer}", "nr": nummer, "name": name, "art": art, "t": mandant})
        # Ein eigener, steuerfreier Schluessel mit eingeordnetem Erloeskonto.
        db.execute(text(
            "INSERT INTO vat_codes (id, name, category, rate, skr03_revenue_account, is_active, is_zero, tenant_id) "
            "VALUES (:id, 'Steuerfrei (Test)', 'EXEMPT', 0, '8400', true, true, :t)"),
            {"id": f"GU{lauf}_FREI", "t": mandant})
        for nr, offen in ((1, 1500), (2, 400)):
            db.execute(text(
                "INSERT INTO domain_erp.offene_posten "
                "(id, tenant_id, rechnungsnr, konto_typ, kunde_id, betrag, offen, op_status) "
                "VALUES (:id, :t, :re, 'debitoren', 'kunde-1', :offen, :offen, 'offen')"),
                {"id": f"gu-{lauf}-op{nr}", "t": mandant, "re": f"RE-{lauf}-{nr}", "offen": offen})
        db.commit()

    monkeypatch.setattr(sales_credit_notes, "assert_customer_allowed_for_invoice", lambda *a, **k: None)
    monkeypatch.setattr(sales_credit_notes, "log_fibu_audit", lambda *a, **k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(sales_credit_notes.router)
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "admin")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"lauf": lauf, "mandant": mandant, "client": client, "frei": f"GU{lauf}_FREI"}
    finally:
        with SessionLocal() as db:
            for sql in AUFRAEUMEN:
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _gutschrift(haus, positionen, *, total, art="rechnungskorrektur") -> str:
    """Legt eine Gutschrift roh an: ``positionen`` = (Steuerschluessel, Satz, Netto)."""
    lauf, gs = haus["lauf"], f"gu-{haus['lauf']}-{uuid.uuid4().hex[:4]}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_sales.sales_credit_notes "
            "(id, tenant_id, credit_note_number, customer_id, invoice_reference, reason, total_amount, status, "
            " correction_type) VALUES (:id, :t, :nr, 'kunde-1', :re, 'Retoure', :total, 'draft', :art)"),
            {"id": gs, "t": haus["mandant"], "nr": gs.upper(), "re": f"RE-{lauf}-1", "total": total, "art": art})
        for nr, (code, satz, netto) in enumerate(positionen, 1):
            db.execute(text(
                "INSERT INTO domain_sales.sales_credit_note_lines "
                "(id, credit_note_id, line_number, description, quantity, unit_price, tax_code, tax_rate, line_total) "
                "VALUES (:id, :gs, :nr, 'Position', 1, :netto, :code, :satz, :netto)"),
                {"id": f"{gs}-{nr}", "gs": gs, "nr": nr, "code": code, "satz": satz, "netto": netto})
        db.commit()
    return gs


def _buchung(mandant: str) -> list[tuple[str, float, float, str | None]]:
    with SessionLocal() as db:
        zeilen = db.execute(text(
            "SELECT k.account_number, l.debit, l.credit, l.tax_code FROM domain_erp.journal_entry_lines l "
            "JOIN domain_erp.chart_of_accounts k ON k.id = l.account_id "
            "JOIN domain_erp.journal_entries e ON e.id = l.journal_entry_id "
            "WHERE e.tenant_id = :t ORDER BY l.line_number"), {"t": mandant}).fetchall()
    return [(z[0], float(z[1]), float(z[2]), z[3]) for z in zeilen]


def _zustand(gs: str) -> tuple:
    with SessionLocal() as db:
        return tuple(db.execute(text(
            "SELECT status, net_amount, tax_amount FROM domain_sales.sales_credit_notes WHERE id = :id"),
            {"id": gs}).fetchone())


def _nicht_gebucht(haus, gs: str, erwartet: str) -> None:
    antwort = haus["client"].post(f"/sales/credit-notes/{gs}/post")
    assert antwort.status_code == 409, antwort.text
    assert "nicht gebucht, bitte prüfen" in antwort.json()["detail"]
    assert erwartet in antwort.json()["detail"], antwort.json()["detail"]
    assert _buchung(haus["mandant"]) == []
    assert _zustand(gs)[0] == "draft"


# --- Der Regelfall --------------------------------------------------------------------------

def test_1190_brutto_mit_19_prozent(haus):
    """Das Buchungsbeispiel der Entscheidung: 8400 Soll 1.000, 1776 Soll 190, Debitor Haben 1.190."""
    gs = _gutschrift(haus, [("DE_19", 19, 1000)], total=1190)
    antwort = haus["client"].post(f"/sales/credit-notes/{gs}/post")
    assert antwort.status_code == 200, antwort.text
    assert _buchung(haus["mandant"]) == [
        ("8400", 1000.0, 0.0, "DE_19"),
        ("1776", 190.0, 0.0, "DE_19"),
        ("1400", 0.0, 1190.0, None),
    ]
    assert _zustand(gs) == ("posted", Decimal("1000.00"), Decimal("190.00"))


def test_offener_posten_wird_um_den_bruttobetrag_gemindert(haus):
    gs = _gutschrift(haus, [("DE_19", 19, 1000)], total=1190)
    assert haus["client"].post(f"/sales/credit-notes/{gs}/post").status_code == 200
    with SessionLocal() as db:
        posten = db.execute(text(
            "SELECT offen, op_status FROM domain_erp.offene_posten WHERE tenant_id = :t ORDER BY rechnungsnr"),
            {"t": haus["mandant"]}).fetchall()
    assert [(float(p[0]), p[1]) for p in posten] == [(310.0, "teilweise"), (400.0, "offen")]


def test_gemischte_saetze_werden_je_steuerschluessel_gebucht(haus):
    gs = _gutschrift(haus, [("DE_19", 19, 100), ("DE_7", 7, 200), ("DE_19", None, 50)], total="392.50")
    assert haus["client"].post(f"/sales/credit-notes/{gs}/post").status_code == 200
    assert _buchung(haus["mandant"]) == [
        ("8400", 150.0, 0.0, "DE_19"),
        ("1776", 28.5, 0.0, "DE_19"),
        ("8300", 200.0, 0.0, "DE_7"),
        ("1771", 14.0, 0.0, "DE_7"),
        ("1400", 0.0, 392.5, None),
    ]


def test_steuerfreie_gutschrift_bucht_keine_umsatzsteuer(haus):
    """Kein blindes Herausrechnen: Bei 0 % ist brutto gleich netto, und es gibt keine Steuerzeile."""
    gs = _gutschrift(haus, [(haus["frei"], 0, 500)], total=500)
    assert haus["client"].post(f"/sales/credit-notes/{gs}/post").status_code == 200
    assert _buchung(haus["mandant"]) == [("8400", 500.0, 0.0, haus["frei"]), ("1400", 0.0, 500.0, None)]
    assert _zustand(gs) == ("posted", Decimal("500.00"), Decimal("0.00"))


def test_anlegen_fuehrt_netto_steuer_und_brutto_getrennt(haus):
    rumpf = {
        "credit_note_number": f"GS-{haus['lauf']}", "customer_id": "kunde-1", "reason": "Retoure",
        "invoice_reference": f"RE-{haus['lauf']}-1",
        "lines": [{"description": "Weizen", "quantity": "2", "unit_price": "500", "tax_code": "DE_19"}],
    }
    antwort = haus["client"].post("/sales/credit-notes", json=rumpf)
    assert antwort.status_code == 201, antwort.text
    daten = antwort.json()
    assert (Decimal(daten["net_amount"]), Decimal(daten["tax_amount"]), Decimal(daten["total_amount"])) == (
        Decimal("1000.00"), Decimal("190.00"), Decimal("1190.00"))
    assert haus["client"].post(f"/sales/credit-notes/{daten['id']}/post").status_code == 200
    assert _buchung(haus["mandant"])[-1] == ("1400", 0.0, 1190.0, None)


def test_anlegen_ohne_steuerangabe_nimmt_keine_19_prozent_an(haus):
    """Vorher trug jede Position stillschweigend 19 %. Jetzt bleibt die Steuer leer — und gebucht wird so nicht."""
    rumpf = {
        "credit_note_number": f"GS-{haus['lauf']}", "customer_id": "kunde-1", "reason": "Retoure",
        "lines": [{"description": "Weizen", "quantity": "1", "unit_price": "100"}],
    }
    antwort = haus["client"].post("/sales/credit-notes", json=rumpf)
    assert antwort.status_code == 201, antwort.text
    assert antwort.json()["tax_amount"] is None
    with SessionLocal() as db:
        satz = db.execute(text(
            "SELECT tax_rate FROM domain_sales.sales_credit_note_lines WHERE credit_note_id = :id"),
            {"id": antwort.json()["id"]}).scalar()
    assert satz is None
    _nicht_gebucht(haus, antwort.json()["id"], "keinen Steuerschlüssel")


def test_anlegen_mit_widerspruch_wird_abgelehnt(haus):
    rumpf = {
        "credit_note_number": f"GS-{haus['lauf']}", "customer_id": "kunde-1", "reason": "Retoure",
        "lines": [{"description": "Weizen", "quantity": "1", "unit_price": "100", "tax_code": "DE_19", "tax_rate": "7"}],
    }
    antwort = haus["client"].post("/sales/credit-notes", json=rumpf)
    assert antwort.status_code == 422, antwort.text
    assert "widerspricht" in antwort.json()["detail"]


# --- Keine stillschweigende Steuerannahme: zur Pruefung statt gebucht --------------------------

def test_position_ohne_steuerschluessel(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("DE_19", 19, 100), (None, 19, 50)], total=178.5), "Position 2 hat keinen")


def test_unbekannter_steuerschluessel(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("GIBT_ES_NICHT", 19, 100)], total=119), "nicht bekannt")


def test_satz_widerspricht_dem_steuerschluessel(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("DE_19", 7, 100)], total=119), "widerspricht dem Steuerschlüssel DE_19")


def test_steuerschluessel_ohne_erloeskonto(haus):
    """Durchschnittssatz nach Paragraf 24 UStG ist nicht vorbelegt — er muss erst eingeordnet werden."""
    _nicht_gebucht(haus, _gutschrift(haus, [("DE_AGR_24_78", None, 100)], total="107.80"), "kein Erlöskonto")


def test_reverse_charge_wird_nicht_automatisch_gebucht(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("EU_ACQ_19", None, 100)], total=119), "Reverse Charge")


def test_belegbetrag_ist_nicht_das_brutto_der_positionen(haus):
    """Ein Belegbetrag von 1.000 bei 1.000 netto und 19 % ist widerspruechlich: brutto waeren 1.190."""
    _nicht_gebucht(haus, _gutschrift(haus, [("DE_19", 19, 1000)], total=1000), "weicht vom Brutto der Positionen 1190.00 ab")


def test_gutschrift_ohne_positionen(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [], total=119), "keine Positionen")


def test_gutschrift_nach_paragraf_14_ist_keine_erloesminderung(haus):
    gs = _gutschrift(haus, [("DE_19", 19, 1000)], total=1190, art="gutschrift_14_ustg")
    _nicht_gebucht(haus, gs, "§ 14 UStG")


def test_fehlendes_konto(haus):
    with SessionLocal() as db:
        db.execute(text("DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t"), {"t": haus["mandant"]})
        db.commit()
    _nicht_gebucht(haus, _gutschrift(haus, [("DE_7", 7, 100)], total=107), "Konto 1771, 8300 fehlt im Kontenplan")


def test_gesperrtes_konto_bucht_nichts(haus):
    """Alles oder nichts: kein Buchungskopf ohne Zeilen, die Gutschrift bleibt Entwurf."""
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, account_number, account_name, account_type, category, tenant_id, is_active, posting_blocked) "
            "VALUES (:id, '1400', 'Forderungen', 'asset', 'receivables', :t, true, true)"),
            {"id": f"gu-{haus['lauf']}-1400", "t": haus["mandant"]})
        db.commit()
    gs = _gutschrift(haus, [("DE_19", 19, 1000)], total=1190)
    antwort = haus["client"].post(f"/sales/credit-notes/{gs}/post")
    assert antwort.status_code == 409, antwort.text
    assert antwort.json()["detail"] == "Konto 1400 ist fuer Buchungen gesperrt."
    with SessionLocal() as db:
        koepfe = db.execute(text(
            "SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"), {"t": haus["mandant"]}).scalar()
        offen = db.execute(text(
            "SELECT count(*) FROM domain_erp.offene_posten WHERE tenant_id = :t AND offen = betrag"),
            {"t": haus["mandant"]}).scalar()
    assert (koepfe, offen, _zustand(gs)[0]) == (0, 2, "draft")
