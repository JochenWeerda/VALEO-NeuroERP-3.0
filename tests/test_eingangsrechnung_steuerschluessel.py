"""Eingangsrechnung: Aufwand und Vorsteuer je Steuerschluessel im Soll, Kreditor brutto im Haben.

Bis zum 13.10.2026 buchten ``POST /finance/ap/invoices/{id}/post`` und der Kernel-Handler seitenverkehrt
(Kreditor im Soll, Aufwand und Vorsteuer im Haben), mit „3300“ und „6000“ als Konten, mit einem einzigen
Vorsteuerkonto nach dem hoechsten Satz (notfalls 1576) — und der REST-Weg meldete „verbucht“, wenn die
Buchung scheiterte.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import ap_approval_workflow, ap_invoices
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from app.finance.steuerschluessel import Steuerklaerung, richte_skr03_ein, vorsteuergruppen
from app.services.finance_freigabe import EingangsrechnungFreigabe
from freigabehilfe import sichere_freigabe_fuer
from testgrenze import ersetze_mandant, ersetze_nutzer

WEG = "/ap/invoices"


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"er-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        # SKR03: Vorsteuerschluessel 8 (7 %, 1571, Wareneingang 3300) und 9 (19 %, 1576, Wareneingang 3400).
        richte_skr03_ein(db, mandant)
        # Der Buchungsdienst bucht nur auf Konten, die dem Mandanten gehoeren.
        for nr, name, art in (("1576", "Abziehbare Vorsteuer 19 %", "asset"), ("4980", "Betriebsbedarf", "expense")):
            db.execute(text(
                "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
                " is_active) SELECT :id, :t, :nr, :name, :art, true WHERE NOT EXISTS (SELECT 1 FROM "
                " domain_erp.chart_of_accounts WHERE tenant_id = :t AND account_number = :nr)"),
                {"id": f"{mandant}-{nr}", "t": mandant, "nr": nr, "name": name, "art": art})
        # Ein Vorsteuerschluessel ohne Aufwandskonto und ein steuerfreier.
        for code, name, satz, vst in (("7", "Vorsteuer 19 % ohne Aufwandskonto", 19, "1576"), ("1", "Steuerfrei", 0, None)):
            db.execute(text(
                "INSERT INTO domain_erp.tax_keys (id, tenant_id, code, bezeichnung, steuersatz, gueltig_von, debit_account) "
                "VALUES (:id, :t, :code, :name, :satz, DATE '2021-01-01', :vst)"),
                {"id": f"{mandant}-sk{code}", "t": mandant, "code": code, "name": name, "satz": satz, "vst": vst})
        db.commit()

    def freigegeben(*_a, **_k):
        return SimpleNamespace(can_post=True, status="approved", required_approvals=1, current_approvals=1)

    from app.services.ap_invoice_approval_service import APApprovalWorkflowService
    monkeypatch.setattr(APApprovalWorkflowService, "status", freigegeben)
    monkeypatch.setattr(ap_invoices, "evaluate_ap_invoice_datensatz", lambda *_a, **_k: SimpleNamespace(bestanden=True))

    def kein_ereignis(*_a, **_k):
        return None

    monkeypatch.setattr(APApprovalWorkflowService, "_post_event", staticmethod(kein_ereignis))
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(ap_invoices.router)
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "admin")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"lauf": lauf, "mandant": mandant, "client": client}
    finally:
        with SessionLocal() as db:
            for sql in (
                "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                "DELETE FROM documents WHERE doc_number LIKE :nr",
                "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                db.execute(text(sql), {"t": mandant, "nr": f"ER-{lauf}-%"})
            db.commit()


def _anlegen(haus, positionen, **abweichend) -> str:
    """``positionen`` = (Steuerschluessel, Satz, Menge, Preis[, Aufwandskonto])."""
    nummer = f"ER-{haus['lauf']}-{uuid.uuid4().hex[:4]}"
    zeilen = []
    for nr, p in enumerate(positionen, 1):
        zeile = {"article": f"A-{nr}", "qty": p[2], "price": p[3]}
        if p[0] is not None:
            zeile["taxCode"] = p[0]
        if p[1] is not None:
            zeile["vatRate"] = p[1]
        zeilen.append(zeile)
    antwort = haus["client"].post(f"{WEG}/", json={
        "number": nummer, "date": "2026-10-13", "customerId": "lieferant-1", "dueDate": "2026-11-12",
        "lines": zeilen, **abweichend})
    assert antwort.status_code == 201, antwort.text
    return nummer


def _freigeben(nummer: str) -> None:
    with SessionLocal() as db:
        db.execute(text(
            "UPDATE documents SET data = jsonb_set(CAST(data AS jsonb), '{status}', '\"FREIGEGEBEN\"') "
            "WHERE doc_type = 'ap_invoice' AND doc_number = :n"), {"n": nummer})
        mandant = db.execute(text(
            "SELECT CAST(data AS jsonb)->>'tenantId' FROM documents WHERE doc_type = 'ap_invoice' AND doc_number = :m"),
            {"m": nummer}).scalar()
        db.commit()
    # Zentrale Freigabe (APPROVAL-001): Eine Finanzrechnung braucht eine zweite Person.
    sichere_freigabe_fuer(EingangsrechnungFreigabe, mandant, nummer)


def _beleg(nummer: str) -> dict:
    with SessionLocal() as db:
        roh = db.execute(text(
            "SELECT data FROM documents WHERE doc_type = 'ap_invoice' AND doc_number = :n"), {"n": nummer}).scalar()
    return roh if isinstance(roh, dict) else json.loads(roh)


def _buchung(mandant: str) -> list[tuple[str, Decimal, Decimal]]:
    with SessionLocal() as db:
        return [(z[0], Decimal(str(z[1])), Decimal(str(z[2]))) for z in db.execute(text(
            "SELECT k.account_number, l.debit, l.credit FROM domain_erp.journal_entry_lines l "
            "JOIN domain_erp.chart_of_accounts k ON k.id = l.account_id "
            "JOIN domain_erp.journal_entries e ON e.id = l.journal_entry_id "
            "WHERE e.tenant_id = :t ORDER BY k.account_number"), {"t": mandant}).fetchall()]


def _buchen(haus, nummer: str):
    return haus["client"].post(f"{WEG}/{nummer}/post", params={"posted_by": "buchhaltung-1"})


# --- Der Regelfall --------------------------------------------------------------------------

def test_bucht_aufwand_und_vorsteuer_im_soll_und_den_kreditor_im_haben(haus):
    nummer = _anlegen(haus, [("9", None, 2, 500), ("8", None, 1, 200)])
    beleg = _beleg(nummer)
    # Schon der Entwurf traegt die Summen des Servers; der Satz ist das Abbild des Schluessels.
    assert (beleg["subtotalNet"], beleg["totalTax"], beleg["totalGross"]) == (1200.0, 204.0, 1404.0)
    assert [(z["taxCode"], z["vatRate"]) for z in beleg["lines"]] == [("9", 19.0), ("8", 7.0)]
    _freigeben(nummer)
    antwort = _buchen(haus, nummer)
    assert antwort.status_code == 200, antwort.text
    assert _buchung(haus["mandant"]) == [
        ("1571", Decimal("14.00"), Decimal("0.00")),      # Vorsteuer 7 %
        ("1576", Decimal("190.00"), Decimal("0.00")),     # Vorsteuer 19 %
        ("1600", Decimal("0.00"), Decimal("1404.00")),    # Verbindlichkeit (Kreditoren, SKR03)
        ("3300", Decimal("200.00"), Decimal("0.00")),     # Wareneingang 7 %
        ("3400", Decimal("1000.00"), Decimal("0.00")),    # Wareneingang 19 %
    ]
    gebucht = _beleg(nummer)
    assert gebucht["status"] == "VERBUCHT" and gebucht["journalEntryId"]
    with SessionLocal() as db:
        posten = db.execute(text(
            "SELECT konto_typ, betrag, offen FROM domain_erp.offene_posten WHERE tenant_id = :t AND rechnungsnr = :n"),
            {"t": haus["mandant"], "n": nummer}).fetchone()
    assert (posten[0], Decimal(str(posten[1])), Decimal(str(posten[2]))) == ("kreditoren", Decimal("1404.00"), Decimal("1404.00"))


def test_das_aufwandskonto_der_rechnung_geht_dem_des_schluessels_vor(haus):
    nummer = _anlegen(haus, [("9", None, 1, 100)], expenseAccountId="4980")
    with SessionLocal() as db:
        db.execute(text(
            "UPDATE documents SET data = jsonb_set(CAST(data AS jsonb), '{expenseAccountId}', '\"4980\"') "
            "WHERE doc_type = 'ap_invoice' AND doc_number = :n"), {"n": nummer})
        db.commit()
    # Erst der endgueltige Inhalt, dann die Freigabe: Eine Aenderung danach machte sie ungueltig.
    _freigeben(nummer)
    assert _buchen(haus, nummer).status_code == 200
    assert ("4980", Decimal("100.00"), Decimal("0.00")) in _buchung(haus["mandant"])


def test_steuerfrei_bucht_ohne_vorsteuerzeile(haus):
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_erp.tax_keys SET expense_account = '4980' WHERE tenant_id = :t AND code = '1'"),
                   {"t": haus["mandant"]})
        db.commit()
    nummer = _anlegen(haus, [("1", None, 1, 100)])
    _freigeben(nummer)
    assert _buchen(haus, nummer).status_code == 200
    assert _buchung(haus["mandant"]) == [
        ("1600", Decimal("0.00"), Decimal("100.00")), ("4980", Decimal("100.00"), Decimal("0.00"))]


# --- Keine stillschweigende Annahme ----------------------------------------------------------

@pytest.mark.parametrize("positionen,meldung", [
    ([(None, None, 1, 100)], "Position 1 hat keinen Steuerschlüssel"),
    # Ein Satz allein ist kein Steuerschluessel — bis zum 13.10.2026 entschied der hoechste Satz ueber das Konto.
    ([("9", None, 1, 100), (None, 19, 1, 50)], "Position 2 hat keinen Steuerschlüssel"),
    ([("9", 7, 1, 100)], "widerspricht dem Steuerschlüssel 9"),
    ([("77", None, 1, 100)], "Steuerschlüssel 77 ist nicht bekannt oder nicht gültig"),
    # Ein Umsatzsteuerschluessel gehoert nicht in eine Eingangsrechnung.
    ([("3", None, 1, 100)], "Steuerschlüssel 3 ist ein Umsatzsteuerschlüssel"),
    ([("7", None, 1, 100)], "Position 1: kein Aufwandskonto"),
])
def test_unklare_rechnung_bleibt_freigegeben_und_ungebucht(haus, positionen, meldung):
    nummer = _anlegen(haus, positionen)
    entwurf = _beleg(nummer)
    assert meldung in entwurf["steuerPruefgrund"]
    # Die Steuer bleibt offen: kein Brutto, das es so nicht gibt.
    assert entwurf["totalTax"] == 0.0 and entwurf["totalGross"] == entwurf["subtotalNet"]
    _freigeben(nummer)
    antwort = _buchen(haus, nummer)
    assert antwort.status_code == 409, antwort.text
    assert "nicht gebucht, bitte prüfen" in antwort.json()["detail"] and meldung in antwort.json()["detail"]
    assert _buchung(haus["mandant"]) == []
    # Bis zum 13.10.2026 stand die Rechnung hier auf „verbucht“.
    assert _beleg(nummer)["status"] == "FREIGEGEBEN"


def test_scheitert_die_buchung_am_konto_bleibt_die_rechnung_freigegeben(haus):
    """Das Vorsteuerkonto des Schluessels gibt es nicht (mehr): keine halbe Buchung, kein „verbucht“."""
    with SessionLocal() as db:
        db.execute(text(
            "UPDATE domain_erp.chart_of_accounts SET is_active = false WHERE tenant_id = :t AND account_number = '1576'"),
            {"t": haus["mandant"]})
        db.commit()
    nummer = _anlegen(haus, [("9", None, 1, 100)])
    _freigeben(nummer)
    assert _buchen(haus, nummer).status_code >= 400
    assert _buchung(haus["mandant"]) == [] and _beleg(nummer)["status"] == "FREIGEGEBEN"
    with SessionLocal() as db:
        assert db.execute(text(
            "SELECT count(*) FROM domain_erp.offene_posten WHERE tenant_id = :t"), {"t": haus["mandant"]}).scalar() == 0


def test_ohne_kontenrahmen_kein_kreditorenkonto(haus):
    with SessionLocal() as db:
        db.execute(text("DELETE FROM domain_shared.system_properties WHERE tenant_id = :t"), {"t": haus["mandant"]})
        db.commit()
    nummer = _anlegen(haus, [("9", None, 1, 100)])
    _freigeben(nummer)
    antwort = _buchen(haus, nummer)
    assert antwort.status_code == 409 and "Kein Kreditorenkonto" in antwort.json()["detail"]


# --- Der Kernel-Weg bucht dasselbe ----------------------------------------------------------

def test_kernel_bucht_ueber_denselben_weg(haus, monkeypatch):
    from app.services.ap_invoice_kernel_posting import post_ap_invoice_kernel_sync
    from app.services import ap_invoice_kernel_posting
    from fastapi import HTTPException
    monkeypatch.setattr(ap_invoice_kernel_posting, "verified_ap_user", lambda tenant: {"sub": "buchhaltung-1", "roles": ["FINANCE_ADMIN"]})

    nummer = _anlegen(haus, [("9", None, 1, 100)])
    unklar = _anlegen(haus, [(None, 19, 1, 100)])
    _freigeben(nummer)
    _freigeben(unklar)
    with SessionLocal() as db:
        post_ap_invoice_kernel_sync(db, invoice_id=nummer, tenant_id=haus["mandant"], posted_by="buchhaltung-1")
        db.commit()
        with pytest.raises(HTTPException) as error:
            post_ap_invoice_kernel_sync(db, invoice_id=unklar, tenant_id=haus["mandant"], posted_by="buchhaltung-1")
        assert error.value.status_code == 409
    assert _buchung(haus["mandant"]) == [
        ("1576", Decimal("19.00"), Decimal("0.00")),
        ("1600", Decimal("0.00"), Decimal("119.00")),
        ("3400", Decimal("100.00"), Decimal("0.00")),
    ]
    assert _beleg(nummer)["status"] == "VERBUCHT" and _beleg(unklar)["status"] == "FREIGEGEBEN"


def test_vorsteuergruppen_trennen_nach_schluessel_und_aufwandskonto(haus):
    with SessionLocal() as db:
        gruppen = vorsteuergruppen(db, haus["mandant"], [
            (1, "9", None, Decimal("100"), None), (2, "9", None, Decimal("50"), "4980"), (3, "9", 19, Decimal("25"), None)])
        assert [(g.tax_code, g.aufwandskonto, g.netto, g.steuer) for g in gruppen] == [
            ("9", "3400", Decimal("125.00"), Decimal("23.75")), ("9", "4980", Decimal("50.00"), Decimal("9.50"))]
        with pytest.raises(Steuerklaerung, match="keine Positionen"):
            vorsteuergruppen(db, haus["mandant"], [])
