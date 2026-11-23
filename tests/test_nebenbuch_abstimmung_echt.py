"""Nebenbuch-Abstimmung gegen das echte OP-Nebenbuch und die Sammelkonten (M3, 23.11.2026).

Bis dahin las ``POST /finance/abstimmung/nebenbuch/{id}/ausfuehren`` den leeren Altspeicher ``public.offene_posten``
und verglich ihn mit Haben minus Soll aller Buchungen der Periode (fuer ausgeglichene Buchungen immer null): Jede
Abstimmung meldete "ABGESTIMMT". Jetzt: ``domain_erp.offene_posten`` je Nebenbuch gegen 1400/1600 (SKR03).
Geprueft gegen die echte Datenbank.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.auth.deps import get_tenant_id
from app.core.database import SessionLocal, get_db
from app.finance.router import router
from testgrenze import ersetze_nutzer

pytestmark = pytest.mark.integration


@pytest.fixture
def mandant():
    from app.finance.steuerschluessel import richte_skr03_ein

    kennung = f"nb-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": kennung})
        richte_skr03_ein(db, kennung)  # Kontenrahmen SKR03 mit 1600, 8400, 1776 ...
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
            "is_active) VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{kennung}-1400", "t": kennung})
        db.commit()
    try:
        yield kennung
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                        "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                        "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                        "DELETE FROM public.nebenbuch_abstimmungen WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": kennung})
            db.commit()


@pytest.fixture
def api(mandant):
    anwendung = FastAPI()
    anwendung.include_router(router)

    def sitzung():
        with SessionLocal() as db:
            yield db

    anwendung.dependency_overrides[get_db] = sitzung
    anwendung.dependency_overrides[get_tenant_id] = lambda: mandant
    ersetze_nutzer(anwendung, "FINANCE_BEARBEITEN")
    with TestClient(anwendung) as client:
        yield client


def _op(mandant: str, typ: str, offen: str, status: str = "offen") -> None:
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.offene_posten (id, tenant_id, rechnungsnr, konto_typ, betrag, offen, op_status) "
            "VALUES (:id, :t, :nr, :typ, :offen, :offen, :status)"),
            {"id": str(uuid.uuid4()), "t": mandant, "nr": f"RE-{uuid.uuid4().hex[:6]}", "typ": typ,
             "offen": offen, "status": status})
        db.commit()


def _buche(mandant: str, soll: str, haben: str, betrag: str, storno: bool = False) -> None:
    from app.services.finance_transaction_service import FinanceTransactionService

    with SessionLocal() as db:
        dienst = FinanceTransactionService(db, mandant)
        konto = dienst.account_id_for_number
        eintrag = dienst.create(f"T-{uuid.uuid4().hex[:8]}", "Testbuchung", datetime.utcnow(), [
            {"account_id": konto(soll), "debit_amount": betrag, "credit_amount": "0"},
            {"account_id": konto(haben), "debit_amount": "0", "credit_amount": betrag},
        ], reference=f"BELEG-{uuid.uuid4().hex[:6]}")
        dienst.post(eintrag.id)
        if storno:
            dienst.reverse(eintrag.id, "Testlauf")


def _ausfuehren(client) -> dict:
    angelegt = client.post("/finance/abstimmung/nebenbuch",
                           json={"abstimmungs_datum": "2026-11-23", "buchungskreis": "DE01"})
    assert angelegt.status_code == 200, angelegt.text
    antwort = client.post(f"/finance/abstimmung/nebenbuch/{angelegt.json()['id']}/ausfuehren")
    assert antwort.status_code == 200, antwort.text
    gespeichert = client.get(f"/finance/abstimmung/nebenbuch/{angelegt.json()['id']}").json()
    assert gespeichert["status"] == antwort.json()["status"]
    return antwort.json() | {"gespeichert": gespeichert}


def test_gebuchte_forderung_und_verbindlichkeit_stimmen_ab(api, mandant):
    _op(mandant, "debitoren", "119.00")
    _op(mandant, "kreditoren", "50.00")
    _op(mandant, "debitoren", "999.00", status="storniert")  # stornierte Posten zaehlen nicht
    _buche(mandant, "1400", "8400", "119.00")
    _buche(mandant, "3400", "1600", "50.00")
    _buche(mandant, "1400", "8400", "300.00", storno=True)  # Storno hebt sich mit seinem Original auf

    ergebnis = _ausfuehren(api)

    assert ergebnis["status"] == "ABGESTIMMT"
    assert ergebnis["nebenbuch_saldo"] == ergebnis["hauptbuch_saldo"] == 69.0
    assert ergebnis["differenz"] == 0
    assert {n["nebenbuch"]: (n["sammelkonto"], n["hauptbuch_saldo"]) for n in ergebnis["nebenbuecher"]} == {
        "debitoren": ("1400", 119.0), "kreditoren": ("1600", 50.0)}
    assert ergebnis["gespeichert"]["nicht_abgestimmte"] == []


def test_offener_posten_ohne_buchung_weicht_ab(api, mandant):
    _op(mandant, "debitoren", "119.00")
    _op(mandant, "kreditoren", "40.00")
    _buche(mandant, "3400", "1600", "40.00")

    ergebnis = _ausfuehren(api)

    assert ergebnis["status"] == "ABWEICHEND"
    assert ergebnis["differenz"] == 119.0
    assert [(n["nebenbuch"], n["differenz"]) for n in ergebnis["gespeichert"]["nicht_abgestimmte"]] == [
        ("debitoren", 119.0)]


def test_abweichungen_heben_sich_nicht_auf(api, mandant):
    """+100 bei den Debitoren und +100 bei den Kreditoren waeren netto null - beide bleiben Abweichungen."""
    _op(mandant, "debitoren", "100.00")
    _op(mandant, "kreditoren", "100.00")

    ergebnis = _ausfuehren(api)

    assert ergebnis["nebenbuch_saldo"] == ergebnis["hauptbuch_saldo"] == 0
    assert ergebnis["status"] == "ABWEICHEND"
    assert ergebnis["differenz"] == 200.0


def test_ohne_kontenrahmen_wird_nicht_abgestimmt(api, mandant):
    with SessionLocal() as db:
        db.execute(text("DELETE FROM domain_shared.system_properties WHERE tenant_id = :t"), {"t": mandant})
        db.commit()
    angelegt = api.post("/finance/abstimmung/nebenbuch",
                        json={"abstimmungs_datum": "2026-11-23", "buchungskreis": "DE01"}).json()

    antwort = api.post(f"/finance/abstimmung/nebenbuch/{angelegt['id']}/ausfuehren")

    assert antwort.status_code == 409
    assert "Kontenrahmen" in antwort.json()["detail"]


def test_unbekannte_abstimmung_ist_404(api):
    assert api.post("/finance/abstimmung/nebenbuch/gibt-es-nicht/ausfuehren").status_code == 404


def test_schein_fibu_ist_entfernt():
    wurzel = Path(__file__).resolve().parents[1]
    assert not (wurzel / "app/routers/fibu_router.py").exists()
    assert not (wurzel / "app/finance/repositories.py").exists()
    assert "fibu_router" not in (wurzel / "main.py").read_text(encoding="utf-8")
