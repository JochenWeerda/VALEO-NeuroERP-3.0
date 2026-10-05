"""Canonical repository creation: no duplicate hash writer or lost input data."""

import asyncio
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.api.v1.schemas.finance import JournalEntry, JournalEntryCreate
from app.core.exceptions import ValidationFailedError
from app.infrastructure.repositories.implementations import JournalEntryRepositoryImpl
from app.services.finance_transaction_service import FinanceTransactionService
import test_journal_amount_integrity as amount_contracts

case = amount_contracts.case
store = amount_contracts.store


def payload(account="a", contra="b"):
    return {
        "entry_number": uuid4().hex[:8], "description": "Create proof", "reference": "REF",
        "entry_date": datetime(2026, 10, 5), "posting_date": datetime(2026, 10, 6),
        "currency": "USD", "source": "manual",
        "lines": [
            {"account_id": account, "debit_amount": Decimal("10.01"), "credit_amount": Decimal("0.00")},
            {"account_id": contra, "debit_amount": Decimal("0.00"), "credit_amount": Decimal("10.01")},
        ],
    }


def create(db, tenant, data):
    return asyncio.run(JournalEntryRepositoryImpl(db).create(data, tenant))


@pytest.mark.parametrize("field,value", [
    ("id", "injected"), ("status", "posted"), ("tenant_id", "foreign"),
    ("sequence_number", 99), ("hash_current", "x" * 64), ("unknown", None),
    ("total_debit", "10.02"), ("total_credit", "10.00"), ("total_debit", "NaN"),
    ("entry_date", None), ("entry_date", "2026-10-05"),
    ("posting_date", datetime(2026, 10, 4)), ("posting_date", "2026-10-06"),
    ("currency", None), ("currency", "eur"), ("currency", "EURO"), ("currency", "ÄBC"),
    ("entry_number", None), ("entry_number", " "), ("description", None),
    ("description", " "), ("reference", " "),
])
def test_invalid_headers_never_access_database_or_mutate_input(field, value):
    db = MagicMock()
    data = payload()
    data[field] = value
    before = deepcopy(data)
    with pytest.raises(ValidationFailedError):
        create(db, "tenant", data)
    assert data == before
    db.execute.assert_not_called()
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("field,value", [
    ("tax_code", "VAT19"), ("tax_amount", "0.01"), ("tax_amount", "NaN"),
    ("cost_center", "CC"), ("profit_center", "PC"), ("segment", "SEG"),
    ("id", "injected"), ("tenant_id", "foreign"), ("unknown", None),
    ("line_number", 2), ("line_number", True), ("debit", "10.01"),
])
def test_unstored_line_metadata_is_rejected_before_database_access(field, value):
    db = MagicMock()
    data = payload()
    data["lines"][0][field] = value
    before = deepcopy(data)
    with pytest.raises(ValidationFailedError):
        create(db, "tenant", data)
    assert data == before
    db.execute.assert_not_called()
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("currency", ["EUR", "USD"])
def test_real_dto_currency_posting_date_and_exact_lines_are_preserved(case, currency):
    db, tenant, _, account = case
    contra = db.execute(text(
        "SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id=:t AND id<>:a"
    ), {"t": tenant, "a": account}).scalar_one()
    data = JournalEntryCreate(**{**payload(account, contra), "currency": currency}).model_dump()
    data.update(tenant_id=tenant, total_debit=Decimal("10.01"), total_credit=Decimal("10.01"))
    before = deepcopy(data)
    service = FinanceTransactionService(db, tenant)
    repo = JournalEntryRepositoryImpl(db)
    with patch.object(repo, "_transaction_service", return_value=service), patch.object(
        service, "_stamp_gobd", wraps=service._stamp_gobd
    ) as stamp:
        entry = asyncio.run(repo.create(data, tenant))
    stamp.assert_called_once()
    assert data == before
    assert entry.currency == currency and entry.status == "draft"
    assert JournalEntry.model_validate(entry).currency == currency
    assert str(entry.posting_date)[:10] == "2026-10-06"
    assert str(entry.entry_date)[:10] == "2026-10-05"
    assert entry.sequence_number == 2 and entry.hash_prev == "a" * 64
    assert len(entry.hash_current) == 64
    assert entry.total_debit == entry.total_credit == Decimal("10.01")
    assert [line.line_number for line in entry.lines] == [1, 2]
    assert all(line.tenant_id == tenant and line.debit == line.debit_amount
               and line.credit == line.credit_amount for line in entry.lines)
    service.post(entry.id)
    _, reversal = service.reverse(entry.id)
    assert reversal.currency == currency and reversal.sequence_number == 3
    assert reversal.hash_prev == entry.hash_current
    assert reversal.total_debit == Decimal("10.01")


def test_foreign_account_prevents_new_head_and_lines(case):
    db, tenant, _, account = case
    with pytest.raises(ValidationFailedError):
        create(db, tenant, payload(account, str(uuid4())))
    assert db.execute(text("SELECT COUNT(*) FROM domain_erp.journal_entries WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 1
    assert db.execute(text("SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 2


def test_direct_service_defaults_remain_eur_and_entry_date(case):
    db, tenant, _, account = case
    contra = db.execute(text("SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id=:t AND id<>:a"), {"t": tenant, "a": account}).scalar_one()
    data = payload(account, contra)
    entry = FinanceTransactionService(db, tenant).create(
        data["entry_number"], data["description"], data["entry_date"], data["lines"], reference="REF"
    )
    assert entry.currency == "EUR" and entry.posting_date == entry.entry_date


def test_reversed_legacy_null_currency_is_not_invented_as_eur(case):
    db, tenant, journal, _ = case
    db.execute(text("UPDATE domain_erp.journal_entries SET currency=NULL,status='posted' WHERE id=:id"), {"id": journal})
    _, reversal = FinanceTransactionService(db, tenant).reverse(journal)
    assert reversal.currency is None
