"""Mandatory booking periods and real concurrent close/booking waits."""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from queue import Queue
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.core import finance_periods
from app.core.exceptions import ValidationFailedError
from app.api.v1.endpoints import accounting_periods
from app.services.finance_period_service import FinancePeriodService, period_bounds
from app.services.finance_transaction_service import FinanceTransactionService
import test_journal_amount_integrity as amount_contracts

case = amount_contracts.case
store = amount_contracts.store


def set_period(db, tenant, period, status):
    start, end = period_bounds(period)
    db.execute(text("""INSERT INTO public.finance_accounting_periods
        (id,tenant_id,period,status,start_date,end_date)
        VALUES (:id,:t,:p,:s,:start,:end)"""),
        {"id": str(uuid4()), "t": tenant, "p": period, "s": status, "start": start, "end": end})


def create(service, db, tenant, account, **extra):
    contra = db.execute(text("SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id=:t AND id<>:a"), {"t": tenant, "a": account}).scalar_one()
    return service.create(uuid4().hex[:8], "Period proof", datetime(2026, 10, 5),
        [{"account_id": account, "debit_amount": 10, "credit_amount": 0},
         {"account_id": contra, "debit_amount": 0, "credit_amount": 10}], reference="REF", **extra)


@pytest.mark.parametrize("operation", ["create", "post", "reverse"])
@pytest.mark.parametrize("state", [None, "OPEN", "ADJUSTING", "CLOSED"])
def test_target_period_is_mandatory_without_explicit_period_argument(case, operation, state):
    db, tenant, journal, account = case
    period = datetime.utcnow().strftime("%Y-%m") if operation == "reverse" else "2026-10"
    if operation == "reverse":
        db.execute(text("UPDATE domain_erp.journal_entries SET status='posted' WHERE id=:id"), {"id": journal})
    if state:
        set_period(db, tenant, period, state)
    service = FinanceTransactionService(db, tenant)
    def mutate():
        return create(service, db, tenant, account) if operation == "create" else getattr(service, operation)(journal)
    if state == "CLOSED":
        with pytest.raises(ValidationFailedError, match="CLOSED"):
            mutate()
        assert db.execute(text("SELECT COUNT(*) FROM domain_erp.journal_entries WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 1
    else:
        mutate()


def test_create_and_post_use_posting_month_not_entry_month(case):
    db, tenant, journal, account = case
    set_period(db, tenant, "2026-11", "CLOSED")
    with pytest.raises(ValidationFailedError, match="2026-11"):
        create(FinanceTransactionService(db, tenant), db, tenant, account, posting_date=datetime(2026, 11, 1))
    db.execute(text("UPDATE domain_erp.journal_entries SET posting_date='2026-11-01' WHERE id=:id"), {"id": journal})
    with pytest.raises(ValidationFailedError, match="2026-11"):
        FinanceTransactionService(db, tenant).post(journal)


def test_foreign_closed_period_never_blocks_own_journal(case):
    db, tenant, journal, _ = case
    set_period(db, str(uuid4()), "2026-10", "CLOSED")
    assert FinanceTransactionService(db, tenant).post(journal).status == "posted"


@pytest.mark.parametrize("period", [None, "", "2026-00", "2026-13", "0000-01", "2026-1", "garbage"])
def test_no_missing_or_malformed_period_can_bypass_guard(period):
    db = MagicMock()
    with pytest.raises(ValidationFailedError):
        FinanceTransactionService(db, "tenant").check_period_open(period)
    db.execute.assert_not_called()


def test_explicit_period_must_match_posting_date_before_database_access():
    db = MagicMock()
    with pytest.raises(ValidationFailedError, match="differs"):
        FinanceTransactionService(db, "tenant").create("JE", "Proof", datetime(2026, 10, 5),
            [{"account_id": "a", "debit_amount": 10, "credit_amount": 0},
             {"account_id": "b", "debit_amount": 0, "credit_amount": 10}],
            reference="REF", period="2026-11")
    db.execute.assert_not_called()


@pytest.mark.parametrize("status", ["UNKNOWN", None])
def test_unknown_status_and_stale_snapshot_isolation_fail_closed(status):
    db = MagicMock()
    db.execute.return_value.scalar_one.return_value = "read committed"
    db.execute.return_value.fetchone.return_value = (status,)
    with pytest.raises(ValidationFailedError, match="UNKNOWN"):
        FinanceTransactionService(db, "tenant").check_period_open("2026-10")
    db.execute.return_value.scalar_one.return_value = "repeatable read"
    with pytest.raises(ValidationFailedError, match="not feststellbar|nicht feststellbar"):
        FinanceTransactionService(db, "tenant").check_period_open("2026-10")


def wait_for_lock(engine, pid):
    deadline = time.monotonic() + 3
    with engine.connect() as observer:
        while time.monotonic() < deadline:
            if observer.execute(text("SELECT EXISTS (SELECT 1 FROM pg_locks WHERE pid=:pid AND NOT granted)"), {"pid": pid}).scalar_one():
                return
            time.sleep(0.02)
    raise AssertionError("Actual blocked PostgreSQL transaction required")


def test_waiting_booking_reads_newly_closed_state(case):
    db, tenant, journal, _ = case
    set_period(db, tenant, "2026-10", "OPEN")
    db.commit()
    finance_periods.sperre_periode(db, tenant, "2026-10", exklusiv=True)
    db.execute(text("UPDATE public.finance_accounting_periods SET status='CLOSED' WHERE tenant_id=:t AND period='2026-10'"), {"t": tenant})
    ready = Queue()
    engine = db.get_bind()
    def peer():
        with type(db)(engine) as other:
            ready.put(other.execute(text("SELECT pg_backend_pid()")).scalar_one())
            with pytest.raises(ValidationFailedError, match="CLOSED"):
                FinanceTransactionService(other, tenant).post(journal)
            other.rollback()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(peer)
        try:
            wait_for_lock(engine, ready.get(timeout=3))
            db.commit()
        finally:
            db.rollback()
        future.result(timeout=5)
    assert db.execute(text("SELECT status FROM domain_erp.journal_entries WHERE id=:id"), {"id": journal}).scalar_one() == "draft"


def test_first_close_of_absent_period_waits_for_journal_commit(case):
    db, tenant, journal, _ = case
    db.commit()
    FinanceTransactionService(db, tenant, commit_on_success=False).post(journal)
    ready = Queue()
    engine = db.get_bind()
    def peer():
        with type(db)(engine) as other:
            ready.put(other.execute(text("SELECT pg_backend_pid()")).scalar_one())
            closing = FinancePeriodService(other, tenant)
            with patch.object(closing, "_period_metrics", return_value={"offen_count": 0, "storno_inkonsistent": 0}):
                return closing.close_period("2026-10")
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(peer)
        try:
            wait_for_lock(engine, ready.get(timeout=3))
            assert db.execute(text("SELECT COUNT(*) FROM public.finance_accounting_periods WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 0
            db.commit()
        finally:
            db.rollback()
        assert future.result(timeout=5)["status"] == "CLOSED"
    with pytest.raises(ValidationFailedError, match="CLOSED"):
        FinanceTransactionService(db, tenant).check_period_open("2026-10")


def test_missing_period_table_fails_closed_without_shared_schema_changes(case):
    db, tenant, _, _ = case
    db.execute(text("ALTER TABLE public.finance_accounting_periods RENAME TO period_missing"))
    with pytest.raises(ValidationFailedError, match="nicht feststellbar"):
        FinanceTransactionService(db, tenant).check_period_open("2026-10")
    db.rollback()  # restores only this fixture's renamed private table


@pytest.mark.parametrize("operation", ["create", "update"])
def test_accounting_period_api_writer_waits_for_journal_reader(case, operation):
    db, tenant, _, _ = case
    if operation == "update":
        set_period(db, tenant, "2026-10", "OPEN")
    db.commit()
    period_id = db.execute(text("SELECT id FROM public.finance_accounting_periods WHERE tenant_id=:t"), {"t": tenant}).scalar() if operation == "update" else None
    FinanceTransactionService(db, tenant).check_period_open("2026-10")
    ready = Queue()
    engine = db.get_bind()
    def peer():
        with type(db)(engine) as other:
            ready.put(other.execute(text("SELECT pg_backend_pid()")).scalar_one())
            with patch.object(accounting_periods, "log_fibu_audit"):
                if operation == "create":
                    start, end = period_bounds("2026-10")
                    return asyncio.run(accounting_periods.create_period(
                        accounting_periods.PeriodCreate(tenant_id=tenant, period="2026-10", status="CLOSED", start_date=start, end_date=end),
                        request=None, tenant_id=tenant, db=other))
                return asyncio.run(accounting_periods.update_period(
                    period_id, accounting_periods.PeriodUpdate(status="CLOSED"),
                    request=None, tenant_id=tenant, db=other))
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(peer)
        try:
            wait_for_lock(engine, ready.get(timeout=3))
        finally:
            db.rollback()
        assert future.result(timeout=5).status == "CLOSED"
    with pytest.raises(ValidationFailedError, match="CLOSED"):
        FinanceTransactionService(db, tenant).check_period_open("2026-10")
