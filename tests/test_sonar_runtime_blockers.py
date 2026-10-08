"""Actual public imports and dashboard calls reported broken by SonarCloud."""

from datetime import datetime, timedelta
from importlib import import_module
from types import SimpleNamespace

import pytest
from sqlalchemy.engine import Engine


@pytest.fixture(autouse=True)
def prohibit_database_connections(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("These runtime contracts must not connect to a database")

    monkeypatch.setattr(Engine, "connect", forbidden)


AGRAR_EXPORTS = {
    "tax_profile_service": ["get_taxation_type_for_supplier"],
    "partie_service": ["generate_lot_number", "create_harvest_acceptance_lines"],
    "price_adjustment_service": ["apply_price_adjustments", "calculate_price_adjustment"],
    "vat_service": [
        "determine_ownership_type", "can_create_credit_note_for_vat",
        "create_provisional_credit_note", "create_advance_payment_credit_note",
        "create_correction_credit_note",
    ],
}


@pytest.mark.parametrize("module,name", [
    (module, name) for module, names in AGRAR_EXPORTS.items() for name in names
])
def test_declared_agrar_export_resolves_to_existing_canonical_function(module, name):
    package = import_module("modules.agrar.services")
    canonical = import_module(f"modules.agrar.services.{module}")
    assert name in package.__all__
    assert getattr(package, name) is getattr(canonical, name)


def test_agrar_wildcard_import_is_complete_and_usable():
    namespace = {}
    exec("from modules.agrar.services import *", namespace)
    package = import_module("modules.agrar.services")
    assert all(name in namespace for name in package.__all__)
    assert namespace["determine_ownership_type"]("STORAGE_ONLY") == "THIRD_PARTY_STOCK"
    assert namespace["can_create_credit_note_for_vat"]("STORAGE_ONLY", "NO_INVOICE") is False


def test_unusable_legacy_nuts_import_is_retired():
    with pytest.raises(ModuleNotFoundError) as error:
        import_module("modules.agrar.services.nuts2_service")
    assert error.value.name == "modules.agrar.services.nuts2_service"


@pytest.fixture
def audit_service(monkeypatch):
    module = import_module("app.security.audit_service")

    class FixedTime(datetime):
        @classmethod
        def utcnow(cls):
            return cls(2026, 10, 8, 12)

    monkeypatch.setattr(module, "datetime", FixedTime)
    return module.ISMSAuditService(db_session=None)


def test_empty_security_dashboard_does_not_crash(audit_service):
    result = audit_service.get_security_dashboard("tenant-a", days=7)
    assert result["total_events"] == 0
    assert result["risk_trend"] == []
    assert result["period_days"] == 7


def test_security_dashboard_preserves_tenant_and_period_filters(audit_service):
    for tenant, event, age in [
        ("tenant-a", "login_success", 1),
        ("tenant-a", "security_breach", 2),
        ("tenant-b", "security_breach", 1),
        ("tenant-a", "data_delete", 20),
    ]:
        audit_service.log_security_event({"tenant_id": tenant, "event_type": event})
        entry = audit_service.audit_trail[-1]
        entry.timestamp = (datetime(2026, 10, 8, 12) - timedelta(days=age)).isoformat()
        entry.integrity_hash = audit_service._create_integrity_hash(entry)
        audit_service.last_hash = entry.integrity_hash
    result = audit_service.get_security_dashboard("tenant-a", days=7)
    assert result["total_events"] == 2
    assert result["critical_events"] == 1
    assert result["top_event_types"] == {"login_success": 1, "security_breach": 1}
    assert sum(row["event_count"] for row in result["risk_trend"]) == 2


def test_explicit_audit_report_filter_still_works(audit_service):
    for event in ["login_success", "logout"]:
        audit_service.log_security_event({"tenant_id": "tenant-a", "event_type": event})
    report = audit_service.get_audit_report(
        "tenant-a", datetime(2026, 10, 8), datetime(2026, 10, 9), {"event_type": "logout"}
    )
    assert report["total_events"] == 1
    assert report["event_summary"] == {"logout": 1}


def test_operations_constructor_registers_distinct_maintenance_windows():
    module = import_module("app.operations_security.management")
    first = module.ISO27001OperationsSecurity(db_session=None)
    second = module.ISO27001OperationsSecurity(db_session=None)
    windows = list(first.maintenance_windows.values())
    assert {window.name for window in windows} == {
        "Database Maintenance", "Security Updates", "System Health Check",
    }
    assert all(window.id and window.start_time < window.end_time for window in windows)
    assert set(first.maintenance_windows).isdisjoint(second.maintenance_windows)


@pytest.mark.parametrize("statuses,expected", [
    ([], 100),
    (["DRAFT", "SUBMITTED", "APPROVED"], 100),
    (["DEPLOYED"], 100),
    (["ROLLED_BACK", "REJECTED"], 0),
    (["DEPLOYED", "DEPLOYED", "ROLLED_BACK", "REJECTED", "SUBMITTED"], 50),
])
def test_actual_operations_dashboard_uses_terminal_change_statuses(statuses, expected):
    module = import_module("app.operations_security.management")
    service = module.ISO27001OperationsSecurity(db_session=None)
    service.change_requests = {
        str(index): SimpleNamespace(status=module.ChangeStatus[status])
        for index, status in enumerate(statuses)
    }
    dashboard = service.get_operations_dashboard()
    summary = dashboard["change_management"]
    assert summary["total_changes"] == len(statuses)
    assert summary["completed_changes"] == statuses.count("DEPLOYED")
    assert summary["failed_changes"] == statuses.count("ROLLED_BACK") + statuses.count("REJECTED")
    assert summary["success_rate"] == expected
