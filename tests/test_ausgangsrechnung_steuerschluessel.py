"""Ausgangsrechnung: Umsatzsteuer und Konten aus den Steuerschluesseln der Positionen.

Bis zum 13.10.2026 nahm ``POST /finance/invoices`` Netto, Steuer und Brutto aus der Anfrage. Fehlte die
Steuer, rechnete der Server mit ``(vatRate or 0.19) / 100`` — 0,19 Promille. Gebucht wurde jeder Erloes auf
8400 und jede Steuer auf 1776, gleich welcher Satz in der Position stand.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import finance_invoices
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from app.finance.steuerschluessel import richte_skr03_ein
from testgrenze import ersetze_mandant, ersetze_nutzer

WEG = "/finance/invoices"


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"ar-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        richte_skr03_ein(db, mandant)
        # Der Buchungsdienst bucht nur auf Konten, die dem Mandanten gehoeren.
        for nr, name, art in (("1400", "Forderungen aus Lieferungen und Leistungen", "asset"),
                              ("1776", "Umsatzsteuer 19 %", "liability"), ("8400", "Erlöse 19 % USt", "revenue")):
            db.execute(text(
                "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
                " is_active) SELECT :id, :t, :nr, :name, :art, true WHERE NOT EXISTS (SELECT 1 FROM "
                " domain_erp.chart_of_accounts WHERE tenant_id = :t AND account_number = :nr)"),
                {"id": f"{mandant}-{nr}", "t": mandant, "nr": nr, "name": name, "art": art})
        db.commit()
    monkeypatch.setattr(finance_invoices, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    monkeypatch.setattr(finance_invoices, "register_artifact", lambda *_a, **_k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(finance_invoices.router)
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
                db.execute(text(sql), {"t": mandant, "nr": f"RE-{lauf}-%"})
            db.commit()


def _rechnung(haus, positionen, status="VERSENDET", **abweichend) -> dict:
    """``positionen`` = (Steuerschluessel, Satz, Menge, Preis)."""
    return {
        "number": f"RE-{haus['lauf']}-{uuid.uuid4().hex[:4]}", "date": "2026-10-13", "customerId": "kunde-1",
        "dueDate": "2026-11-12", "status": status,
        "lines": [
            {"article": f"A-{nr}", "qty": menge, "price": preis,
             **({"taxCode": code} if code is not None else {}), **({"vatRate": satz} if satz is not None else {})}
            for nr, (code, satz, menge, preis) in enumerate(positionen, 1)
        ],
        **abweichend,
    }


def _buchung(mandant: str) -> list[tuple[str, Decimal, Decimal]]:
    with SessionLocal() as db:
        return [(z[0], Decimal(str(z[1])), Decimal(str(z[2]))) for z in db.execute(text(
            "SELECT k.account_number, l.debit, l.credit FROM domain_erp.journal_entry_lines l "
            "JOIN domain_erp.chart_of_accounts k ON k.id = l.account_id "
            "JOIN domain_erp.journal_entries e ON e.id = l.journal_entry_id "
            "WHERE e.tenant_id = :t ORDER BY k.account_number"), {"t": mandant}).fetchall()]


def _beleg(nummer: str) -> dict | None:
    import json

    with SessionLocal() as db:
        roh = db.execute(text("SELECT data FROM documents WHERE doc_number = :n"), {"n": nummer}).scalar()
    return None if roh is None else (roh if isinstance(roh, dict) else json.loads(roh))


# --- Der Regelfall --------------------------------------------------------------------------

def test_bucht_erloes_und_steuer_je_steuerschluessel_und_rechnet_selbst(haus):
    # Die Summen der Anfrage sind falsch — der Server rechnet aus den Schluesseln.
    rumpf = _rechnung(haus, [("3", None, 2, 500), ("2", None, 1, 200)], subtotalNet=1, totalTax=1, totalGross=2)
    antwort = haus["client"].post(WEG, json=rumpf)
    assert antwort.status_code == 200, antwort.text
    assert _buchung(haus["mandant"]) == [
        ("1400", Decimal("1404.00"), Decimal("0.00")),
        ("1771", Decimal("0.00"), Decimal("14.00")),
        ("1776", Decimal("0.00"), Decimal("190.00")),
        ("8300", Decimal("0.00"), Decimal("200.00")),
        ("8400", Decimal("0.00"), Decimal("1000.00")),
    ]
    beleg = _beleg(rumpf["number"])
    assert (beleg["subtotalNet"], beleg["totalTax"], beleg["totalGross"]) == (1200.0, 204.0, 1404.0)
    # Der Satz der Position ist das Abbild des Schluessels.
    assert [(z["taxCode"], z["vatRate"]) for z in beleg["lines"]] == [("3", 19.0), ("2", 7.0)]
    with SessionLocal() as db:
        offen = db.execute(text(
            "SELECT betrag FROM domain_erp.offene_posten WHERE tenant_id = :t AND rechnungsnr = :n"),
            {"t": haus["mandant"], "n": rumpf["number"]}).scalar()
    assert Decimal(str(offen)) == Decimal("1404.00")


# --- Keine stillschweigende Annahme ----------------------------------------------------------

@pytest.mark.parametrize("positionen,meldung", [
    ([(None, None, 1, 100)], "Position 1 hat keinen Steuerschlüssel"),
    # Ein Satz allein ist kein Steuerschluessel: Er sagt nicht, auf welches Konto.
    ([("3", None, 1, 100), (None, 19, 1, 50)], "Position 2 hat keinen Steuerschlüssel"),
    ([("3", 7, 1, 100)], "widerspricht dem Steuerschlüssel 3"),
    ([("77", None, 1, 100)], "Steuerschlüssel 77 ist nicht bekannt oder nicht gültig"),
    # Ein reiner Vorsteuerschluessel gehoert nicht in eine Ausgangsrechnung.
    ([("9", None, 1, 100)], "kein Erlöskonto"),
    ([], "keine Positionen"),
])
def test_unklare_steuer_wird_nicht_gebucht_und_nicht_gespeichert(haus, positionen, meldung):
    rumpf = _rechnung(haus, positionen, subtotalNet=100, totalTax=19, totalGross=119)
    antwort = haus["client"].post(WEG, json=rumpf)
    assert antwort.status_code == 409, antwort.text
    assert "nicht gebucht, bitte prüfen" in antwort.json()["detail"] and meldung in antwort.json()["detail"]
    assert _buchung(haus["mandant"]) == []
    assert _beleg(rumpf["number"]) is None


# --- Entwurf ---------------------------------------------------------------------------------

def test_entwurf_ohne_schluessel_wird_gespeichert_und_laesst_die_steuer_offen(haus):
    rumpf = _rechnung(haus, [(None, 19, 1, 100)], status="ENTWURF", subtotalNet=100, totalTax=19, totalGross=119)
    assert haus["client"].post(WEG, json=rumpf).status_code == 200
    beleg = _beleg(rumpf["number"])
    assert "Position 1 hat keinen Steuerschlüssel" in beleg["steuerPruefgrund"]
    # Kein Brutto unterstellen, das es so nicht gibt: Die Steuer der Anfrage wird nicht uebernommen.
    assert (beleg["subtotalNet"], beleg["totalTax"], beleg["totalGross"]) == (100.0, 0.0, 100.0)
    assert _buchung(haus["mandant"]) == []


def test_entwurf_mit_schluessel_traegt_die_steuer_des_servers(haus):
    rumpf = _rechnung(haus, [("2", None, 3, 100)], status="ENTWURF")
    assert haus["client"].post(WEG, json=rumpf).status_code == 200
    beleg = _beleg(rumpf["number"])
    assert (beleg["subtotalNet"], beleg["totalTax"], beleg["totalGross"], beleg["steuerPruefgrund"]) == (
        300.0, 21.0, 321.0, None)


def test_entwurf_wird_erst_mit_schluesseln_gebucht(haus):
    rumpf = _rechnung(haus, [(None, None, 1, 100)], status="ENTWURF")
    assert haus["client"].post(WEG, json=rumpf).status_code == 200
    versendet = {**rumpf, "status": "VERSENDET"}
    abgelehnt = haus["client"].put(f"{WEG}/{rumpf['number']}", json=versendet)
    assert abgelehnt.status_code == 409 and "keinen Steuerschlüssel" in abgelehnt.json()["detail"]
    assert _beleg(rumpf["number"])["status"] == "ENTWURF" and _buchung(haus["mandant"]) == []
    versendet["lines"][0]["taxCode"] = "3"
    assert haus["client"].put(f"{WEG}/{rumpf['number']}", json=versendet).status_code == 200
    assert ("1776", Decimal("0.00"), Decimal("19.00")) in _buchung(haus["mandant"])


def test_eine_gebuchte_rechnung_wird_nicht_neu_gerechnet(haus):
    """Statuswechsel einer gebuchten Rechnung (bezahlt) verlangt keine Steuerschluessel nach."""
    rumpf = _rechnung(haus, [("3", None, 1, 100)])
    assert haus["client"].post(WEG, json=rumpf).status_code == 200
    bezahlt = {**rumpf, "status": "BEZAHLT", "lines": [], "subtotalNet": 100, "totalTax": 19, "totalGross": 119}
    assert haus["client"].put(f"{WEG}/{rumpf['number']}", json=bezahlt).status_code == 200
    assert len(_buchung(haus["mandant"])) == 3
