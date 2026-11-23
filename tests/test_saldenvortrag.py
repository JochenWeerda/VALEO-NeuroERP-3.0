"""Saldenvortrag ins neue Geschaeftsjahr gegen die echte Datenbank (M3, 23.11.2026)."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.exceptions import ConflictError

pytestmark = pytest.mark.integration
JAHR = 2025


@pytest.fixture
def mandant():
    from app.finance.steuerschluessel import richte_skr03_ein

    kennung = f"sv-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": kennung})
        richte_skr03_ein(db, kennung)  # u. a. 1600, 1776, 3400, 8400, 9000, 0860, 0868
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
                        "DELETE FROM public.finance_accounting_periods WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": kennung})
            db.commit()


def _buche(mandant: str, zeilen: list[tuple[str, str, str]]) -> None:
    from app.services.finance_transaction_service import FinanceTransactionService

    with SessionLocal() as db:
        dienst = FinanceTransactionService(db, mandant)
        konto = dienst.account_id_for_number
        eintrag = dienst.create(f"T-{uuid.uuid4().hex[:8]}", "Testbuchung", datetime(JAHR, 3, 10), [
            {"account_id": konto(nr), "debit_amount": soll, "credit_amount": haben} for nr, soll, haben in zeilen
        ], reference=f"BELEG-{uuid.uuid4().hex[:6]}")
        dienst.post(eintrag.id)


def _sperre_jahr(mandant: str, ausser: str | None = None) -> None:
    with SessionLocal() as db:
        for monat in range(1, 13):
            periode = f"{JAHR}-{monat:02d}"
            if periode == ausser:
                continue
            db.execute(text(
                "INSERT INTO public.finance_accounting_periods (id, tenant_id, period, status, start_date, end_date) "
                "VALUES (:id, :t, :p, 'CLOSED', :s, :s)"),
                {"id": str(uuid.uuid4()), "t": mandant, "p": periode, "s": datetime(JAHR, monat, 1).date()})
        db.commit()


def _vortrag(mandant: str):
    from app.services.finance_saldenvortrag_service import trage_salden_vor

    with SessionLocal() as db:
        return trage_salden_vor(db, mandant, JAHR, actor=None)


def _eroeffnung(mandant: str) -> dict[str, Decimal]:
    with SessionLocal() as db:
        zeilen = db.execute(text(
            "SELECT coa.account_number, SUM(jel.debit_amount - jel.credit_amount) FROM domain_erp.journal_entry_lines jel "
            "JOIN domain_erp.journal_entries je ON je.id = jel.journal_entry_id "
            "JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id "
            "WHERE je.tenant_id = :t AND je.source = 'saldenvortrag' AND je.period = :p AND je.status = 'posted' "
            "GROUP BY coa.account_number"), {"t": mandant, "p": f"{JAHR + 1}-01"}).fetchall()
    return {nr: Decimal(str(s)) for nr, s in zeilen}


def test_bestandskonten_und_gewinn_werden_vorgetragen(mandant):
    _buche(mandant, [("1400", "119.00", "0"), ("8400", "0", "100.00"), ("1776", "0", "19.00")])
    _buche(mandant, [("3400", "50.00", "0"), ("1600", "0", "50.00")])
    _sperre_jahr(mandant)

    ergebnis = _vortrag(mandant)

    assert ergebnis.jahresergebnis == Decimal("50.00")
    assert _eroeffnung(mandant) == {"1400": Decimal("119.00"), "1600": Decimal("-50.00"),
                                    "1776": Decimal("-19.00"), "0860": Decimal("-50.00")}


def test_verlust_geht_auf_den_verlustvortrag(mandant):
    _buche(mandant, [("3400", "80.00", "0"), ("1600", "0", "80.00")])
    _sperre_jahr(mandant)

    ergebnis = _vortrag(mandant)

    assert ergebnis.jahresergebnis == Decimal("-80.00")
    assert _eroeffnung(mandant) == {"1600": Decimal("-80.00"), "0868": Decimal("80.00")}


def test_ohne_abgeschlossene_perioden_kein_vortrag(mandant):
    _buche(mandant, [("1400", "119.00", "0"), ("8400", "0", "100.00"), ("1776", "0", "19.00")])
    _sperre_jahr(mandant, ausser=f"{JAHR}-12")

    with pytest.raises(ConflictError, match=f"offen: {JAHR}-12"):
        _vortrag(mandant)
    assert _eroeffnung(mandant) == {}


def test_ein_jahr_wird_nur_einmal_vorgetragen(mandant):
    _buche(mandant, [("1400", "119.00", "0"), ("8400", "0", "100.00"), ("1776", "0", "19.00")])
    _sperre_jahr(mandant)
    _vortrag(mandant)

    with pytest.raises(ConflictError, match="bereits gebucht"):
        _vortrag(mandant)


def test_rest_weg_bucht_den_vortrag(mandant):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.api.v1.endpoints import finance_actions
    from app.core.database import get_db
    from app.core.exceptions import register_domain_exception_handlers
    from testgrenze import ersetze_mandant, ersetze_nutzer

    _buche(mandant, [("1400", "119.00", "0"), ("8400", "0", "100.00"), ("1776", "0", "19.00")])
    _sperre_jahr(mandant)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(finance_actions.router, prefix="/finance")

    def sitzung():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = sitzung
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "FINANCE_ADMIN")
    with TestClient(app) as client:
        erste = client.post("/finance/closing/saldenvortrag", json={"jahr": JAHR})
        zweite = client.post("/finance/closing/saldenvortrag", json={"jahr": JAHR})

    assert erste.status_code == 201, erste.text
    assert erste.json()["jahresergebnis"] == 100.0
    assert zweite.status_code == 409
