"""Fail-closed journal chain contracts on the existing shared PostgreSQL."""
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailedError
from app.infrastructure.models.journal import JournalEntry
from app.services.finance_transaction_service import FinanceTransactionService


def entry(tenant):
    return JournalEntry(id=str(uuid4()), tenant_id=tenant, entry_number=uuid4().hex[:20],
        entry_date=datetime(2026, 10, 2, tzinfo=timezone.utc),
        posting_date=datetime(2026, 10, 2, tzinfo=timezone.utc), description="Proof",
        total_debit=Decimal("10.00"), total_credit=Decimal("10.00"))


@pytest.fixture(scope="module")
def store():
    raw = os.getenv("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("Existing shared PostgreSQL required")
    url = make_url(raw)
    assert url.database == "valeo_probe" or "test" in url.database.lower()
    engine = create_engine(url)
    name = "journalstamp_" + uuid4().hex
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{name}"'))
        conn.execute(text(f'CREATE TABLE "{name}".journal_entries (LIKE domain_erp.journal_entries INCLUDING ALL)'))

    class OwnedSession(Session):
        def execute(self, statement, params=None, **kwargs):
            return super().execute(text(str(statement).replace("domain_erp.", f'"{name}".')), params, **kwargs)

    try:
        yield engine, OwnedSession
    finally:
        assert name.startswith("journalstamp_") and len(name) == 45
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{name}" CASCADE'))
        engine.dispose()


@pytest.fixture
def case(store):
    engine, factory = store
    tenant = str(uuid4())
    db = factory(engine)
    try:
        yield db, tenant, factory, engine
    finally:
        db.rollback()
        with factory(engine) as cleanup:
            cleanup.execute(text("DELETE FROM domain_erp.journal_entries WHERE tenant_id=:t"), {"t": tenant})
            cleanup.commit()
        db.close()


def persist(db, obj):
    db.execute(text("""INSERT INTO domain_erp.journal_entries
        (id,tenant_id,entry_number,entry_date,posting_date,description,
         total_debit,total_credit,sequence_number,hash_current,hash_prev)
        VALUES (:id,:tenant,:number,:date,:date,'Proof',10,10,:seq,:hash,:prev)"""),
        {"id": obj.id, "tenant": obj.tenant_id, "number": obj.entry_number,
         "date": obj.entry_date, "seq": obj.sequence_number,
         "hash": obj.hash_current, "prev": obj.hash_prev})


def test_first_and_successor_use_actual_previous_hash(case):
    db, tenant, _, _ = case
    service = FinanceTransactionService(db, tenant)
    first = entry(tenant)
    service._stamp_gobd(first)
    assert first.sequence_number == 1 and first.hash_prev is None
    persist(db, first)
    second = entry(tenant)
    service._stamp_gobd(second)
    assert second.sequence_number == 2 and second.hash_prev == first.hash_current
    persist(db, second)
    db.commit()


@pytest.mark.parametrize("seq,current,previous", [
    (None, None, None), (0, "a"*64, None), (-1, "a"*64, None),
    (2, "a"*64, None), (1, None, None), (1, "invalid", None),
    (1, "A"*64, None), (1, "a"*64, "b"*64),
])
def test_incomplete_existing_chain_rejects_without_partial_stamp(case, seq, current, previous):
    db, tenant, _, _ = case
    bad = entry(tenant)
    bad.sequence_number, bad.hash_current, bad.hash_prev = seq, current, previous
    persist(db, bad)
    obj = entry(tenant)
    with pytest.raises(ValidationFailedError, match="inconsistent"):
        FinanceTransactionService(db, tenant)._stamp_gobd(obj)
    assert (obj.sequence_number, obj.hash_current, obj.hash_prev) == (None, None, None)


def test_duplicate_sequence_is_rejected(case):
    db, tenant, _, _ = case
    for previous in (None, "a"*64):
        obj = entry(tenant)
        obj.sequence_number, obj.hash_current, obj.hash_prev = 1, "a"*64, previous
        persist(db, obj)
    with pytest.raises(ValidationFailedError, match="inconsistent"):
        FinanceTransactionService(db, tenant)._stamp_gobd(entry(tenant))


def test_broken_middle_link_is_rejected(case):
    db, tenant, _, _ = case
    for seq, current, previous in ((1,"a"*64,None),(2,"b"*64,"c"*64),(3,"d"*64,"b"*64)):
        obj = entry(tenant)
        obj.sequence_number, obj.hash_current, obj.hash_prev = seq,current,previous
        persist(db,obj)
    with pytest.raises(ValidationFailedError, match="inconsistent"):
        FinanceTransactionService(db,tenant)._stamp_gobd(entry(tenant))


def test_other_tenant_does_not_supply_predecessor(case):
    db, tenant, _, _ = case
    other = entry(str(uuid4()))
    other.sequence_number, other.hash_current = 1, "a"*64
    persist(db, other)
    try:
        obj = entry(tenant)
        FinanceTransactionService(db,tenant)._stamp_gobd(obj)
        assert obj.sequence_number == 1 and obj.hash_prev is None
    finally:
        db.execute(text("DELETE FROM domain_erp.journal_entries WHERE id=:id"), {"id":other.id})


def test_concurrent_writers_wait_and_use_committed_predecessor(case):
    db, tenant, factory, engine = case
    first = entry(tenant)
    FinanceTransactionService(db,tenant)._stamp_gobd(first)
    persist(db,first)
    ready = threading.Event()
    info = {}
    def worker():
        with factory(engine) as second_db:
            info["pid"] = second_db.execute(text("SELECT pg_backend_pid()")).scalar_one()
            ready.set()
            second = entry(tenant)
            FinanceTransactionService(second_db,tenant)._stamp_gobd(second)
            persist(second_db,second)
            second_db.commit()
            return second
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(worker)
        try:
            assert ready.wait(3)
            deadline = time.monotonic()+3
            waiting = False
            with engine.connect() as observer:
                while time.monotonic()<deadline:
                    waiting = observer.execute(text("SELECT EXISTS (SELECT 1 FROM pg_locks WHERE pid=:pid AND locktype='advisory' AND NOT granted)"), {"pid":info["pid"]}).scalar_one()
                    if waiting:
                        break
                    time.sleep(0.02)
            assert waiting, "Second writer must wait for the actual transaction lock"
        finally:
            db.commit()  # release even if the observation assertion failed
        second = future.result(timeout=5)
    assert second.sequence_number == 2 and second.hash_prev == first.hash_current


@pytest.mark.parametrize("operation", ["create", "reverse"])
def test_stamp_read_failure_prevents_create_and_reverse_writes(operation):
    db = MagicMock()
    db.execute.side_effect = RuntimeError("secret SQL connection detail")
    service = FinanceTransactionService(db,"tenant")
    if operation == "reverse":
        original = entry("tenant")
        original.status = "posted"
        db.query.return_value.filter.return_value.first.return_value = original
        db.query.return_value.filter.return_value.all.return_value = []
    with pytest.raises(ValidationFailedError, match="write rejected") as error:
        if operation == "create":
            service.create("TEST","Proof",datetime(2026,10,2),[],reference="REF")
        else:
            service.reverse("id")
    assert "secret" not in str(error.value)
    db.add.assert_not_called()
    db.flush.assert_not_called()
    db.commit.assert_not_called()
    if operation == "reverse":
        assert original.status == "posted"


def test_hash_failure_leaves_no_partial_stamp(monkeypatch):
    db = MagicMock()
    db.execute.return_value.fetchone.side_effect = [("read committed",),(0,None,0,0,None)]
    service = FinanceTransactionService(db,"tenant")
    def fail(*args):
        raise RuntimeError("hash failed")
    monkeypatch.setattr(service,"_compute_hash",fail)
    obj = entry("tenant")
    with pytest.raises(ValidationFailedError,match="write rejected"):
        service._stamp_gobd(obj)
    assert (obj.sequence_number,obj.hash_current,obj.hash_prev) == (None,None,None)


@pytest.mark.parametrize("kind", ["foreign", "replace"])
def test_foreign_tenant_and_replacing_existing_stamp_are_rejected(kind):
    db = MagicMock()
    obj = entry("foreign" if kind == "foreign" else "tenant")
    if kind == "replace":
        obj.sequence_number = 1
    with pytest.raises(ValidationFailedError):
        FinanceTransactionService(db,"tenant")._stamp_gobd(obj)
    db.execute.assert_not_called()


def test_repeatable_read_is_rejected_instead_of_allocating_from_old_snapshot(case):
    db,tenant,_,_ = case
    db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
    obj = entry(tenant)
    with pytest.raises(ValidationFailedError,match="READ COMMITTED"):
        FinanceTransactionService(db,tenant)._stamp_gobd(obj)
    assert obj.sequence_number is None and obj.hash_current is None
