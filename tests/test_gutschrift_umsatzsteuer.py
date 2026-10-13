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
from app.finance.steuerschluessel import kontenrahmen, richte_skr03_ein
from app.finance.tax_resolver import resolve_tax_key_accounts
from app.services.finance_freigabe import VerkaufsgutschriftFreigabe
from freigabehilfe import sichere_freigabe_fuer
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
    "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
    "DELETE FROM public.agent_proposals WHERE tenant_id = :t",
    "DELETE FROM public.mcp_tool_executions WHERE tenant_id = :t",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"gu-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        # Grundausstattung SKR03: Schluessel 2 (7 %), 3 (19 %), 8 und 9 (Vorsteuer) und die Konten dazu.
        richte_skr03_ein(db, mandant)
        # Dazu, was die Buchhaltung selbst einordnet: steuerfrei mit Erloeskonto, Paragraf 24 ohne, Reverse Charge.
        for code, name, satz, ust, erloes, rc, p24 in (
            ("1", "Steuerfrei (Test)", 0, None, "8400", False, False),
            ("24", "Durchschnittssatz 7,8 %", "7.8", "1773", None, False, True),
            ("94", "Reverse Charge", 0, None, "8400", True, False),
        ):
            db.execute(text(
                "INSERT INTO domain_erp.tax_keys (id, tenant_id, code, bezeichnung, steuersatz, gueltig_von, "
                " credit_account, revenue_account, reverse_charge, par_24_ustg) "
                "VALUES (:id, :t, :code, :name, :satz, DATE '2021-01-01', :ust, :erloes, :rc, :p24)"),
                {"id": f"gu-{lauf}-sk{code}", "t": mandant, "code": code, "name": name, "satz": satz,
                 "ust": ust, "erloes": erloes, "rc": rc, "p24": p24})
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
            yield {"lauf": lauf, "mandant": mandant, "client": client, "frei": "1"}
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
    # Jede Gutschrift braucht die Freigabe einer zweiten Person (APPROVAL-001).
    sichere_freigabe_fuer(VerkaufsgutschriftFreigabe, haus["mandant"], gs)
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
    gs = _gutschrift(haus, [("3", 19, 1000)], total=1190)
    antwort = haus["client"].post(f"/sales/credit-notes/{gs}/post")
    assert antwort.status_code == 200, antwort.text
    assert _buchung(haus["mandant"]) == [
        ("8400", 1000.0, 0.0, "3"),
        ("1776", 190.0, 0.0, "3"),
        ("1400", 0.0, 1190.0, None),
    ]
    assert _zustand(gs) == ("posted", Decimal("1000.00"), Decimal("190.00"))


def test_offener_posten_wird_um_den_bruttobetrag_gemindert(haus):
    gs = _gutschrift(haus, [("3", 19, 1000)], total=1190)
    assert haus["client"].post(f"/sales/credit-notes/{gs}/post").status_code == 200
    with SessionLocal() as db:
        posten = db.execute(text(
            "SELECT offen, op_status FROM domain_erp.offene_posten WHERE tenant_id = :t ORDER BY rechnungsnr"),
            {"t": haus["mandant"]}).fetchall()
    assert [(float(p[0]), p[1]) for p in posten] == [(310.0, "teilweise"), (400.0, "offen")]


def test_gemischte_saetze_werden_je_steuerschluessel_gebucht(haus):
    gs = _gutschrift(haus, [("3", 19, 100), ("2", 7, 200), ("3", None, 50)], total="392.50")
    assert haus["client"].post(f"/sales/credit-notes/{gs}/post").status_code == 200
    assert _buchung(haus["mandant"]) == [
        ("8300", 200.0, 0.0, "2"),
        ("1771", 14.0, 0.0, "2"),
        ("8400", 150.0, 0.0, "3"),
        ("1776", 28.5, 0.0, "3"),
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
        "lines": [{"description": "Weizen", "quantity": "2", "unit_price": "500", "tax_code": "3"}],
    }
    antwort = haus["client"].post("/sales/credit-notes", json=rumpf)
    assert antwort.status_code == 201, antwort.text
    daten = antwort.json()
    assert (Decimal(daten["net_amount"]), Decimal(daten["tax_amount"]), Decimal(daten["total_amount"])) == (
        Decimal("1000.00"), Decimal("190.00"), Decimal("1190.00"))
    sichere_freigabe_fuer(VerkaufsgutschriftFreigabe, haus["mandant"], daten["id"])
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
        "lines": [{"description": "Weizen", "quantity": "1", "unit_price": "100", "tax_code": "3", "tax_rate": "7"}],
    }
    antwort = haus["client"].post("/sales/credit-notes", json=rumpf)
    assert antwort.status_code == 422, antwort.text
    assert "widerspricht" in antwort.json()["detail"]


# --- Keine stillschweigende Steuerannahme: zur Pruefung statt gebucht --------------------------

def test_position_ohne_steuerschluessel(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("3", 19, 100), (None, 19, 50)], total=178.5), "Position 2 hat keinen")


def test_unbekannter_steuerschluessel(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("77", 19, 100)], total=119), "nicht bekannt")


def test_satz_widerspricht_dem_steuerschluessel(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("3", 7, 100)], total=119), "widerspricht dem Steuerschlüssel 3")


def test_steuerschluessel_ohne_erloeskonto(haus):
    """Durchschnittssatz nach Paragraf 24 UStG ist nicht vorbelegt — er muss erst eingeordnet werden."""
    _nicht_gebucht(haus, _gutschrift(haus, [("24", None, 100)], total="107.80"), "kein Erlöskonto")


def test_reverse_charge_wird_nicht_automatisch_gebucht(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [("94", None, 100)], total=100), "Reverse Charge")


def test_belegbetrag_ist_nicht_das_brutto_der_positionen(haus):
    """Ein Belegbetrag von 1.000 bei 1.000 netto und 19 % ist widerspruechlich: brutto waeren 1.190."""
    _nicht_gebucht(haus, _gutschrift(haus, [("3", 19, 1000)], total=1000), "weicht vom Brutto der Positionen 1190.00 ab")


def test_gutschrift_ohne_positionen(haus):
    _nicht_gebucht(haus, _gutschrift(haus, [], total=119), "keine Positionen")


def test_gutschrift_nach_paragraf_14_ist_keine_erloesminderung(haus):
    gs = _gutschrift(haus, [("3", 19, 1000)], total=1190, art="gutschrift_14_ustg")
    _nicht_gebucht(haus, gs, "§ 14 UStG")


def test_fehlendes_konto(haus):
    with SessionLocal() as db:
        db.execute(text("DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t"), {"t": haus["mandant"]})
        db.commit()
    _nicht_gebucht(haus, _gutschrift(haus, [("2", 7, 100)], total=107), "Konto 1771, 8300 fehlt im Kontenplan")


def test_gesperrtes_konto_bucht_nichts(haus):
    """Alles oder nichts: kein Buchungskopf ohne Zeilen, die Gutschrift bleibt Entwurf."""
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, account_number, account_name, account_type, category, tenant_id, is_active, posting_blocked) "
            "VALUES (:id, '1400', 'Forderungen', 'asset', 'receivables', :t, true, true)"),
            {"id": f"gu-{haus['lauf']}-1400", "t": haus["mandant"]})
        db.commit()
    gs = _gutschrift(haus, [("3", 19, 1000)], total=1190)
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


# --- Eine Quelle: der Steuerschluessel des Mandanten --------------------------------------------

def test_testmandant_bucht_nach_skr03(haus):
    with SessionLocal() as db:
        assert kontenrahmen(db, haus["mandant"]) == "SKR03"
        # Zweiter Lauf legt nichts doppelt an.
        assert richte_skr03_ein(db, haus["mandant"]) == {"steuerschluessel": [], "konten": []}
        db.rollback()
        schluessel = db.execute(text(
            "SELECT code, credit_account, debit_account, revenue_account FROM domain_erp.tax_keys "
            "WHERE tenant_id = :t AND code IN ('2', '3', '8', '9') ORDER BY code"), {"t": haus["mandant"]}).fetchall()
    assert [tuple(z) for z in schluessel] == [
        ("2", "1771", None, "8300"), ("3", "1776", None, "8400"), ("8", None, "1571", None), ("9", None, "1576", None)]


def test_eingangsrechnung_findet_das_vorsteuerkonto_zum_satz(haus):
    """Bei gleichem Satz gibt es einen Umsatzsteuer- und einen Vorsteuerschluessel; gemeint ist der zweite."""
    with SessionLocal() as db:
        konten = {satz: resolve_tax_key_accounts(db, haus["mandant"], Decimal(satz), "DE")["debit_account"]
                  for satz in ("19", "7")}
    assert konten == {"19": "1576", "7": "1571"}


def test_steuerschluessel_pflege_fuehrt_das_erloeskonto(haus):
    from app.api.v1.endpoints import tax_keys

    haus["client"].app.include_router(tax_keys.router, prefix="/finance")
    liste = haus["client"].get("/finance/tax-keys")
    assert liste.status_code == 200, liste.text
    nach_code = {k["code"]: k for k in liste.json()}
    assert (nach_code["3"]["revenue_account"], nach_code["24"]["revenue_account"], nach_code["24"]["par_24_ustg"]) == (
        "8400", None, True)
    # Die Buchhaltung ordnet den Durchschnittssatz ein — danach bucht die Gutschrift damit.
    antwort = haus["client"].put(f"/finance/tax-keys/{nach_code['24']['id']}", json={"revenue_account": "8400"})
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["revenue_account"] == "8400"


# --- Maske sales/gutschrift: ScreenDefinition und Kommando-Wege --------------------------------

RUMPF = {
    "customer_id": "kunde-1", "reason": "Retoure",
    "lines": [{"description": "Weizen", "quantity": "2", "unit_price": "500", "tax_code": "3"}],
}


def _koepfe(mandant: str) -> int:
    with SessionLocal() as db:
        return db.execute(text(
            "SELECT count(*) FROM domain_sales.sales_credit_notes WHERE tenant_id = :t"), {"t": mandant}).scalar()


def test_maske_ist_eine_screen_definition_ohne_prozentfeld():
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import _AGENT_SYNONYMS, _SCREEN_LIST_ROUTE, get_screen_definition
    from app.core.screen_governance import governance_errors, ux_lint

    sd = get_screen_definition("sales/gutschrift")
    assert sd["adapter"]["temporary"] is False
    assert "sales/gutschrift" in _AGENT_SYNONYMS and "sales/gutschrift" in _SCREEN_LIST_ROUTE
    assert governance_errors(sd) == []
    assert [f for f in ux_lint(sd) if f["severity"] == "error"] == []
    bereit = _check_readiness(sd)
    assert bereit["generatorReady"] is True and bereit["advisoryScore"] == 1.0

    felder = {f["key"]: f for f in sd["fields"]}
    # Die Steuer kommt aus dem Steuerschluessel: kein Prozentfeld, kein Vorgabewert.
    assert felder["pos_tax_code"]["type"] == "select" and felder["pos_tax_code"]["dataSourceKey"] == "steuerschluessel"
    assert "default" not in felder["pos_tax_code"] and "defaultValue" not in felder["pos_tax_code"]
    assert not [k for k, f in felder.items() if f["type"] == "percentage" or "rate" in k or "satz" in k]
    wege = {a["key"]: a.get("commandEndpoint") for a in sd["actions"]}
    assert wege["speichern"] == "/api/v1/sales/credit-notes/actions/speichern"
    assert wege["buchen"] == "/api/v1/sales/credit-notes/{entity_id}/actions/buchen"


def test_steuer_vorschau_rechnet_wie_die_buchung(haus):
    antwort = haus["client"].post("/sales/credit-notes/steuer-vorschau", json={"lines": RUMPF["lines"]})
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert (daten["geklaert"], Decimal(daten["netto"]), Decimal(daten["steuer"]), Decimal(daten["brutto"])) == (
        True, Decimal("1000.00"), Decimal("190.00"), Decimal("1190.00"))
    assert [(g["tax_code"], Decimal(g["steuer"])) for g in daten["gruppen"]] == [("3", Decimal("190.00"))]


def test_steuer_vorschau_nimmt_ohne_schluessel_nichts_an(haus):
    zeile = {"description": "Weizen", "quantity": "1", "unit_price": "100"}
    daten = haus["client"].post("/sales/credit-notes/steuer-vorschau", json={"lines": [zeile]}).json()
    assert (daten["geklaert"], daten["steuer"], daten["brutto"]) == (False, None, None)
    assert "keinen Steuerschlüssel" in daten["pruefgrund"]


def test_kommando_speichern_trockenlauf_schreibt_nichts(haus):
    antwort = haus["client"].post("/sales/credit-notes/actions/speichern", json={
        **RUMPF, "credit_note_number": f"GS-{haus['lauf']}", "_mode": "dryRun"})
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["success"] is True, antwort.json()
    assert _koepfe(haus["mandant"]) == 0


def test_kommando_speichern_legt_den_entwurf_an_und_lehnt_die_doppelte_nummer_ab(haus):
    rumpf = {**RUMPF, "credit_note_number": f"GS-{haus['lauf']}", "_mode": "execute",
             "_idempotencyKey": f"gs-{haus['lauf']}-1"}
    antwort = haus["client"].post("/sales/credit-notes/actions/speichern", json=rumpf)
    assert antwort.status_code == 200, antwort.text
    ergebnis = antwort.json()
    assert ergebnis["success"] is True, ergebnis
    assert "netto 1000.00, Umsatzsteuer 190.00" in ergebnis["summary"]
    assert _koepfe(haus["mandant"]) == 1

    liste = haus["client"].get("/sales/credit-notes").json()
    assert [(g["status"], Decimal(g["total_amount"])) for g in liste] == [("draft", Decimal("1190.00"))]
    einzeln = haus["client"].get(f"/sales/credit-notes/{liste[0]['id']}").json()
    assert [(z["description"], z["tax_code"]) for z in einzeln["lines"]] == [("Weizen", "3")]

    zweite = haus["client"].post("/sales/credit-notes/actions/speichern", json={
        **rumpf, "_idempotencyKey": f"gs-{haus['lauf']}-2"}).json()
    assert zweite["success"] is False and "bereits vergeben" in zweite["error"]
    assert _koepfe(haus["mandant"]) == 1


def test_kommando_speichern_verlangt_positionen(haus):
    antwort = haus["client"].post("/sales/credit-notes/actions/speichern", json={
        "credit_note_number": f"GS-{haus['lauf']}", "customer_id": "kunde-1", "reason": "Retoure", "lines": [],
        "_mode": "execute"}).json()
    assert antwort["success"] is False and "Position" in antwort["error"]
    assert _koepfe(haus["mandant"]) == 0


def test_kommando_buchen_trockenlauf_nennt_den_pruefgrund(haus):
    gs = _gutschrift(haus, [(None, None, 100)], total=100)
    ergebnis = haus["client"].post(f"/sales/credit-notes/{gs}/actions/buchen", json={"_mode": "dryRun"}).json()
    assert ergebnis["success"] is False
    assert "bitte prüfen" in ergebnis["error"] and "keinen Steuerschlüssel" in ergebnis["error"]
    assert _buchung(haus["mandant"]) == [] and _zustand(gs)[0] == "draft"


def test_kommando_buchen_bucht_mit_audit_und_nur_einmal(haus):
    gs = _gutschrift(haus, [("3", 19, 1000)], total=1190)
    weg = f"/sales/credit-notes/{gs}/actions/buchen"
    assert haus["client"].post(weg, json={"_mode": "dryRun"}).json()["success"] is True
    assert _buchung(haus["mandant"]) == []

    rumpf = {"_mode": "execute", "_idempotencyKey": f"buchen-{gs}"}
    ergebnis = haus["client"].post(weg, json=rumpf).json()
    assert ergebnis["success"] is True, ergebnis
    assert ergebnis["auditEntryId"] and "brutto 1190.00" in ergebnis["summary"]
    erwartet = [("8400", 1000.0, 0.0, "3"), ("1776", 190.0, 0.0, "3"), ("1400", 0.0, 1190.0, None)]
    assert _buchung(haus["mandant"]) == erwartet

    # Wiederholung desselben Auftrags und ein zweiter Auftrag: Es bleibt bei einer Buchung.
    haus["client"].post(weg, json=rumpf)
    zweiter = haus["client"].post(weg, json={"_mode": "execute", "_idempotencyKey": f"buchen-{gs}-2"}).json()
    assert zweiter["success"] is False and "bereits gebucht" in zweiter["error"]
    assert _buchung(haus["mandant"]) == erwartet


def test_kommando_buchen_nennt_die_kontosperre(haus):
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, account_number, account_name, account_type, category, tenant_id, is_active, posting_blocked) "
            "VALUES (:id, '1400', 'Forderungen', 'asset', 'receivables', :t, true, true)"),
            {"id": f"gu-{haus['lauf']}-1400", "t": haus["mandant"]})
        db.commit()
    gs = _gutschrift(haus, [("3", 19, 1000)], total=1190)
    ergebnis = haus["client"].post(f"/sales/credit-notes/{gs}/actions/buchen", json={"_mode": "execute"}).json()
    assert ergebnis["success"] is False and "1400 ist fuer Buchungen gesperrt" in ergebnis["error"]
    assert _buchung(haus["mandant"]) == [] and _zustand(gs)[0] == "draft"


def test_gutschrift_wege_pruefen_die_rolle(haus):
    from app.auth.deps import get_current_user

    haus["client"].app.dependency_overrides[get_current_user] = lambda: {"sub": "x", "name": "x", "roles": ["LAGER_LESEN"]}
    assert haus["client"].get("/sales/credit-notes").status_code == 403
    assert haus["client"].post("/sales/credit-notes/actions/speichern", json={"_mode": "dryRun"}).status_code == 403
    assert haus["client"].post("/sales/credit-notes/x/actions/buchen", json={"_mode": "dryRun"}).status_code == 403


# --- MCP: Agent legt den Entwurf an, gebucht wird durch einen Menschen --------------------------

@pytest.fixture
def mcp(haus):
    from app.api.v1.endpoints.mcp_tool_registry import get_current_user as mcp_nutzer
    from app.api.v1.endpoints.mcp_tool_registry import get_db as mcp_get_db
    from app.api.v1.endpoints.mcp_tool_registry import router as mcp_router

    app = FastAPI()
    app.include_router(mcp_router)
    scopes = ["sales:write"]
    app.dependency_overrides[mcp_nutzer] = lambda: {
        "sub": "agent-7", "scopes": list(scopes), "raw": {"tenant_id": haus["mandant"]}}

    def _db():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[mcp_get_db] = _db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield {**haus, "mcp": client, "scopes": scopes}


def _auftrag(mcp, **zusatz) -> dict:
    return {
        "tool_name": "sales.gutschrift.speichern",
        "parameters": {
            "credit_note_number": f"GS-{mcp['lauf']}-A", "customer_id": "kunde-1", "grund": "Retoure",
            "lines": [{"description": "Weizen", "quantity": 2, "unit_price": 500, "tax_code": "3"}],
            "reason": "Retoure laut Kundenmeldung",
        },
        **zusatz,
    }


def test_mcp_trockenlauf_zeigt_die_betraege_und_schreibt_nichts(mcp):
    antwort = mcp["mcp"].post("/mcp/tools/call", json=_auftrag(mcp))
    assert antwort.status_code == 200, antwort.text
    vorschlag = antwort.json()["proposedChanges"]
    assert (vorschlag["netto"], vorschlag["steuer"], vorschlag["brutto"], vorschlag["pruefgrund"]) == (
        1000.0, 190.0, 1190.0, None)
    assert _koepfe(mcp["mandant"]) == 0


def test_mcp_trockenlauf_nennt_den_pruefgrund_statt_einen_satz_anzunehmen(mcp):
    auftrag = _auftrag(mcp)
    del auftrag["parameters"]["lines"][0]["tax_code"]
    vorschlag = mcp["mcp"].post("/mcp/tools/call", json=auftrag).json()["proposedChanges"]
    assert (vorschlag["steuer"], vorschlag["brutto"]) == (None, None)
    assert "keinen Steuerschlüssel" in vorschlag["pruefgrund"]


def test_mcp_legt_den_entwurf_einmal_an_und_bucht_nicht(mcp):
    ohne_schluessel = mcp["mcp"].post("/mcp/tools/call", json=_auftrag(mcp, mode="execute"))
    assert ohne_schluessel.status_code == 422
    auftrag = _auftrag(mcp, mode="execute", idempotency_key=f"mcp-{mcp['lauf']}")
    erste = mcp["mcp"].post("/mcp/tools/call", json=auftrag)
    assert erste.status_code == 200, erste.text
    ergebnis = erste.json()
    assert ergebnis["success"] is True and ergebnis["auditEntryId"] and ergebnis["brutto"] == 1190.0
    zweite = mcp["mcp"].post("/mcp/tools/call", json=auftrag).json()
    assert zweite["credit_note_id"] == ergebnis["credit_note_id"]
    assert _koepfe(mcp["mandant"]) == 1
    assert _zustand(ergebnis["credit_note_id"])[0] == "draft"
    assert _buchung(mcp["mandant"]) == []


def test_mcp_weist_mandantenangabe_und_fehlendes_recht_ab(mcp):
    fremd = _auftrag(mcp)
    fremd["parameters"]["tenant_id"] = "anderes-haus"
    assert mcp["mcp"].post("/mcp/tools/call", json=fremd).status_code == 422
    mcp["scopes"][:] = ["sales:read"]
    assert mcp["mcp"].post("/mcp/tools/call", json=_auftrag(mcp)).status_code == 403
    assert _koepfe(mcp["mandant"]) == 0


def test_agent_bucht_nicht_direkt_sondern_nur_ueber_vorschlag_und_freigabe():
    """Die Maskenaktionen Buchen, Freigeben und Ablehnen sind fuer Agenten gesperrt; es gibt das Werkzeugpaar."""
    import yaml

    from app.core.screen_definitions import get_screen_definition

    aktionen = {a["key"]: a for a in get_screen_definition("sales/gutschrift")["actions"]}
    for schluessel in ("buchen", "vorschlag_freigeben", "vorschlag_ablehnen"):
        assert aktionen[schluessel]["forbiddenForAgents"] is True, schluessel
        assert aktionen[schluessel]["humanApprovalRequired"] is True, schluessel
    wurzel = __import__("pathlib").Path(__file__).resolve().parent.parent
    karte = yaml.safe_load((wurzel / "config/mcp_mask_action_map.yaml").read_text(encoding="utf-8"))
    eintraege = {m["mask_action_id"]: m for m in karte["mappings"] if m.get("mask") == "sales/gutschrift"}
    assert eintraege["mask:sales/gutschrift:buchen"]["mcp_tool_id"] == "sales.gutschrift.buchen"
    assert eintraege["mask:sales/gutschrift:speichern"]["mcp_tool_id"] == "sales.gutschrift.speichern"
    # Fuer die Freigabe gibt es kein Werkzeug — sie ist die Pruefung durch einen Menschen.
    for schluessel in ("vorschlag_freigeben", "vorschlag_ablehnen"):
        assert eintraege[f"mask:sales/gutschrift:{schluessel}"]["mcp_tool_id"] is None
    werkzeuge = {w["tool_id"]: w for w in
                 yaml.safe_load((wurzel / "config/mcp_erp_tools.yaml").read_text(encoding="utf-8"))["tools"]
                 if "gutschrift" in w["tool_id"]}
    assert sorted(werkzeuge) == ["sales.gutschrift.buchen", "sales.gutschrift.propose", "sales.gutschrift.speichern"]
    assert werkzeuge["sales.gutschrift.buchen"]["human_approval_required"] is True
    assert werkzeuge["sales.gutschrift.propose"]["human_approval_required"] is True


# --- Agent schlaegt vor, Mensch prueft und gibt frei, Agent bucht ---------------------------------

def _werkzeug(mcp, name: str, parameter: dict, **zusatz):
    return mcp["mcp"].post("/mcp/tools/call", json={"tool_name": name, "parameters": parameter, **zusatz})


def _vorschlag(mcp, gs: str) -> str:
    antwort = _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": gs}, mode="propose",
                        idempotency_key=f"vorschlag-{gs}")
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["approval_status"] == "pending"
    return antwort.json()["entwurf_id"]


def _als_mensch(mcp, kennung: str = "buchhaltung-1") -> None:
    from app.auth.deps import get_current_user

    mcp["client"].app.dependency_overrides[get_current_user] = lambda: {
        "sub": kennung, "name": kennung, "roles": ["FINANCE_BEARBEITEN"]}


def _stand(vorschlag: str) -> tuple:
    with SessionLocal() as db:
        return tuple(db.execute(text(
            "SELECT approval_status, reviewed_by, execution_result IS NOT NULL FROM public.agent_proposals "
            "WHERE proposal_id = :id"), {"id": vorschlag}).fetchone())


def test_vorschlag_zeigt_die_buchung_und_bucht_nicht(mcp):
    gs = _gutschrift(mcp, [("3", 19, 1000)], total=1190)
    vorschau = _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": gs}).json()
    assert (vorschau["netto"], vorschau["steuer"], vorschau["brutto"]) == (1000.0, 190.0, 1190.0)
    assert [(z["soll"], z["haben"]) for z in vorschau["buchungszeilen"]] == [(1000.0, 0.0), (190.0, 0.0), (0.0, 1190.0)]
    vorschlag = _vorschlag(mcp, gs)
    assert _stand(vorschlag) == ("pending", None, False)
    assert _buchung(mcp["mandant"]) == [] and _zustand(gs)[0] == "draft"
    # Ein zweiter Vorschlag fuer dieselbe Gutschrift, solange der erste offen ist: abgelehnt.
    zweiter = _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": gs}, mode="propose",
                        idempotency_key=f"vorschlag-{gs}-2")
    assert zweiter.status_code == 409


def test_kein_vorschlag_fuer_eine_gutschrift_die_sich_nicht_buchen_laesst(mcp):
    gs = _gutschrift(mcp, [(None, None, 100)], total=100)
    antwort = _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": gs}, mode="propose",
                        idempotency_key=f"vorschlag-{gs}")
    assert antwort.status_code == 409 and "keinen Steuerschlüssel" in antwort.text
    with SessionLocal() as db:
        assert db.execute(text(
            "SELECT count(*) FROM public.agent_proposals WHERE tenant_id = :t"), {"t": mcp["mandant"]}).scalar() == 0


def test_ohne_freigabe_bucht_der_agent_nicht(mcp):
    gs = _gutschrift(mcp, [("3", 19, 1000)], total=1190)
    vorschlag = _vorschlag(mcp, gs)
    antwort = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                        idempotency_key=f"buchen-{gs}")
    assert antwort.status_code == 409 and "not approved" in antwort.text
    assert _buchung(mcp["mandant"]) == [] and _zustand(gs)[0] == "draft"


def test_mensch_gibt_frei_und_der_agent_bucht_genau_einmal(mcp):
    gs = _gutschrift(mcp, [("3", 19, 1000)], total=1190)
    vorschlag = _vorschlag(mcp, gs)

    _als_mensch(mcp)
    liste = mcp["client"].get("/sales/credit-notes/buchungsvorschlaege", params={"status": "pending"}).json()
    assert [(v["proposal_id"], v["vorgeschlagen_von"], Decimal(v["brutto"])) for v in liste] == [
        (vorschlag, "agent-7", Decimal("1190.00"))]
    weg = f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/freigeben"
    assert mcp["client"].post(weg, json={"_mode": "dryRun"}).json()["success"] is True
    assert _stand(vorschlag)[0] == "pending"
    freigabe = mcp["client"].post(weg, json={"_mode": "execute", "_idempotencyKey": f"frei-{vorschlag}"}).json()
    assert freigabe["success"] is True, freigabe
    assert _stand(vorschlag) == ("approved", "buchhaltung-1", False)
    # Freigeben bucht nicht.
    assert _buchung(mcp["mandant"]) == [] and _zustand(gs)[0] == "draft"

    auftrag = {"mode": "execute", "idempotency_key": f"buchen-{gs}"}
    gebucht = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, **auftrag)
    assert gebucht.status_code == 200, gebucht.text
    assert gebucht.json()["posted"] is True and gebucht.json()["approved_by"] == "buchhaltung-1"
    erwartet = [("8400", 1000.0, 0.0, "3"), ("1776", 190.0, 0.0, "3"), ("1400", 0.0, 1190.0, None)]
    assert _buchung(mcp["mandant"]) == erwartet and _zustand(gs)[0] == "posted"
    assert _stand(vorschlag) == ("approved", "buchhaltung-1", True)

    # Derselbe Auftrag noch einmal: dieselbe Antwort. Ein neuer Auftrag: abgelehnt. Es bleibt bei einer Buchung.
    assert _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, **auftrag).json()["replayed"] is True
    nochmal = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                        idempotency_key=f"buchen-{gs}-2")
    assert nochmal.status_code == 409
    assert _buchung(mcp["mandant"]) == erwartet


def test_wer_vorschlaegt_gibt_nicht_selbst_frei(mcp):
    gs = _gutschrift(mcp, [("3", 19, 1000)], total=1190)
    vorschlag = _vorschlag(mcp, gs)
    _als_mensch(mcp, kennung="agent-7")
    ergebnis = mcp["client"].post(
        f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/freigeben", json={"_mode": "execute"}).json()
    assert ergebnis["success"] is False and "nicht selbst prüfen" in ergebnis["error"]
    assert _stand(vorschlag)[0] == "pending"


def test_freigabe_verlangt_die_rolle_und_kommt_nicht_aus_der_anfrage(mcp):
    """Wer freigibt, steht in der geprueften Anmeldung — ein Kopf oder ein Feld der Anfrage zaehlt nicht."""
    from app.auth.deps import get_current_user

    gs = _gutschrift(mcp, [("3", 19, 1000)], total=1190)
    vorschlag = _vorschlag(mcp, gs)
    weg = f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/freigeben"
    mcp["client"].app.dependency_overrides[get_current_user] = lambda: {"sub": "lager-1", "name": "lager-1", "roles": ["LAGER_LESEN"]}
    antwort = mcp["client"].post(weg, json={"_mode": "execute", "approved_by": "chef"},
                                 headers={"X-VALEO-Roles": "agent:approve,FINANCE_ADMIN"})
    assert antwort.status_code == 403
    assert _stand(vorschlag)[0] == "pending"
    _als_mensch(mcp)
    mcp["client"].post(weg, json={"_mode": "execute", "approved_by": "chef"})
    assert _stand(vorschlag)[:2] == ("approved", "buchhaltung-1")


def test_ablehnung_braucht_einen_grund_und_sperrt_die_buchung(mcp):
    gs = _gutschrift(mcp, [("3", 19, 1000)], total=1190)
    vorschlag = _vorschlag(mcp, gs)
    _als_mensch(mcp)
    weg = f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/ablehnen"
    ohne = mcp["client"].post(weg, json={"_mode": "execute"}).json()
    assert ohne["success"] is False and _stand(vorschlag)[0] == "pending"
    mit = mcp["client"].post(weg, json={"_mode": "execute", "_auditReason": "Menge stimmt nicht mit der Retoure"}).json()
    assert mit["success"] is True, mit
    assert _stand(vorschlag)[:2] == ("rejected", "buchhaltung-1")
    abgelehnt = mcp["client"].get("/sales/credit-notes/buchungsvorschlaege").json()[0]
    assert abgelehnt["ablehnungsgrund"] == "Menge stimmt nicht mit der Retoure"
    antwort = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                        idempotency_key=f"buchen-{gs}")
    assert antwort.status_code == 409
    assert _buchung(mcp["mandant"]) == [] and _zustand(gs)[0] == "draft"


def test_gebucht_wird_was_freigegeben_wurde(mcp):
    """Aendert sich die Gutschrift nach der Freigabe, bucht der Agent nicht — es braucht einen neuen Vorschlag."""
    gs = _gutschrift(mcp, [("3", 19, 1000)], total=1190)
    vorschlag = _vorschlag(mcp, gs)
    _als_mensch(mcp)
    assert mcp["client"].post(f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/freigeben",
                              json={"_mode": "execute"}).json()["success"] is True
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_sales.sales_credit_note_lines SET line_total = 2000, unit_price = 2000 "
                        "WHERE credit_note_id = :id"), {"id": gs})
        db.execute(text("UPDATE domain_sales.sales_credit_notes SET total_amount = 2380 WHERE id = :id"), {"id": gs})
        db.commit()
    antwort = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                        idempotency_key=f"buchen-{gs}")
    assert antwort.status_code == 409 and "changed after approval" in antwort.text
    assert _buchung(mcp["mandant"]) == [] and _zustand(gs)[0] == "draft"
