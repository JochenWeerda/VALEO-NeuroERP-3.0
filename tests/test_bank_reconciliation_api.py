"""FIN-COV-002: Tests fuer bank_reconciliation.py.

Abdeckung: Pydantic-Modelle, HTTP-Smoke-Tests.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.api.v1.schemas.bank_reconciliation_schemas import (
    BalanceComparison,
    DifferenceItem,
    ReconciliationResult,
)

# ---------------------------------------------------------------------------
# Pydantic model unit tests
# ---------------------------------------------------------------------------

def test_balance_comparison_balanced():
    bc = BalanceComparison(
        bank_statement_balance=Decimal("10000.00"),
        accounting_balance=Decimal("10000.00"),
        statement_date=date(2026, 4, 30),
        comparison_date=date(2026, 5, 1),
        currency="EUR", ledger_account_id="ledger-1",
        bank_balance_state="BANK_PROVIDED", accounting_state="AVAILABLE",
    )
    assert bc.is_balanced is True
    assert bc.difference == Decimal("0.00")


def test_balance_comparison_unbalanced():
    bc = BalanceComparison(
        bank_statement_balance=Decimal("10500.00"),
        accounting_balance=Decimal("10000.00"),
        statement_date=date(2026, 4, 30),
        comparison_date=date(2026, 5, 1),
        currency="EUR", ledger_account_id="ledger-1",
        bank_balance_state="BANK_PROVIDED", accounting_state="AVAILABLE",
    )
    assert bc.is_balanced is False
    assert bc.difference == Decimal("500.00")


def test_difference_item_unmatched_statement():
    item = DifferenceItem(
        item_type="UNMATCHED_STATEMENT", statement_line_id="line-1", bank_amount=Decimal("250.00"),
        date=date(2026, 4, 28),
        amount=Decimal("250.00"),
        description="Unbekannte Buchung",
        suggested_action="INVESTIGATE",
    )
    assert item.item_type == "UNMATCHED_STATEMENT"
    assert item.suggested_action == "INVESTIGATE"
    assert item.statement_line_id == "line-1"


def test_difference_item_amount_mismatch():
    item = DifferenceItem(
        item_type="BALANCE_MISMATCH",
        date=date(2026, 4, 29),
        amount=Decimal("5.00"),
        bank_amount=Decimal("105.00"),
        accounting_amount=Decimal("100.00"),
        description="Differenz EUR 5,00",
        suggested_action="INVESTIGATE",
    )
    assert item.bank_amount == Decimal("105.00")
    assert item.accounting_amount == Decimal("100.00")


def test_reconciliation_result_structure():
    bc = BalanceComparison(
        bank_statement_balance=Decimal("0"),
        accounting_balance=Decimal("0"),
        statement_date=date(2026, 4, 30),
        comparison_date=date(2026, 5, 1),
        currency="EUR", ledger_account_id="ledger-1",
        bank_balance_state="BANK_PROVIDED", accounting_state="AVAILABLE",
    )
    result = ReconciliationResult(
        statement_id="stmt-001",
        bank_account_id="kto-001",
        balance_comparison=bc,
        differences=[],
        total_differences=0,
        line_counts={"total": 10, "matched": 10, "unmatched": 0, "partial": 0, "unknown": 0},
        can_be_booked=False,
    )
    assert result.can_be_booked is False
    assert result.total_differences == 0
    assert "booking_suggestions" not in result.model_dump()


def test_unknown_difference_type_is_rejected():
    with pytest.raises(ValidationError):
        DifferenceItem(item_type="CREATE_ENTRY", date=date(2026, 9, 28), amount=Decimal("25"), description="Invalid")


def test_contradictory_balance_difference_is_rejected():
    with pytest.raises(ValidationError):
        DifferenceItem(item_type="BALANCE_MISMATCH", date=date(2026, 9, 28), amount=Decimal("100"),
                       bank_amount=Decimal("105"), accounting_amount=Decimal("100"), description="Invalid")


def test_balanced_flag_cannot_be_supplied_instead_of_evidence():
    with pytest.raises(ValidationError):
        BalanceComparison(bank_statement_balance=Decimal("1"), accounting_balance=None,
                          bank_balance_state="BANK_PROVIDED", accounting_state="MAPPING_REQUIRED",
                          ledger_account_id=None, currency="EUR", statement_date=date(2026, 9, 28),
                          comparison_date=date(2026, 9, 28), is_balanced=True)
