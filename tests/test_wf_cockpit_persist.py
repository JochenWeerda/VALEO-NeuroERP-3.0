"""WF-COCKPIT-PERSIST-001 — Unit Tests fuer WorkflowCockpitPersistService.

Alle Tests laufen ohne Datenbank (Mock-Session via MagicMock).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, call, patch

import pytest

from app.services.wf_cockpit_persist_service import WorkflowCockpitPersistService


def _mock_row(**kwargs):
    row = MagicMock()
    row._mapping = kwargs
    return row


def _svc(rows: list | None = None, rowcount: int = 0) -> WorkflowCockpitPersistService:
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.fetchone.return_value = rows[0] if rows else None
    execute_result.fetchall.return_value = rows or []
    execute_result.rowcount = rowcount
    db.execute.return_value = execute_result
    return WorkflowCockpitPersistService(db=db, tenant_id="test-tenant")


class TestUpsertInstance:
    def test_insert_when_not_exists(self):
        svc = _svc(rows=None)
        svc.upsert_instance(
            process_instance_id="pid-1",
            process_key="O2C",
            status="running",
            correlation_id="corr-1",
        )
        svc.db.execute.assert_called()
        svc.db.commit.assert_called()

    def test_update_when_exists(self):
        existing = _mock_row(id="pid-1")
        svc = _svc(rows=[existing])
        svc.upsert_instance(
            process_instance_id="pid-1",
            process_key="O2C",
            status="completed",
            correlation_id="corr-1",
        )
        svc.db.commit.assert_called()

    def test_upsert_with_optional_fields(self):
        svc = _svc()
        svc.upsert_instance(
            process_instance_id="pid-2",
            process_key="P2P",
            status="failed",
            correlation_id="corr-2",
            current_step="Freigabe",
            business_object_ref="BE-001",
            audit_ref="AUDIT-001",
            active_blocker_count=2,
            replayable=True,
        )
        svc.db.commit.assert_called()


class TestAppendEvent:
    def test_creates_event_with_id(self):
        svc = _svc()
        event_id = svc.append_event(
            process_instance_id="pid-1",
            kind="created",
            message="Prozess gestartet",
        )
        assert isinstance(event_id, str)
        assert len(event_id) == 36

    def test_payload_serialized(self):
        svc = _svc()
        svc.append_event(
            process_instance_id="pid-1",
            kind="domain_event",
            message="Test",
            payload={"key": "value", "num": 42},
        )
        call_args = svc.db.execute.call_args
        params = call_args[0][1]
        assert "payload" in params
        parsed = json.loads(params["payload"])
        assert parsed["key"] == "value"


class TestUpsertBlocker:
    def test_creates_new_blocker(self):
        svc = _svc()
        bid = svc.upsert_blocker(
            process_instance_id="pid-1",
            blocker_type="DATEV_TIMEOUT",
            message="DATEV antwortet nicht",
            external_system="DATEV",
        )
        assert isinstance(bid, str)
        svc.db.commit.assert_called()

    def test_existing_blocker_not_duplicated(self):
        existing = _mock_row(id="blk-1")
        svc = _svc(rows=[existing])
        bid = svc.upsert_blocker(
            process_instance_id="pid-1",
            blocker_id="blk-1",
            blocker_type="ELSTER",
            message="ELSTER-Verbindungsfehler",
        )
        assert bid == "blk-1"


class TestResolveBlocker:
    def test_resolves_blocker_returns_true(self):
        svc = _svc(rowcount=1)
        result = svc.resolve_blocker(blocker_id="blk-1")
        assert result is True

    def test_blocker_not_found_returns_false(self):
        svc = _svc(rowcount=0)
        result = svc.resolve_blocker(blocker_id="blk-x")
        assert result is False


class TestListInstances:
    def test_returns_list(self):
        rows = [
            _mock_row(id="p1", process_key="O2C", status="running",
                      correlation_id="c1", idempotency_key=None,
                      business_object_ref=None, current_step=None,
                      created_at=datetime(2026, 6, 25, tzinfo=timezone.utc),
                      updated_at=datetime(2026, 6, 25, tzinfo=timezone.utc),
                      active_blocker_count=0, replayable=False, tenant_id="test-tenant"),
        ]
        svc = _svc(rows=rows)
        result = svc.list_instances()
        assert isinstance(result, list)

    def test_status_filter_passed_to_query(self):
        svc = _svc()
        svc.list_instances(status="failed")
        call_args = svc.db.execute.call_args
        params = call_args[0][1]
        assert params.get("status") == "failed"

    def test_limit_passed_to_query(self):
        svc = _svc()
        svc.list_instances(limit=10)
        call_args = svc.db.execute.call_args
        params = call_args[0][1]
        assert params.get("lim") == 10


class TestDeadLetterView:
    def test_returns_dict_with_items(self):
        rows = [
            _mock_row(
                id="p1", process_key="FIBU", status="failed",
                correlation_id="c1", current_step="DATEV",
                updated_at=datetime(2026, 6, 25, tzinfo=timezone.utc),
                replayable=True, open_blocker_count=1,
            ),
        ]
        svc = _svc(rows=rows)
        result = svc.dead_letter_view()
        assert "dead_letter_count" in result
        assert "items" in result
        assert result["dead_letter_count"] == 1

    def test_timestamps_iso_serialized(self):
        rows = [
            _mock_row(
                id="p1", process_key="P2P", status="blocked_external_gate",
                correlation_id="c1", current_step=None,
                updated_at=datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc),
                replayable=False, open_blocker_count=2,
            ),
        ]
        svc = _svc(rows=rows)
        result = svc.dead_letter_view()
        assert "2026-06-25" in result["items"][0]["updated_at"]


class TestGetInstanceDetail:
    def test_not_found_returns_none(self):
        svc = _svc(rows=None)
        result = svc.get_instance_detail("not-existing")
        assert result is None

    def test_found_includes_events_and_blockers(self):
        instance_row = _mock_row(
            id="p1", tenant_id="test-tenant", process_key="WMS", status="running",
            correlation_id="c1", idempotency_key=None, business_object_ref=None,
            current_step="Einlagerung", audit_ref=None,
            created_at=datetime(2026, 6, 25, tzinfo=timezone.utc),
            updated_at=datetime(2026, 6, 25, tzinfo=timezone.utc),
            active_blocker_count=0, replayable=False,
        )
        db = MagicMock()
        results = iter([
            MagicMock(fetchone=MagicMock(return_value=instance_row), fetchall=MagicMock(return_value=[])),
            MagicMock(fetchone=MagicMock(return_value=None), fetchall=MagicMock(return_value=[])),
            MagicMock(fetchone=MagicMock(return_value=None), fetchall=MagicMock(return_value=[])),
        ])
        db.execute.side_effect = lambda *a, **kw: next(results)
        svc = WorkflowCockpitPersistService(db=db, tenant_id="test-tenant")
        result = svc.get_instance_detail("p1")
        assert result is not None
        assert result["id"] == "p1"
        assert "events" in result
        assert "blockers" in result


class TestRetryInstance:
    def _svc_with_row(self, status: str):
        db = MagicMock()
        row = MagicMock()
        row.status = status
        row.replayable = True
        db.execute.return_value.fetchone.return_value = row
        db.execute.return_value.rowcount = 1
        return WorkflowCockpitPersistService(db=db, tenant_id="t1"), db

    def test_retry_failed_returns_true(self):
        svc, db = self._svc_with_row("failed")
        result = svc.retry_instance(process_instance_id="p1", retried_by="hr-admin", reason="network error")
        assert result is True
        assert db.commit.call_count >= 1

    def test_retry_blocked_external_returns_true(self):
        svc, db = self._svc_with_row("blocked_external_gate")
        result = svc.retry_instance(process_instance_id="p1")
        assert result is True

    def test_retry_running_status_returns_false(self):
        svc, db = self._svc_with_row("running")
        result = svc.retry_instance(process_instance_id="p1")
        assert result is False
        db.commit.assert_not_called()

    def test_retry_not_found_returns_false(self):
        db = MagicMock()
        db.execute.return_value.fetchone.return_value = None
        svc = WorkflowCockpitPersistService(db=db, tenant_id="t1")
        result = svc.retry_instance(process_instance_id="unknown")
        assert result is False


class TestCompensateInstance:
    def _svc_with_row(self, status: str):
        db = MagicMock()
        row = MagicMock()
        row.status = status
        db.execute.return_value.fetchone.return_value = row
        db.execute.return_value.rowcount = 1
        return WorkflowCockpitPersistService(db=db, tenant_id="t1"), db

    def test_compensate_returns_true(self):
        svc, db = self._svc_with_row("failed")
        result = svc.compensate_instance(
            process_instance_id="p1",
            compensated_by="manager",
            compensation_action="storno",
            notes="Kundenauftrag storniert",
        )
        assert result is True
        assert db.commit.call_count >= 1

    def test_compensate_not_found_returns_false(self):
        db = MagicMock()
        db.execute.return_value.fetchone.return_value = None
        svc = WorkflowCockpitPersistService(db=db, tenant_id="t1")
        result = svc.compensate_instance(process_instance_id="missing")
        assert result is False


class TestUpsertFromEventSync:
    def test_sync_calls_upsert_and_append(self):
        db = MagicMock()
        db.execute.return_value.fetchone.return_value = None
        db.execute.return_value.fetchall.return_value = []
        svc = WorkflowCockpitPersistService(db=db, tenant_id="t1")
        svc._upsert_from_event_sync(
            tenant_id="t2",
            process_instance_id="p1",
            process_key="O2C",
            status="running",
            correlation_id="c1",
            current_step="Auftragsannahme",
            business_object_ref="order-42",
            event_kind="order_created",
            event_message="Auftrag erstellt",
            event_payload={"ref": "order-42"},
        )
        assert db.execute.call_count >= 2
