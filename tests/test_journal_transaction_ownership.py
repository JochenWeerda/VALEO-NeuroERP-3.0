"""Actual commit visibility and complete rollback across journal operations."""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ValidationFailedError
from app.services.finance_transaction_service import FinanceTransactionService
import test_journal_amount_integrity as amount_contracts

case = amount_contracts.case
store = amount_contracts.store


def snapshot(db, tenant):
    return tuple(
        db.execute(text(sql), {"t": tenant}).scalars().all()
        for sql in (
            "SELECT row_to_json(j) FROM domain_erp.journal_entries j WHERE tenant_id=:t ORDER BY id",
            "SELECT row_to_json(l) FROM domain_erp.journal_entry_lines l WHERE tenant_id=:t ORDER BY id",
        )
    )


def new_entry(service, account, contra):
    return service.create(
        uuid4().hex[:8], "Outer transaction proof", datetime(2026, 10, 5),
        [
            {"account_id": account, "debit_amount": 11, "credit_amount": 0},
            {"account_id": contra, "debit_amount": 0, "credit_amount": 11},
        ],
        reference="OUTER", currency="USD",
    )


@pytest.mark.parametrize("operation", ["create", "update", "delete", "post", "cancel", "reverse"])
@pytest.mark.parametrize("finish", ["commit", "rollback"])
def test_every_mutation_is_invisible_until_outer_commit_and_fully_rollbackable(case, operation, finish):
    db, tenant, journal, account = case
    if operation == "reverse":
        db.execute(text("UPDATE domain_erp.journal_entries SET status='posted' WHERE id=:id"), {"id": journal})
    if operation == "delete":
        db.execute(text("UPDATE domain_erp.journal_entries SET sequence_number=NULL,hash_current=NULL,hash_prev=NULL WHERE id=:id"), {"id": journal})
    contra = db.execute(text("SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id=:t AND id<>:a"), {"t": tenant, "a": account}).scalar_one()
    db.commit()  # only private fixture rows; make them visible to the independent peer
    service = FinanceTransactionService(db, tenant, commit_on_success=False)
    with type(db)(db.get_bind()) as peer:
        before = snapshot(peer, tenant)
        with patch.object(db, "commit", wraps=db.commit) as commit:
            if operation == "create":
                new_entry(service, account, contra)
            elif operation == "update":
                service.update(journal, {"description": "Changed in outer transaction"})
            elif operation == "cancel":
                service.cancel(journal, "Discard proof")
            elif operation == "reverse":
                service.reverse(journal, "Reverse proof")
            else:
                getattr(service, operation)(journal)
            commit.assert_not_called()
        pending = snapshot(db, tenant)
        assert pending != before
        assert snapshot(peer, tenant) == before
        assert db.in_transaction()
        getattr(db, finish)()
        assert snapshot(peer, tenant) == (pending if finish == "commit" else before)


@pytest.mark.parametrize("finish", ["commit", "rollback"])
def test_create_post_reverse_form_one_outer_transaction(case, finish):
    db, tenant, _, account = case
    contra = db.execute(text("SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id=:t AND id<>:a"), {"t": tenant, "a": account}).scalar_one()
    db.commit()
    service = FinanceTransactionService(db, tenant, commit_on_success=False)
    with type(db)(db.get_bind()) as peer:
        before = snapshot(peer, tenant)
        with patch.object(db, "commit", wraps=db.commit) as commit:
            entry = new_entry(service, account, contra)
            service.post(entry.id)
            original, reversal = service.reverse(entry.id)
            commit.assert_not_called()
        assert original.status == "reversed" and reversal.status == "posted"
        assert reversal.currency == "USD" and reversal.sequence_number == 3
        pending = snapshot(db, tenant)
        assert len(pending[0]) == 3 and len(pending[1]) == 6
        assert snapshot(peer, tenant) == before
        getattr(db, finish)()
        assert snapshot(peer, tenant) == (pending if finish == "commit" else before)


@pytest.mark.parametrize("failure", ["domain", "database"])
def test_later_failure_rolls_back_previously_successful_create_and_post(case, failure):
    db, tenant, _, account = case
    contra = db.execute(text("SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id=:t AND id<>:a"), {"t": tenant, "a": account}).scalar_one()
    db.commit()
    service = FinanceTransactionService(db, tenant, commit_on_success=False)
    with type(db)(db.get_bind()) as peer:
        before = snapshot(peer, tenant)
        with pytest.raises(ValidationFailedError if failure == "domain" else IntegrityError):
            with db.begin():
                entry = new_entry(service, account, contra)
                service.post(entry.id)
                assert snapshot(peer, tenant) == before
                if failure == "domain":
                    service.post(entry.id)  # duplicate status transition
                else:
                    db.execute(text("INSERT INTO domain_erp.journal_entries SELECT * FROM domain_erp.journal_entries WHERE id=:id"), {"id": entry.id})
        assert snapshot(peer, tenant) == before
        assert not db.in_transaction()
