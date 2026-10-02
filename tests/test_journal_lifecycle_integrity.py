"""Actual transaction waits and retained journal chain metadata."""

import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import pytest
from sqlalchemy import text

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.services.finance_transaction_service import FinanceTransactionService
import test_journal_amount_integrity as amount_contracts

case = amount_contracts.case
store = amount_contracts.store


@pytest.mark.parametrize("second", ["post", "cancel", "update", "delete", "reverse"])
def test_competing_mutation_waits_and_refreshes_cached_state(case, second):
    db, tenant, journal, _ = case
    starting = "posted" if second == "reverse" else "draft"
    final = "reversed" if second == "reverse" else "posted"
    db.execute(
        text("UPDATE domain_erp.journal_entries SET status=:s WHERE id=:j"),
        {"s": starting, "j": journal},
    )
    db.commit()  # only this fixture's own schema, make rows visible to the peer
    first = FinanceTransactionService(db, tenant)
    first._locked_entry(journal)
    engine = db.get_bind()
    factory = type(db)
    ready = Queue()

    def peer():
        with factory(engine) as other:
            service = FinanceTransactionService(other, tenant)
            cached = service.get_by_id(journal)  # keep the old ORM identity alive
            before = cached.status
            pid = other.execute(text("SELECT pg_backend_pid()")).scalar_one()
            ready.put(pid)
            try:
                if second == "cancel":
                    service.cancel(journal, "Concurrent cancellation")
                elif second == "update":
                    service.update(journal, {"description": "Stale update"})
                else:
                    getattr(service, second)(journal)
            except ValidationFailedError:
                after = cached.status
                other.rollback()
                return before, after
            raise AssertionError("The stale mutation must be rejected")

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(peer)
        try:
            pid = ready.get(timeout=3)
            deadline = time.monotonic() + 3
            waiting = False
            with engine.connect() as observer:
                while time.monotonic() < deadline:
                    waiting = observer.execute(
                        text(
                            "SELECT EXISTS (SELECT 1 FROM pg_locks WHERE pid=:pid AND NOT granted)"
                        ),
                        {"pid": pid},
                    ).scalar_one()
                    if waiting:
                        break
                    time.sleep(0.02)
            assert waiting, "A real blocked PostgreSQL transaction is required"
            if second == "reverse":
                first.reverse(journal)
            else:
                first.post(journal)
        finally:
            db.rollback()  # release the lock on every failure path
        before, after = future.result(timeout=5)
    assert before == starting and after == final
    assert (
        db.execute(
            text("SELECT status FROM domain_erp.journal_entries WHERE id=:j"),
            {"j": journal},
        ).scalar_one()
        == final
    )
    assert db.execute(
        text("SELECT COUNT(*) FROM domain_erp.journal_entries WHERE tenant_id=:t"),
        {"t": tenant},
    ).scalar_one() == (2 if second == "reverse" else 1)


@pytest.mark.parametrize("field", ["sequence_number", "hash_current", "hash_prev"])
def test_any_existing_stamp_prevents_physical_delete(case, field):
    db, tenant, journal, _ = case
    db.execute(
        text(
            "UPDATE domain_erp.journal_entries SET sequence_number=NULL,hash_current=NULL,hash_prev=NULL WHERE id=:j"
        ),
        {"j": journal},
    )
    db.execute(
        text(f"UPDATE domain_erp.journal_entries SET {field}=:value WHERE id=:j"),
        {"j": journal, "value": 1 if field == "sequence_number" else "a" * 64},
    )
    with pytest.raises(ValidationFailedError, match="Stamped drafts"):
        FinanceTransactionService(db, tenant).delete(journal)
    assert (
        db.execute(
            text("SELECT COUNT(*) FROM domain_erp.journal_entries WHERE id=:j"),
            {"j": journal},
        ).scalar_one()
        == 1
    )
    assert (
        db.execute(
            text(
                "SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:j"
            ),
            {"j": journal},
        ).scalar_one()
        == 2
    )


def test_cancelling_draft_preserves_sequence_hash_and_lines(case):
    db, tenant, journal, _ = case
    result = FinanceTransactionService(db, tenant).cancel(journal, "Discard draft")
    assert result.status == "cancelled"
    assert result.sequence_number == 1 and result.hash_current == "a" * 64
    assert (
        db.execute(
            text(
                "SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:j"
            ),
            {"j": journal},
        ).scalar_one()
        == 2
    )


def test_unstamped_own_legacy_draft_can_be_deleted(case):
    db, tenant, journal, _ = case
    db.execute(
        text(
            "UPDATE domain_erp.journal_entries SET sequence_number=NULL,hash_current=NULL,hash_prev=NULL WHERE id=:j"
        ),
        {"j": journal},
    )
    FinanceTransactionService(db, tenant).delete(journal)
    assert (
        db.execute(
            text("SELECT COUNT(*) FROM domain_erp.journal_entries WHERE id=:j"),
            {"j": journal},
        ).scalar_one()
        == 0
    )
    assert (
        db.execute(
            text(
                "SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:j"
            ),
            {"j": journal},
        ).scalar_one()
        == 0
    )


def test_foreign_line_blocks_deleting_even_unstamped_legacy_draft(case):
    db, tenant, journal, _ = case
    db.execute(
        text(
            "UPDATE domain_erp.journal_entries SET sequence_number=NULL,hash_current=NULL,hash_prev=NULL WHERE id=:j"
        ),
        {"j": journal},
    )
    db.execute(
        text(
            "UPDATE domain_erp.journal_entry_lines SET tenant_id='foreign-proof' WHERE journal_entry_id=:j AND line_number=1"
        ),
        {"j": journal},
    )
    with pytest.raises(ValidationFailedError, match="another tenant"):
        FinanceTransactionService(db, tenant).delete(journal)
    assert (
        db.execute(
            text(
                "SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:j"
            ),
            {"j": journal},
        ).scalar_one()
        == 2
    )


def test_foreign_tenant_cannot_lock_or_mutate_header(case):
    db, _, journal, _ = case
    with pytest.raises(EntityNotFoundError):
        FinanceTransactionService(db, "foreign-proof")._locked_entry(journal)


@pytest.mark.parametrize("reference", [None, "", "   "])
def test_draft_update_cannot_erase_required_reference(case, reference):
    db, tenant, journal, _ = case
    with pytest.raises(ValidationFailedError, match="Belegprinzip"):
        FinanceTransactionService(db, tenant).update(journal, {"reference": reference})
    assert (
        db.execute(
            text("SELECT reference FROM domain_erp.journal_entries WHERE id=:j"),
            {"j": journal},
        ).scalar_one()
        == "REF"
    )


def test_unstamped_delete_handles_preloaded_line_collection(case):
    db, tenant, journal, _ = case
    db.execute(
        text(
            "UPDATE domain_erp.journal_entries SET sequence_number=NULL,hash_current=NULL,hash_prev=NULL WHERE id=:j"
        ),
        {"j": journal},
    )
    service = FinanceTransactionService(db, tenant)
    obj = service.get_by_id(journal)
    assert len(obj.lines) == 2
    service.delete(journal)
    assert (
        db.execute(
            text(
                "SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:j"
            ),
            {"j": journal},
        ).scalar_one()
        == 0
    )
