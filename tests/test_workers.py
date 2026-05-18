"""Unit tests for background workers."""
from __future__ import annotations

import asyncio
import sys
import types
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_db():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.fetchall.return_value = []
    db.execute.return_value.scalar.return_value = 0
    db.query.return_value.filter.return_value.delete.return_value = 0
    db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
    db.query.return_value.filter.return_value.all.return_value = []
    db.commit = MagicMock()
    db.rollback = MagicMock()
    db.close = MagicMock()
    return db


def run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _stub_daily_report_service():
    """Inject a stub for the broken DailyReportService import chain."""
    # Build minimal fake module tree so daily_report_worker can be imported
    for mod_path in [
        "app.domains",
        "app.domains.crm",
        "app.domains.crm.services",
        "app.domains.crm.services.daily_report_service",
    ]:
        if mod_path not in sys.modules:
            sys.modules[mod_path] = types.ModuleType(mod_path)

    fake_svc_mod = sys.modules["app.domains.crm.services.daily_report_service"]
    if not hasattr(fake_svc_mod, "DailyReportService"):
        class DailyReportService:
            def __init__(self, db):
                pass
            def generate_daily_reports(self):
                return []
            def send_daily_reports(self, reports):
                return {}
        fake_svc_mod.DailyReportService = DailyReportService


# ============================================================================
# BaseWorker
# ============================================================================

@pytest.mark.unit
def test_base_worker_is_abstract():
    from app.workers.base_worker import BaseWorker
    import inspect
    assert inspect.isabstract(BaseWorker)


@pytest.mark.unit
def test_base_worker_base_result():
    from app.workers.base_worker import BaseWorker

    class _Concrete(BaseWorker):
        async def run(self):
            return self._base_result(foo="bar")

    w = _Concrete()
    result = run(w.run())
    assert result["success"] is True
    assert result["foo"] == "bar"


@pytest.mark.unit
def test_base_worker_error_result():
    from app.workers.base_worker import BaseWorker

    class _Concrete(BaseWorker):
        async def run(self):
            base = self._base_result()
            return self._error_result(base, ValueError("boom"))

    w = _Concrete()
    result = run(w.run())
    assert result["success"] is False
    assert "boom" in result["error"]


@pytest.mark.unit
def test_base_worker_ensure_db_calls_initialize():
    from app.workers.base_worker import BaseWorker

    class _Concrete(BaseWorker):
        async def run(self):
            await self._ensure_db()
            return self._base_result()

    db = _mock_db()
    w = _Concrete()
    with patch("app.workers.base_worker.get_db", return_value=iter([db])):
        result = run(w.run())
    assert result["success"] is True
    assert w.db is db


# ============================================================================
# CleanupWorker
# ============================================================================

@pytest.mark.unit
def test_cleanup_worker_instantiation():
    from app.workers.cleanup_worker import CleanupWorker
    w = CleanupWorker()
    assert w.db is None


@pytest.mark.unit
def test_cleanup_worker_run_returns_tasks():
    from app.workers.cleanup_worker import CleanupWorker
    db = _mock_db()
    w = CleanupWorker()
    w.db = db
    result = run(w.run())
    assert result["success"] is True
    assert "tasks" in result
    assert len(result["tasks"]) == 4


@pytest.mark.unit
def test_cleanup_worker_run_no_db():
    """run() should still succeed when db initialisation raises."""
    from app.workers.cleanup_worker import CleanupWorker
    w = CleanupWorker()
    # Don't assign db — _ensure_db will call get_db
    with patch("app.workers.base_worker.get_db", side_effect=Exception("no db")):
        result = run(w.run())
    # Error is captured, success flipped to False
    assert result["success"] is False


@pytest.mark.unit
def test_cleanup_worker_cleanup_closes_db():
    from app.workers.cleanup_worker import CleanupWorker
    db = _mock_db()
    w = CleanupWorker()
    w.db = db
    run(w.cleanup())
    db.close.assert_called_once()


@pytest.mark.unit
def test_cleanup_worker_audit_log_deletion():
    from app.workers.cleanup_worker import CleanupWorker
    db = _mock_db()
    db.query.return_value.filter.return_value.delete.return_value = 5
    w = CleanupWorker()
    w.db = db
    result = run(w._cleanup_old_audit_logs())
    assert result["success"] is True
    assert result["deleted"] == 5
    db.commit.assert_called_once()


@pytest.mark.unit
def test_execute_cleanup_returns_dict():
    from app.workers.cleanup_worker import execute_cleanup
    db = _mock_db()
    with patch("app.workers.base_worker.get_db", return_value=iter([db])):
        result = execute_cleanup()
    assert isinstance(result, dict)
    assert "success" in result


# ============================================================================
# ComplianceCheckWorker
# ============================================================================

@pytest.mark.unit
def test_compliance_worker_instantiation():
    from app.workers.compliance_check_worker import ComplianceCheckWorker
    w = ComplianceCheckWorker()
    assert w.db is None


@pytest.mark.unit
def test_compliance_worker_run_structure():
    from app.workers.compliance_check_worker import ComplianceCheckWorker
    db = _mock_db()
    w = ComplianceCheckWorker()
    w.db = db
    result = run(w.run())
    assert "issues" in result
    assert "checks" in result
    assert "passed" in result
    assert "failed" in result
    assert result["checks"] == 5


@pytest.mark.unit
def test_compliance_worker_checks_with_no_db():
    """All individual checks return [] when db is None."""
    from app.workers.compliance_check_worker import ComplianceCheckWorker
    w = ComplianceCheckWorker()
    # db remains None — checks should return empty lists
    for method in (
        w._check_certificate_expiry,
        w._check_employee_certifications,
        w._check_vehicle_inspections,
        w._check_warehouse_licenses,
        w._check_tax_compliance,
    ):
        issues = run(method())
        assert isinstance(issues, list)


@pytest.mark.unit
def test_compliance_worker_certificate_expiry_returns_list():
    from app.workers.compliance_check_worker import ComplianceCheckWorker
    db = _mock_db()
    w = ComplianceCheckWorker()
    w.db = db
    issues = run(w._check_certificate_expiry())
    assert isinstance(issues, list)


@pytest.mark.unit
def test_compliance_worker_no_db_run():
    from app.workers.compliance_check_worker import ComplianceCheckWorker
    w = ComplianceCheckWorker()
    with patch("app.workers.base_worker.get_db", side_effect=Exception("no db")):
        result = run(w.run())
    assert result["success"] is False


# ============================================================================
# DailyReportWorker
# ============================================================================

@pytest.mark.unit
def test_daily_report_worker_instantiation():
    _stub_daily_report_service()
    from app.workers.daily_report_worker import DailyReportWorker  # noqa: PLC0415
    w = DailyReportWorker()
    assert w.service is None


@pytest.mark.unit
def test_daily_report_worker_run_no_reports():
    _stub_daily_report_service()
    from app.workers.daily_report_worker import DailyReportWorker  # noqa: PLC0415
    db = _mock_db()
    w = DailyReportWorker()
    w.db = db
    mock_service = MagicMock()
    mock_service.generate_daily_reports.return_value = []
    w.service = mock_service
    result = run(w.run())
    assert result["success"] is True
    assert result["reports_generated"] == 0
    assert "message" in result


@pytest.mark.unit
def test_daily_report_worker_run_with_reports():
    _stub_daily_report_service()
    from app.workers.daily_report_worker import DailyReportWorker  # noqa: PLC0415
    db = _mock_db()
    w = DailyReportWorker()
    w.db = db
    mock_service = MagicMock()
    mock_service.generate_daily_reports.return_value = ["report1", "report2"]
    mock_service.send_daily_reports.return_value = {
        "report1": {"success": True},
        "report2": {"success": False},
    }
    w.service = mock_service
    result = run(w.run())
    assert result["success"] is True
    assert result["reports_generated"] == 2
    assert result["reports_sent"] == 1


@pytest.mark.unit
def test_daily_report_worker_run_service_error():
    _stub_daily_report_service()
    from app.workers.daily_report_worker import DailyReportWorker  # noqa: PLC0415
    w = DailyReportWorker()
    mock_service = MagicMock()
    mock_service.generate_daily_reports.side_effect = RuntimeError("db down")
    w.service = mock_service
    result = run(w.run())
    assert result["success"] is False
    assert "db down" in result["error"]


@pytest.mark.unit
def test_daily_report_worker_cleanup():
    _stub_daily_report_service()
    from app.workers.daily_report_worker import DailyReportWorker  # noqa: PLC0415
    db = _mock_db()
    w = DailyReportWorker()
    w.db = db
    run(w.cleanup())
    db.close.assert_called_once()


# ============================================================================
# MonthlyReportWorker
# ============================================================================

@pytest.mark.unit
def test_monthly_report_worker_instantiation():
    from app.workers.monthly_report_worker import MonthlyReportWorker
    w = MonthlyReportWorker()
    assert w.db is None


@pytest.mark.unit
def test_monthly_report_worker_run_db_ok():
    from app.workers.monthly_report_worker import MonthlyReportWorker
    db = _mock_db()
    db.execute.return_value.scalar.return_value = 10
    w = MonthlyReportWorker()
    w.db = db
    result = run(w.run())
    assert result["success"] is True
    assert result["reports_generated"] == 1
    assert "period_start" in result
    assert "period_end" in result


@pytest.mark.unit
def test_monthly_report_worker_run_db_error_graceful():
    """DB execute failure is silently caught; reports_generated stays 0."""
    from app.workers.monthly_report_worker import MonthlyReportWorker
    db = _mock_db()
    db.execute.side_effect = Exception("table missing")
    w = MonthlyReportWorker()
    w.db = db
    result = run(w.run())
    # outer try still succeeded
    assert result["success"] is True
    assert result["reports_generated"] == 0


@pytest.mark.unit
def test_monthly_report_worker_no_db():
    from app.workers.monthly_report_worker import MonthlyReportWorker
    w = MonthlyReportWorker()
    with patch("app.workers.base_worker.get_db", side_effect=Exception("no db")):
        result = run(w.run())
    assert result["success"] is False


# ============================================================================
# WeeklyReportWorker
# ============================================================================

@pytest.mark.unit
def test_weekly_report_worker_instantiation():
    from app.workers.weekly_report_worker import WeeklyReportWorker
    w = WeeklyReportWorker()
    assert w.db is None


@pytest.mark.unit
def test_weekly_report_worker_run_db_ok():
    from app.workers.weekly_report_worker import WeeklyReportWorker
    db = _mock_db()
    db.execute.return_value.scalar.return_value = 7
    w = WeeklyReportWorker()
    w.db = db
    result = run(w.run())
    assert result["success"] is True
    assert result["reports_generated"] == 1
    assert "period_start" in result
    assert "period_end" in result


@pytest.mark.unit
def test_weekly_report_worker_run_db_error_graceful():
    from app.workers.weekly_report_worker import WeeklyReportWorker
    db = _mock_db()
    db.execute.side_effect = Exception("table missing")
    w = WeeklyReportWorker()
    w.db = db
    result = run(w.run())
    assert result["success"] is True
    assert result["reports_generated"] == 0


@pytest.mark.unit
def test_weekly_report_worker_no_db():
    from app.workers.weekly_report_worker import WeeklyReportWorker
    w = WeeklyReportWorker()
    with patch("app.workers.base_worker.get_db", side_effect=Exception("no db")):
        result = run(w.run())
    assert result["success"] is False


# ============================================================================
# PriceMonitoringWorker
# ============================================================================

@pytest.mark.unit
def test_price_monitoring_worker_instantiation():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    w = PriceMonitoringWorker()
    assert w.db is None


@pytest.mark.unit
def test_price_monitoring_worker_run_no_db():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    w = PriceMonitoringWorker()
    with patch("app.workers.base_worker.get_db", side_effect=Exception("no db")):
        result = run(w.run())
    assert result["success"] is False


@pytest.mark.unit
def test_price_monitoring_worker_run_empty_prices():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    db = _mock_db()
    w = PriceMonitoringWorker()
    w.db = db
    result = run(w.run())
    assert "alerts" in result
    assert "checks" in result
    assert result["checks"] == 4
    assert isinstance(result["alerts"], list)


@pytest.mark.unit
def test_price_monitoring_check_competitor_returns_empty():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    w = PriceMonitoringWorker()
    result = run(w._check_competitor_prices())
    assert result == []


@pytest.mark.unit
def test_price_monitoring_check_supplier_returns_empty():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    w = PriceMonitoringWorker()
    result = run(w._check_supplier_price_changes())
    assert result == []


@pytest.mark.unit
def test_price_monitoring_daily_prices_no_db():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    w = PriceMonitoringWorker()
    # db is None
    result = run(w._check_daily_price_changes())
    assert result == []


@pytest.mark.unit
def test_price_monitoring_threshold_no_db():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    w = PriceMonitoringWorker()
    result = run(w._check_price_thresholds())
    assert result == []


@pytest.mark.unit
def test_price_monitoring_cleanup():
    from app.workers.price_monitoring_worker import PriceMonitoringWorker
    db = _mock_db()
    w = PriceMonitoringWorker()
    w.db = db
    run(w.cleanup())
    db.close.assert_called_once()


@pytest.mark.unit
def test_price_key_helper():
    from app.workers.price_monitoring_worker import _price_key
    r = MagicMock()
    r.article_id = "A1"
    r.warengruppe = "GETREIDE"
    r.crop_code = "WW"
    assert _price_key(r) == ("A1", "GETREIDE", "WW")
