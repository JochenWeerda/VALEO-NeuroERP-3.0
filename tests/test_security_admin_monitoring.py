from __future__ import annotations

import importlib

from app.services.security_observability import SecurityObservability, security_observer

admin_monitoring = importlib.import_module("app.api.v1.endpoints.admin_monitoring")


class _Row:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _DbResult:
    def __init__(self, rows=None, first=None):
        self._rows = list(rows or [])
        self._first = first

    def fetchall(self):
        return list(self._rows)

    def first(self):
        return self._first


class _MonitoringDb:
    def execute(self, statement, params=None):
        sql = str(statement)
        if "SELECT 1" in sql:
            return _DbResult(first=(1,))
        if "FROM domain_inventory.articles" in sql:
            return _DbResult(rows=[])
        if "FROM offene_posten" in sql:
            return _DbResult(first=_Row(cnt=0))
        raise AssertionError(f"Unexpected SQL: {sql}")


def test_admin_alerts_include_security_events():
    security_observer.reset()
    security_observer.record_event(
        category="tenant_isolation",
        outcome="denied",
        severity="warning",
        message="Cross-tenant access denied",
        tenant_id="tenant-a",
    )

    result = admin_monitoring.list_admin_monitoring_alerts(
        tenant_id="tenant-a",
        db=_MonitoringDb(),
    )

    assert result.active >= 1
    assert any(item.type == "Security tenant_isolation" for item in result.items)
    assert result.warning >= 1


def test_security_monitoring_summary_surfaces_counts(monkeypatch):
    security_observer.reset()
    security_observer.record_event(
        category="outbound_http",
        outcome="blocked",
        severity="warning",
        message="Blocked outbound target",
        tenant_id=None,
    )
    security_observer.record_event(
        category="tenant_isolation",
        outcome="denied",
        severity="warning",
        message="Cross-tenant access denied",
        tenant_id="tenant-a",
    )

    monkeypatch.setattr(
        admin_monitoring,
        "_load_tenant_settings",
        lambda _db, _tenant_id: {
            "admin_monitoring": {
                "rules": [{"id": "rule-1"}],
                "channels": [{"id": "channel-1"}, {"id": "channel-2"}],
                "scheduler_jobs": [],
            }
        },
    )

    result = admin_monitoring.get_security_monitoring_summary(
        tenant_id="tenant-a",
        db=object(),
    )

    assert result.status == "warning"
    assert result.event_count == 2
    assert result.blocked_count == 1
    assert result.denied_count == 1
    assert result.channel_count == 2
    assert result.rule_count == 1
    assert result.top_categories["outbound_http"] == 1


def test_security_monitoring_summary_reads_persisted_events_after_restart(monkeypatch, tmp_path):
    observer = SecurityObservability(
        persist_enabled=True,
        storage_path=tmp_path / "security-events.jsonl",
    )
    observer.reset()
    observer.record_event(
        category="tenant_isolation",
        outcome="denied",
        severity="warning",
        message="Cross-tenant access denied",
        tenant_id="tenant-a",
    )

    monkeypatch.setattr(
        admin_monitoring,
        "security_observer",
        SecurityObservability(
            persist_enabled=True,
            storage_path=tmp_path / "security-events.jsonl",
        ),
    )
    monkeypatch.setattr(
        admin_monitoring,
        "_load_tenant_settings",
        lambda _db, _tenant_id: {"admin_monitoring": {"rules": [], "channels": [], "scheduler_jobs": []}},
    )

    result = admin_monitoring.get_security_monitoring_summary(
        tenant_id="tenant-a",
        db=object(),
    )

    assert result.event_count == 1
    assert result.denied_count == 1
    assert result.top_categories["tenant_isolation"] == 1
