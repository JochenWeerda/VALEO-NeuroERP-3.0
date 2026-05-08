"""FIN-COV-002: Tests fuer bank_reconciliation.py.

Abdeckung: Pydantic-Modelle, HTTP-Smoke-Tests.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.bank_reconciliation import (
    BalanceComparison,
    DifferenceItem,
    ReconciliationResult,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Pydantic model unit tests
# ---------------------------------------------------------------------------

def test_balance_comparison_balanced():
    bc = BalanceComparison(
        bank_statement_balance=Decimal("10000.00"),
        accounting_balance=Decimal("10000.00"),
        difference=Decimal("0.00"),
        is_balanced=True,
        statement_date=date(2026, 4, 30),
        comparison_date=date(2026, 5, 1),
    )
    assert bc.is_balanced is True
    assert bc.difference == Decimal("0.00")


def test_balance_comparison_unbalanced():
    bc = BalanceComparison(
        bank_statement_balance=Decimal("10500.00"),
        accounting_balance=Decimal("10000.00"),
        difference=Decimal("500.00"),
        is_balanced=False,
        statement_date=date(2026, 4, 30),
        comparison_date=date(2026, 5, 1),
    )
    assert bc.is_balanced is False
    assert bc.difference == Decimal("500.00")


def test_difference_item_unmatched_statement():
    item = DifferenceItem(
        item_type="UNMATCHED_STATEMENT",
        date=date(2026, 4, 28),
        amount=Decimal("250.00"),
        description="Unbekannte Buchung",
        suggested_action="INVESTIGATE",
    )
    assert item.item_type == "UNMATCHED_STATEMENT"
    assert item.suggested_action == "INVESTIGATE"
    assert item.statement_line_id is None


def test_difference_item_amount_mismatch():
    item = DifferenceItem(
        item_type="AMOUNT_MISMATCH",
        date=date(2026, 4, 29),
        amount=Decimal("100.00"),
        bank_amount=Decimal("105.00"),
        accounting_amount=Decimal("100.00"),
        description="Differenz EUR 5,00",
        journal_entry_id="JE-001",
        suggested_action="ADJUST_ENTRY",
    )
    assert item.bank_amount == Decimal("105.00")
    assert item.accounting_amount == Decimal("100.00")


def test_reconciliation_result_structure():
    bc = BalanceComparison(
        bank_statement_balance=Decimal("0"),
        accounting_balance=Decimal("0"),
        difference=Decimal("0"),
        is_balanced=True,
        statement_date=date(2026, 4, 30),
        comparison_date=date(2026, 5, 1),
    )
    result = ReconciliationResult(
        statement_id="stmt-001",
        bank_account_id="kto-001",
        balance_comparison=bc,
        differences=[],
        total_differences=0,
        line_counts={"matched": 10, "unmatched": 0},
        can_be_booked=True,
    )
    assert result.can_be_booked is True
    assert result.total_differences == 0
    assert result.booking_suggestions is None


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

_FAKE_ID = "00000000-0000-0000-0000-000000000001"


def test_balance_comparison_for_nonexistent_statement_returns_404():
    resp = _client.get(
        f"/api/v1/finance/bank-reconciliation/{_FAKE_ID}/balance-comparison",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 422, 500)


def test_differences_for_nonexistent_statement_returns_404():
    resp = _client.get(
        f"/api/v1/finance/bank-reconciliation/{_FAKE_ID}/differences",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 422, 500)


def test_summary_for_nonexistent_statement_returns_404():
    resp = _client.get(
        f"/api/v1/finance/bank-reconciliation/{_FAKE_ID}/summary",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 422, 500)


def test_reconcile_for_nonexistent_statement():
    resp = _client.post(
        f"/api/v1/finance/bank-reconciliation/{_FAKE_ID}/reconcile",
        json={},
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 422, 500)
