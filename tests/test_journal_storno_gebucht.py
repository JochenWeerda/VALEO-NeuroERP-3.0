"""Ein Storno zaehlt im Journal mit seinem Original: beide gebucht, Saldo null (M3, 23.11.2026).

``FinanceTransactionService.reverse`` setzt das Original auf ``reversed`` und bucht eine Gegenbuchung ``posted``.
Beide Buchungen stehen im Journal und heben sich auf. Bis 23.11.2026 summierten Abschluss, UStVA, Bilanz/GuV,
Kontenblatt, Nebenbuch-Abstimmung, Bankabgleich und DATEV-Export nur ``status = 'posted'``: Das Original fiel
heraus, die Gegenbuchung blieb - jeder Storno erschien als negative Buchung (in der Entwicklungsdatenbank drei).
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import text

APP = Path(__file__).resolve().parents[1] / "app"
# Nur-gebucht-Filter auf Journalkoepfe (Alias ``je``) oder im Zaehler gebuchter Buchungen.
NUR_POSTED = re.compile(r"je\.status\s*=\s*'posted'|FILTER \(WHERE status = 'posted'\)")


def test_kein_journalleser_zaehlt_nur_posted():
    treffer = [
        f"{pfad.relative_to(APP.parent)}:{nr}"
        for pfad in APP.rglob("*.py")
        for nr, zeile in enumerate(pfad.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1)
        if NUR_POSTED.search(zeile)
    ]
    assert not treffer, "Journal gebucht = status IN ('posted', 'reversed'):\n" + "\n".join(treffer)


def test_ratschenmuster_trifft_den_alten_filter():
    assert NUR_POSTED.search("WHERE je.tenant_id = :t AND je.status = 'posted'")
    assert NUR_POSTED.search("SELECT COUNT(*) FILTER (WHERE status = 'posted') AS gebucht")
    assert not NUR_POSTED.search("AND je.status IN ('posted', 'reversed')")


@pytest.fixture
def storniert():
    """Ausgangsrechnung 1400 an 8400/1776 gebucht und storniert - im echten Journal eines eigenen Mandanten."""
    from app.core.database import SessionLocal
    from app.finance.steuerschluessel import richte_skr03_ein
    from app.services.finance_transaction_service import FinanceTransactionService

    mandant = f"st-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": mandant})
        richte_skr03_ein(db, mandant)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
            "is_active) VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{mandant}-1400", "t": mandant})
        db.commit()
        dienst = FinanceTransactionService(db, mandant)
        konto = dienst.account_id_for_number
        jetzt = datetime.utcnow()
        eintrag = dienst.create(f"AR-{mandant}", "Ausgangsrechnung (Test)", jetzt, [
            {"account_id": konto("1400"), "debit_amount": "119.00", "credit_amount": "0"},
            {"account_id": konto("8400"), "debit_amount": "0", "credit_amount": "100.00"},
            {"account_id": konto("1776"), "debit_amount": "0", "credit_amount": "19.00"},
        ], reference=f"RE-{mandant}", source="sales_invoice")
        dienst.post(eintrag.id)
        dienst.reverse(eintrag.id, "Testlauf")
        periode = jetzt.strftime("%Y-%m")
    try:
        yield mandant, periode
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                        "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                        "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": mandant})
            db.commit()


@pytest.mark.integration
def test_abschluss_zeigt_storno_und_original_mit_saldo_null(storniert):
    from app.core.database import SessionLocal
    from app.services.finance_closing_service import FinanceClosingService

    mandant, periode = storniert
    with SessionLocal() as db:
        ergebnis = FinanceClosingService(db, mandant).calculate(periode)

    assert ergebnis.entry_count == 2
    assert ergebnis.total_debit == ergebnis.total_credit == 238.0
    salden = {zeile["konto"]: zeile for zeile in ergebnis.account_balances}
    for konto in ("1400", "8400", "1776"):
        assert salden[konto]["saldo"] == 0, salden[konto]


@pytest.mark.integration
def test_ustva_hebt_die_stornierte_steuer_auf(storniert):
    from app.core.database import SessionLocal
    from app.finance import ustva

    mandant, periode = storniert
    with SessionLocal() as db:
        stand = ustva.berechne(db, mandant, periode)

    assert stand.gebuchte_buchungen == 2
    assert stand.umsatzsteuer == 0
    assert stand.umsatz_netto == 0
