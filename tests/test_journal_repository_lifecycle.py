"""Repository consumers must use real canonical journal lifecycle guards."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import ValidationFailedError
from app.infrastructure.repositories.implementations import JournalEntryRepositoryImpl
import test_journal_amount_integrity as amount_contracts

case = amount_contracts.case
store = amount_contracts.store


def call(repo, operation, journal, tenant, data=None):
    if operation == "update":
        return asyncio.run(repo.update(journal, data or {"description": "Changed"}, tenant))
    if operation == "reverse_entry":
        return asyncio.run(repo.reverse_entry(journal, "Proof reversal", tenant))
    return asyncio.run(getattr(repo, operation)(journal, tenant))


def test_reads_use_actual_model_without_soft_delete_columns(case):
    db, tenant, journal, _ = case
    repo = JournalEntryRepositoryImpl(db)
    entry = call(repo, "get_by_id", journal, tenant)
    assert entry.id == journal and len(entry.lines) == 2
    assert call(repo, "exists", journal, tenant)
    assert asyncio.run(repo.count(tenant)) == 1
    assert asyncio.run(repo.count(tenant, status="posted")) == 0
    assert call(repo, "get_by_id", journal, str(uuid4())) is None
    assert not call(repo, "exists", journal, str(uuid4()))


@pytest.mark.parametrize("operation", ["update", "delete", "post_entry", "reverse_entry"])
def test_foreign_tenant_never_changes_journal(case, operation):
    db, _, journal, _ = case
    result = call(JournalEntryRepositoryImpl(db), operation, journal, str(uuid4()))
    assert result is None or result is False
    assert db.execute(text("SELECT status FROM domain_erp.journal_entries WHERE id=:id"),
                      {"id": journal}).scalar_one() == "draft"


@pytest.mark.parametrize("operation", ["post_entry", "reverse_entry"])
@pytest.mark.parametrize("fault", ["amount", "header", "foreign", "inactive"])
def test_repository_lifecycle_rejects_stored_contradictions(case, operation, fault):
    db, tenant, journal, account = case
    if operation == "reverse_entry":
        db.execute(text("UPDATE domain_erp.journal_entries SET status='posted' WHERE id=:id"),
                   {"id": journal})
    if fault == "amount":
        db.execute(text("UPDATE domain_erp.journal_entry_lines SET debit_amount=11 WHERE journal_entry_id=:id AND debit>0"), {"id": journal})
    elif fault == "header":
        db.execute(text("UPDATE domain_erp.journal_entries SET total_debit=11 WHERE id=:id"), {"id": journal})
    elif fault == "foreign":
        db.execute(text("UPDATE domain_erp.journal_entry_lines SET tenant_id=:tenant WHERE journal_entry_id=:id"), {"id": journal, "tenant": str(uuid4())})
    else:
        db.execute(text("UPDATE domain_erp.chart_of_accounts SET is_active=FALSE WHERE id=:id"), {"id": account})
    with pytest.raises(ValidationFailedError):
        call(JournalEntryRepositoryImpl(db), operation, journal, tenant)
    assert db.execute(text("SELECT COUNT(*) FROM domain_erp.journal_entries WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 1
    assert db.execute(text("SELECT status FROM domain_erp.journal_entries WHERE id=:id"), {"id": journal}).scalar_one() == ("posted" if operation == "reverse_entry" else "draft")


def test_post_and_reverse_persist_canonical_mirrors_and_no_second_reversal(case):
    db, tenant, journal, _ = case
    repo = JournalEntryRepositoryImpl(db)
    assert call(repo, "post_entry", journal, tenant)
    with pytest.raises(ValidationFailedError):
        call(repo, "post_entry", journal, tenant)
    reversal = call(repo, "reverse_entry", journal, tenant)
    assert reversal.status == "posted" and reversal.sequence_number == 2
    assert reversal.hash_prev == "a" * 64 and len(reversal.hash_current) == 64
    assert len(reversal.lines) == 2
    assert all(line.tenant_id == tenant and line.debit == line.debit_amount
               and line.credit == line.credit_amount for line in reversal.lines)
    original = call(repo, "get_by_id", journal, tenant)
    assert original.status == "reversed" and original.reversed_entry_id == reversal.id
    with pytest.raises(ValidationFailedError):
        call(repo, "reverse_entry", journal, tenant)
    assert asyncio.run(repo.count(tenant)) == 2


def test_delete_retains_stamped_head_and_lines(case):
    db, tenant, journal, _ = case
    with pytest.raises(ValidationFailedError, match="Stamped drafts"):
        call(JournalEntryRepositoryImpl(db), "delete", journal, tenant)
    assert db.execute(text("SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:id"), {"id": journal}).scalar_one() == 2


def test_delete_unstamped_own_draft(case):
    db, tenant, journal, _ = case
    db.execute(text("UPDATE domain_erp.journal_entries SET sequence_number=NULL,hash_current=NULL,hash_prev=NULL WHERE id=:id"), {"id": journal})
    repo = JournalEntryRepositoryImpl(db)
    assert call(repo, "delete", journal, tenant)
    assert not call(repo, "exists", journal, tenant)
    assert db.execute(text("SELECT COUNT(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:id"), {"id": journal}).scalar_one() == 0


@pytest.mark.parametrize("data", [{"status": "posted"}, {"tenant_id": "foreign"},
                                 {"entry_date": "2026-10-05"}, {"posting_date": "2026-10-05"},
                                 {"description": None}, {"description": "x" * 201},
                                 {"reference": ""}, {"reference": "x" * 51}])
def test_update_rejects_arbitrary_fields_and_nonpersistable_values(case, data):
    db, tenant, journal, _ = case
    with pytest.raises(ValidationFailedError):
        call(JournalEntryRepositoryImpl(db), "update", journal, tenant, data)
    assert call(JournalEntryRepositoryImpl(db), "get_by_id", journal, tenant).reference == "REF"


def test_update_draft_but_never_posted_entry(case):
    db, tenant, journal, _ = case
    repo = JournalEntryRepositoryImpl(db)
    assert call(repo, "update", journal, tenant).description == "Changed"
    call(repo, "post_entry", journal, tenant)
    with pytest.raises(ValidationFailedError):
        call(repo, "update", journal, tenant)


@pytest.mark.parametrize("operation", ["post_entry", "reverse_entry"])
def test_two_repository_writers_wait_and_reject_stale_cached_state(case, operation):
    db, tenant, journal, _ = case
    starting = "posted" if operation == "reverse_entry" else "draft"
    final = "reversed" if operation == "reverse_entry" else "posted"
    db.execute(text("UPDATE domain_erp.journal_entries SET status=:s WHERE id=:id"),
               {"s": starting, "id": journal})
    db.commit()  # only private schema rows; required for the peer connection
    repo = JournalEntryRepositoryImpl(db)
    repo._transaction_service(tenant)._locked_entry(journal)
    engine = db.get_bind()
    factory = type(db)
    ready = Queue()

    def peer():
        with factory(engine) as other:
            peer_repo = JournalEntryRepositoryImpl(other)
            cached = call(peer_repo, "get_by_id", journal, tenant)
            assert cached.status == starting
            ready.put(other.execute(text("SELECT pg_backend_pid()")).scalar_one())
            try:
                call(peer_repo, operation, journal, tenant)
            except ValidationFailedError:
                observed = cached.status
                other.rollback()
                return observed
            raise AssertionError("Stale repository mutation accepted")

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(peer)
        try:
            pid = ready.get(timeout=3)
            deadline = time.monotonic() + 3
            waiting = False
            with engine.connect() as observer:
                while time.monotonic() < deadline:
                    waiting = observer.execute(text(
                        "SELECT EXISTS (SELECT 1 FROM pg_locks WHERE pid=:pid AND NOT granted)"
                    ), {"pid": pid}).scalar_one()
                    if waiting:
                        break
                    time.sleep(0.02)
            assert waiting, "Actual PostgreSQL lock wait required"
            call(repo, operation, journal, tenant)
        finally:
            db.rollback()
        assert future.result(timeout=5) == final
    assert asyncio.run(repo.count(tenant)) == (2 if operation == "reverse_entry" else 1)


@pytest.mark.parametrize("operation", ["get_by_id", "get_all", "count", "exists", "post_entry", "reverse_entry", "delete", "update"])
def test_database_errors_are_never_missing_or_empty_success(operation):
    db = MagicMock()
    db.query.side_effect = SQLAlchemyError("Unavailable")
    repo = JournalEntryRepositoryImpl(db)
    with pytest.raises(SQLAlchemyError):
        if operation in ("get_all", "count"):
            asyncio.run(getattr(repo, operation)("tenant"))
        else:
            call(repo, operation, "journal", "tenant")
