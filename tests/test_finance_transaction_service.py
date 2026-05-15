"""Unit tests for FinanceTransactionService — no real DB required."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, call, patch

import pytest

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.services.finance_transaction_service import FinanceTransactionService


# ── fixtures ──────────────────────────────────────────────────────────────────

TENANT = "tenant-test"
NOW = datetime(2026, 1, 15, 10, 0, 0)

BALANCED_LINES = [
    {"account_id": "1000", "debit_amount": 100, "credit_amount": 0},
    {"account_id": "4000", "debit_amount": 0, "credit_amount": 100},
]

UNBALANCED_LINES = [
    {"account_id": "1000", "debit_amount": 100, "credit_amount": 0},
    {"account_id": "4000", "debit_amount": 0, "credit_amount": 90},
]


def _make_service(db=None):
    if db is None:
        db = MagicMock()
        # sequence + prev-hash queries return safe defaults
        db.execute.return_value.fetchone.return_value = (1,)
    return FinanceTransactionService(db, TENANT)


def _make_entry(status="draft", entry_id="e-001"):
    entry = MagicMock()
    entry.id = entry_id
    entry.tenant_id = TENANT
    entry.status = status
    entry.entry_number = "BU-2026-001"
    entry.description = "Test"
    entry.reference = "REF-001"
    entry.entry_date = NOW
    entry.total_debit = Decimal("100")
    entry.total_credit = Decimal("100")
    entry.sequence_number = 1
    entry.hash_current = None
    entry.hash_prev = None
    entry.document_type = None
    entry.reversed_entry_id = None
    return entry


# ── validate_balanced ─────────────────────────────────────────────────────────

def test_validate_balanced_ok():
    svc = _make_service()
    svc.validate_balanced(BALANCED_LINES)  # no exception


def test_validate_balanced_raises():
    svc = _make_service()
    with pytest.raises(ValidationFailedError, match="not balanced"):
        svc.validate_balanced(UNBALANCED_LINES)


# ── validate_status_transition ────────────────────────────────────────────────

@pytest.mark.parametrize("current,target", [
    ("draft", "posted"),
    ("draft", "cancelled"),
    ("posted", "reversed"),
])
def test_valid_transitions(current, target):
    svc = _make_service()
    svc.validate_status_transition(current, target)  # no exception


@pytest.mark.parametrize("current,target", [
    ("posted", "draft"),
    ("cancelled", "posted"),
    ("reversed", "posted"),
    ("draft", "reversed"),
])
def test_invalid_transitions(current, target):
    svc = _make_service()
    with pytest.raises(ValidationFailedError):
        svc.validate_status_transition(current, target)


# ── check_period_open ─────────────────────────────────────────────────────────

def test_period_open_no_row():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    svc = FinanceTransactionService(db, TENANT)
    svc.check_period_open("2026-01")  # no exception — no row means allow through


def test_period_open_open():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = ("OPEN",)
    svc = FinanceTransactionService(db, TENANT)
    svc.check_period_open("2026-01")  # no exception


def test_period_closed_raises():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = ("CLOSED",)
    svc = FinanceTransactionService(db, TENANT)
    with pytest.raises(ValidationFailedError, match="CLOSED"):
        svc.check_period_open("2026-01")


def test_period_none_skipped():
    svc = _make_service()
    svc.check_period_open(None)  # no exception


# ── get_by_id ─────────────────────────────────────────────────────────────────

def test_get_by_id_found():
    entry = _make_entry()
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    result = svc.get_by_id("e-001")
    assert result is entry


def test_get_by_id_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    svc = FinanceTransactionService(db, TENANT)
    with pytest.raises(EntityNotFoundError):
        svc.get_by_id("missing")


# ── list_paginated ────────────────────────────────────────────────────────────

def test_list_paginated_returns_tuple():
    entry = _make_entry()
    db = MagicMock()
    q = MagicMock()
    db.query.return_value.filter.return_value = q
    q.filter.return_value = q
    q.count.return_value = 1
    q.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [entry]
    svc = FinanceTransactionService(db, TENANT)
    items, total = svc.list_paginated()
    assert total == 1
    assert items == [entry]


# ── create ────────────────────────────────────────────────────────────────────

def test_create_missing_reference_raises():
    svc = _make_service()
    with pytest.raises(ValidationFailedError, match="Belegprinzip"):
        svc.create("BU-001", "desc", NOW, BALANCED_LINES, reference="")


def test_create_unbalanced_raises():
    svc = _make_service()
    with pytest.raises(ValidationFailedError, match="not balanced"):
        svc.create("BU-001", "desc", NOW, UNBALANCED_LINES, reference="REF-001")


def test_create_persists_entry_and_lines():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = (1,)
    added = []
    db.add.side_effect = lambda obj: added.append(obj)

    svc = FinanceTransactionService(db, TENANT)
    with patch("app.services.finance_transaction_service.JournalEntry") as MockEntry, \
         patch("app.services.finance_transaction_service.JournalEntryLine") as MockLine:
        mock_entry = MagicMock()
        mock_entry.id = "new-id"
        mock_entry.sequence_number = None
        mock_entry.hash_current = None
        MockEntry.return_value = mock_entry

        svc.create("BU-001", "desc", NOW, BALANCED_LINES, reference="REF-001")

    # entry + 2 lines added
    assert db.add.call_count == 3
    db.flush.assert_called_once()
    db.commit.assert_called_once()


# ── update ────────────────────────────────────────────────────────────────────

def test_update_draft_ok():
    entry = _make_entry(status="draft")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    svc.update("e-001", {"description": "new desc"})
    assert entry.description == "new desc"
    db.commit.assert_called_once()


def test_update_posted_raises():
    entry = _make_entry(status="posted")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    with pytest.raises(ValidationFailedError, match="Entwürf"):
        svc.update("e-001", {"description": "x"})


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_draft_ok():
    entry = _make_entry(status="draft")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    db.query.return_value.filter.return_value.delete.return_value = None
    svc = FinanceTransactionService(db, TENANT)
    svc.delete("e-001")
    db.delete.assert_called_once_with(entry)
    db.commit.assert_called_once()


def test_delete_posted_raises():
    entry = _make_entry(status="posted")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    with pytest.raises(ValidationFailedError, match="Entwürf"):
        svc.delete("e-001")


# ── post ──────────────────────────────────────────────────────────────────────

def test_post_draft_entry():
    entry = _make_entry(status="draft")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    svc.post("e-001", posted_by="user-1")
    assert entry.status == "posted"
    assert entry.posted_by == "user-1"
    db.commit.assert_called_once()


def test_post_already_posted_raises():
    entry = _make_entry(status="posted")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    with pytest.raises(ValidationFailedError):
        svc.post("e-001")


# ── cancel ────────────────────────────────────────────────────────────────────

def test_cancel_draft_ok():
    entry = _make_entry(status="draft")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    svc.cancel("e-001", reason="Fehleingabe")
    assert entry.status == "cancelled"


# ── reverse ───────────────────────────────────────────────────────────────────

def test_reverse_posted_creates_reversal():
    original = _make_entry(status="posted", entry_id="e-orig")
    original.entry_number = "BU-001"
    original.description = "Buchung"

    line = MagicMock()
    line.account_id = "1000"
    line.debit = Decimal("100")
    line.credit = Decimal("0")
    line.description = "Kasse"

    db = MagicMock()
    # get_by_id
    db.query.return_value.filter.return_value.first.return_value = original
    # lines query
    db.query.return_value.filter.return_value.all.return_value = [line]
    db.execute.return_value.fetchone.return_value = (2,)

    added = []
    db.add.side_effect = lambda obj: added.append(obj)

    svc = FinanceTransactionService(db, TENANT)
    with patch("app.services.finance_transaction_service.JournalEntry") as MockEntry, \
         patch("app.services.finance_transaction_service.JournalEntryLine") as MockLine:
        mock_reversal = MagicMock()
        mock_reversal.id = "e-rev"
        mock_reversal.sequence_number = None
        mock_reversal.hash_current = None
        MockEntry.return_value = mock_reversal

        orig_out, rev_out = svc.reverse("e-orig", reason="Test-Storno")

    assert original.status == "reversed"
    db.commit.assert_called_once()


def test_reverse_draft_raises():
    entry = _make_entry(status="draft")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = entry
    svc = FinanceTransactionService(db, TENANT)
    with pytest.raises(ValidationFailedError):
        svc.reverse("e-001")


# ── GoBD hash chain ──────────────────────────────────────────────────────────

def test_compute_hash_deterministic():
    entry = _make_entry()
    entry.sequence_number = 42
    h1 = FinanceTransactionService._compute_hash(entry, "prev-hash")
    h2 = FinanceTransactionService._compute_hash(entry, "prev-hash")
    assert h1 == h2
    assert len(h1) == 64


def test_compute_hash_changes_with_prev():
    entry = _make_entry()
    entry.sequence_number = 1
    h1 = FinanceTransactionService._compute_hash(entry, None)
    h2 = FinanceTransactionService._compute_hash(entry, "some-prev")
    assert h1 != h2
