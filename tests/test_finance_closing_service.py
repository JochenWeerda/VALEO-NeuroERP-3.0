"""FIN-ABSCHLUSS-STUBS-001 — Tests für FinanceClosingService."""
from __future__ import annotations

from unittest.mock import MagicMock, patch, call
import pytest

from app.services.finance_closing_service import (
    FinanceClosingService,
    ClosingError,
    ClosingCalculateResult,
    ClosingLockResult,
    ClosingRunResult,
)


TENANT = "test-tenant-fin-001"


def _db_with_journal(entry_count=3, total_debit=10000.0, total_credit=9500.0, accounts=None):
    """Erzeugt eine Mock-DB-Session, die journal_entries-Summen zurückgibt."""
    db = MagicMock()
    summary_row = MagicMock()
    summary_row.__getitem__ = lambda self, i: [entry_count, total_debit, total_credit][i]
    summary_result = MagicMock()
    summary_result.first.return_value = summary_row

    account_rows = accounts or []
    account_result = MagicMock()
    account_result.mappings.return_value.all.return_value = account_rows

    db.execute.side_effect = [summary_result, account_result]
    return db


# ── calculate ─────────────────────────────────────────────────────────────────

class TestCalculate:
    def test_returns_correct_sums(self):
        db = _db_with_journal(entry_count=5, total_debit=20000.0, total_credit=18000.0)
        svc = FinanceClosingService(db, TENANT)
        result = svc.calculate("2025-01")
        assert isinstance(result, ClosingCalculateResult)
        assert result.entry_count == 5
        assert result.total_debit == pytest.approx(20000.0)
        assert result.total_credit == pytest.approx(18000.0)
        assert result.balance == pytest.approx(2000.0)
        assert result.status == "calculated"

    def test_raises_on_none_row(self):
        db = MagicMock()
        res = MagicMock()
        res.first.return_value = None
        db.execute.return_value = res
        svc = FinanceClosingService(db, TENANT)
        with pytest.raises(ClosingError, match="Keine Buchungsdaten"):
            svc.calculate("2025-01")

    def test_zero_entries_returns_zero_balance(self):
        db = _db_with_journal(entry_count=0, total_debit=0.0, total_credit=0.0)
        svc = FinanceClosingService(db, TENANT)
        result = svc.calculate("2025-02")
        assert result.entry_count == 0
        assert result.balance == 0.0

    def test_period_passed_to_query(self):
        db = _db_with_journal()
        svc = FinanceClosingService(db, TENANT)
        svc.calculate("2024-12")
        first_call_params = db.execute.call_args_list[0][0][1]
        assert first_call_params["period"] == "2024-12"
        assert first_call_params["tid"] == TENANT

    def test_closing_type_preserved(self):
        db = _db_with_journal()
        svc = FinanceClosingService(db, TENANT)
        result = svc.calculate("2025-12", closing_type="annual")
        assert result.closing_type == "annual"

    def test_account_balances_returned(self):
        account_row = MagicMock()
        account_row.__getitem__ = lambda self, k: {
            "konto": "1600", "bezeichnung": "Bankguthaben",
            "soll": 5000.0, "haben": 3000.0,
        }[k]
        account_row.__class__ = dict  # make it iterable-like
        # Use real dict for simplicity
        db = MagicMock()
        summary_row = MagicMock()
        summary_row.__getitem__ = lambda self, i: [2, 5000.0, 3000.0][i]
        summary_result = MagicMock()
        summary_result.first.return_value = summary_row
        account_result = MagicMock()
        account_result.mappings.return_value.all.return_value = [
            {"konto": "1600", "bezeichnung": "Bankguthaben", "soll": 5000.0, "haben": 3000.0}
        ]
        db.execute.side_effect = [summary_result, account_result]
        svc = FinanceClosingService(db, TENANT)
        result = svc.calculate("2025-01")
        assert len(result.account_balances) == 1
        assert result.account_balances[0]["konto"] == "1600"
        assert result.account_balances[0]["saldo"] == pytest.approx(2000.0)


# ── lock ──────────────────────────────────────────────────────────────────────

class TestLock:
    def _svc_with_period_svc(self, period_svc_mock):
        db = MagicMock()
        svc = FinanceClosingService(db, TENANT)
        svc._period_svc = period_svc_mock
        return svc

    def test_lock_calls_period_svc(self):
        period_svc = MagicMock()
        period_svc.close_period.return_value = {"ok": True, "status": "closed"}
        svc = self._svc_with_period_svc(period_svc)
        result = svc.lock("2025-01", actor="buchhalter")
        period_svc.close_period.assert_called_once_with("2025-01", bediener="buchhalter", force=False)
        assert isinstance(result, ClosingLockResult)
        assert result.status == "closed"

    def test_lock_raises_on_already_locked(self):
        from app.services.finance_period_service import PeriodError
        period_svc = MagicMock()
        period_svc.close_period.side_effect = PeriodError("Periode 2025-01 ist bereits abgeschlossen.")
        svc = self._svc_with_period_svc(period_svc)
        with pytest.raises(ClosingError, match="bereits abgeschlossen"):
            svc.lock("2025-01")

    def test_lock_raises_on_blocker(self):
        from app.services.finance_period_service import PeriodError
        period_svc = MagicMock()
        period_svc.close_period.side_effect = PeriodError("3 offene Posten in der Periode")
        svc = self._svc_with_period_svc(period_svc)
        with pytest.raises(ClosingError, match="offene Posten"):
            svc.lock("2025-01")

    def test_lock_force_bypasses_blocker(self):
        period_svc = MagicMock()
        period_svc.close_period.return_value = {"ok": True, "status": "closed", "erzwungen": True}
        svc = self._svc_with_period_svc(period_svc)
        result = svc.lock("2025-01", actor="admin", force=True)
        period_svc.close_period.assert_called_once_with("2025-01", bediener="admin", force=True)
        assert result.status == "closed"


# ── run ───────────────────────────────────────────────────────────────────────

class TestRun:
    def _svc(self, calc_result=None, lock_result=None):
        db = MagicMock()
        db.execute.return_value = MagicMock()
        db.flush.return_value = None
        db.commit.return_value = None
        svc = FinanceClosingService(db, TENANT)
        calc_result = calc_result or ClosingCalculateResult(
            period="2025-01", closing_type="monthly",
            entry_count=10, total_debit=50000.0, total_credit=50000.0, balance=0.0,
        )
        lock_result = lock_result or ClosingLockResult(
            period="2025-01", status="closed", message="Periode gesperrt.",
        )
        svc.calculate = MagicMock(return_value=calc_result)
        svc.lock = MagicMock(return_value=lock_result)
        return svc

    def test_run_returns_result(self):
        svc = self._svc()
        result = svc.run("2025-01", closing_type="monthly", actor="admin")
        assert isinstance(result, ClosingRunResult)
        assert result.period == "2025-01"
        assert result.status == "closed"
        assert "2025-01" in result.message

    def test_run_calls_calculate_and_lock(self):
        svc = self._svc()
        svc.run("2025-01")
        svc.calculate.assert_called_once_with("2025-01", "monthly")
        svc.lock.assert_called_once()

    def test_run_propagates_closing_error(self):
        svc = self._svc()
        svc.calculate.side_effect = ClosingError("Keine Daten")
        with pytest.raises(ClosingError, match="Keine Daten"):
            svc.run("2025-01")

    def test_run_commits_db(self):
        svc = self._svc()
        svc.run("2025-01")
        svc.db.commit.assert_called_once()

    def test_run_entry_count_in_message(self):
        calc = ClosingCalculateResult(
            period="2025-03", closing_type="monthly",
            entry_count=42, total_debit=1000.0, total_credit=1000.0, balance=0.0,
        )
        svc = self._svc(calc_result=calc)
        result = svc.run("2025-03")
        assert "42" in result.message
