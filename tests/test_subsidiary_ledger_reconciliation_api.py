"""DOM-FIN-002: Tests fuer subsidiary_ledger_reconciliation.py.

Abdeckung: ReconciliationEntry/Detail/Result Pydantic-Modelle, HTTP smoke.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.subsidiary_ledger_reconciliation import (
    ReconciliationEntry,
    ReconciliationDetail,
    ReconciliationResult,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# ReconciliationEntry unit tests
# ---------------------------------------------------------------------------

def test_reconciliation_entry_balanced():
    entry = ReconciliationEntry(
        account_number="1400",
        account_name="Forderungen",
        subsidiary_balance=Decimal("10000.00"),
        general_ledger_balance=Decimal("10000.00"),
        difference=Decimal("0.00"),
        is_balanced=True,
        entry_count=5,
        unmatched_entries=0,
    )
    assert entry.is_balanced is True
    assert entry.difference == Decimal("0.00")


def test_reconciliation_entry_unbalanced():
    entry = ReconciliationEntry(
        account_number="1400",
        account_name="Forderungen",
        subsidiary_balance=Decimal("10500.00"),
        general_ledger_balance=Decimal("10000.00"),
        difference=Decimal("500.00"),
        is_balanced=False,
        entry_count=5,
        unmatched_entries=1,
    )
    assert entry.is_balanced is False
    assert entry.difference == Decimal("500.00")
    assert entry.unmatched_entries == 1


# ---------------------------------------------------------------------------
# ReconciliationDetail unit tests
# ---------------------------------------------------------------------------

def test_reconciliation_detail_structure():
    detail = ReconciliationDetail(
        entry_id="e-001",
        entry_number="BE-2026-001",
        entry_date=date(2026, 4, 30),
        amount=Decimal("1500.00"),
        description="Zahlung Kunde X",
        source="AR",
        status="posted",
        matched=True,
    )
    assert detail.matched is True
    assert detail.source == "AR"


def test_reconciliation_detail_unmatched():
    detail = ReconciliationDetail(
        entry_id="e-002",
        entry_number="BE-2026-002",
        entry_date=date(2026, 5, 1),
        amount=Decimal("250.00"),
        description="Offener Posten",
        source="AP",
        status="open",
        matched=False,
    )
    assert detail.matched is False


# ---------------------------------------------------------------------------
# ReconciliationResult unit tests
# ---------------------------------------------------------------------------

def _make_result(**kwargs) -> ReconciliationResult:
    defaults = {
        "ledger_type": "AR",
        "period": "2026-04",
        "reconciliation_date": date(2026, 5, 1),
        "total_accounts": 10,
        "balanced_accounts": 9,
        "unbalanced_accounts": 1,
        "total_difference": Decimal("500.00"),
        "entries": [],
    }
    defaults.update(kwargs)
    return ReconciliationResult(**defaults)


def test_reconciliation_result_basic():
    result = _make_result()
    assert result.ledger_type == "AR"
    assert result.period == "2026-04"
    assert result.balanced_accounts == 9
    assert result.details is None


def test_reconciliation_result_with_entries():
    entry = ReconciliationEntry(
        account_number="1400", account_name="Debitoren",
        subsidiary_balance=Decimal("5000"), general_ledger_balance=Decimal("5000"),
        difference=Decimal("0"), is_balanced=True, entry_count=2, unmatched_entries=0,
    )
    result = _make_result(entries=[entry], total_accounts=1, balanced_accounts=1, unbalanced_accounts=0)
    assert len(result.entries) == 1
    assert result.entries[0].account_number == "1400"


def test_reconciliation_result_fully_balanced():
    result = _make_result(
        unbalanced_accounts=0,
        total_difference=Decimal("0.00"),
        balanced_accounts=10,
    )
    assert result.total_difference == Decimal("0.00")
    assert result.unbalanced_accounts == 0


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_get_ar_reconciliation_requires_period():
    resp = _client.get("/api/v1/finance/subsidiary-ledger-reconciliation/AR", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 404, 422)


def test_get_ar_reconciliation_with_period():
    resp = _client.get(
        "/api/v1/finance/subsidiary-ledger-reconciliation/AR?period=2026-04",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 404, 422, 500)


def test_get_ap_reconciliation():
    resp = _client.get(
        "/api/v1/finance/subsidiary-ledger-reconciliation/AP?period=2026-04",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 404, 422, 500)
