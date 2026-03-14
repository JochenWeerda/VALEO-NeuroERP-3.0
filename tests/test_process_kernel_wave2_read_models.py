"""Wave-2 AP2 Contract-Tests: Finance Read-Model Schemas."""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from app.api.v1.endpoints import finance_read_models as read_models

APInvoiceBucket = read_models.APInvoiceBucket
APInvoiceCockpitReadModel = read_models.APInvoiceCockpitReadModel
PaymentRunCockpitReadModel = read_models.PaymentRunCockpitReadModel
WorkflowInstanceSummary = read_models.WorkflowInstanceSummary
WorkflowStepSlaSummary = read_models.WorkflowStepSlaSummary
WorkflowSlaProfile = read_models.WorkflowSlaProfile
ProcessObservationReadModel = read_models.ProcessObservationReadModel


class FakeRegistryResult:
    def __init__(self, rows=None):
        self._rows = rows or []

    def mappings(self):
        return self

    def all(self):
        return list(self._rows)

    def first(self):
        return self._rows[0] if self._rows else None


class FakeProjectionRegistryDb:
    def __init__(self, select_rows=None, snapshot_rows=None, cursor_rows=None, workflow_event_rows=None, outbox_rows=None):
        self.select_rows = select_rows or []
        self.snapshot_rows = snapshot_rows or []
        self.cursor_rows = cursor_rows or []
        self.workflow_event_rows = workflow_event_rows or []
        self.outbox_rows = outbox_rows or []
        self.commands = []

    def execute(self, statement, params=None):
        sql = str(statement)
        self.commands.append((sql, params))
        if "SELECT projection_key, item_count, last_rebuilt_at" in sql:
            return FakeRegistryResult(self.select_rows)
        if "SELECT projection_key, rebuilt_at" in sql:
            return FakeRegistryResult(self.snapshot_rows)
        if "FROM domain_shared.process_projection_cursors" in sql:
            return FakeRegistryResult(self.cursor_rows)
        if "SELECT domain, doc_number, ts" in sql and "FROM workflow_audit" in sql:
            return FakeRegistryResult(self.workflow_event_rows)
        if "SELECT id, event_type, timestamp" in sql and "FROM outbox_events" in sql:
            event_types = {
                str(value)
                for key, value in (params or {}).items()
                if str(key).startswith("event_type_")
            }
            if not event_types:
                return FakeRegistryResult(self.outbox_rows)
            return FakeRegistryResult(
                [row for row in self.outbox_rows if str(row.get("event_type")) in event_types]
            )
        return FakeRegistryResult()

    def commit(self):
        self.commands.append(("COMMIT", None))

    def rollback(self):
        self.commands.append(("ROLLBACK", None))


# ---------------------------------------------------------------------------
# 1. APInvoiceCockpitReadModel — schema_version
# ---------------------------------------------------------------------------

def test_ap_invoice_cockpit_read_model_has_schema_version():
    model = APInvoiceCockpitReadModel(
        tenant_id="t1",
        buckets=[],
        total_count=0,
        pending_approval_count=0,
        ready_to_post_count=0,
        overdue_count=0,
    )
    assert model.schema_version == 1


# ---------------------------------------------------------------------------
# 2. APInvoiceCockpitReadModel — buckets serialise correctly
# ---------------------------------------------------------------------------

def test_ap_invoice_cockpit_read_model_serializes_buckets():
    bucket = APInvoiceBucket(status="ENTWURF", count=3, total_amount=150.0)
    model = APInvoiceCockpitReadModel(
        tenant_id="t1",
        buckets=[bucket],
        total_count=3,
        pending_approval_count=0,
        ready_to_post_count=0,
        overdue_count=0,
    )
    serialized = model.model_dump()
    assert len(serialized["buckets"]) == 1
    first = serialized["buckets"][0]
    assert first["status"] == "ENTWURF"
    assert first["count"] == 3
    assert first["total_amount"] == 150.0


# ---------------------------------------------------------------------------
# 3. PaymentRunCockpitReadModel — schema_version
# ---------------------------------------------------------------------------

def test_payment_run_cockpit_read_model_has_schema_version():
    model = PaymentRunCockpitReadModel(
        tenant_id="t1",
        draft_count=2,
        approved_count=1,
        executed_count=0,
        total_pending_amount=500.0,
    )
    assert model.schema_version == 1


def test_projection_builders_are_reusable_without_http_layer():
    ap_projection = read_models.project_ap_invoice_cockpit(
        tenant_id="t1",
        tenant_invoices=[
            {
                "semantic_status": "ENTWURF",
                "amount": 125.0,
                "created_at": "2026-01-01T00:00:00+00:00",
            },
            {
                "semantic_status": "ZUR_FREIGABE",
                "amount": 50.0,
                "approval_can_post": True,
            },
        ],
    )
    payment_projection = read_models.project_payment_run_cockpit(
        tenant_id="t1",
        tenant_runs=[
            {"status": "draft", "total_amount": 300.0},
            {"status": "approved", "total_amount": 200.0},
            {"status": "executed", "total_amount": 100.0},
        ],
    )

    assert ap_projection.total_count == 2
    assert ap_projection.pending_approval_count == 1
    assert ap_projection.ready_to_post_count == 1
    assert ap_projection.overdue_count == 1
    assert payment_projection.draft_count == 1
    assert payment_projection.approved_count == 1
    assert payment_projection.executed_count == 1
    assert payment_projection.total_pending_amount == 500.0


# ---------------------------------------------------------------------------
# 4. ProcessObservationReadModel — total_running aggregates correctly
# ---------------------------------------------------------------------------

def test_process_observation_read_model_aggregates_totals():
    instances = [
        WorkflowInstanceSummary(
            process_key="ap_approval",
            running_count=3,
            waiting_count=2,
            completed_today=1,
            failed_count=0,
        ),
        WorkflowInstanceSummary(
            process_key="payment_run",
            running_count=1,
            waiting_count=4,
            completed_today=0,
            failed_count=1,
        ),
    ]
    sla_profiles = [
        WorkflowSlaProfile(
            process_key="annahme",
            escalatable_steps=2,
            step_sla=[
                WorkflowStepSlaSummary(
                    step_key="warteschlange",
                    timeout_hours=4,
                    escalation_roles=["annahme_leiter"],
                )
            ],
        )
    ]
    model = ProcessObservationReadModel(
        tenant_id="t1",
        workflow_instances=instances,
        sla_profiles=sla_profiles,
        total_running=sum(i.running_count for i in instances),
        total_waiting=sum(i.waiting_count for i in instances),
        overdue_instances=0,
    )
    assert model.total_running == 4   # 3 + 1
    assert model.total_waiting == 6   # 2 + 4
    assert model.sla_profiles[0].process_key == "annahme"
    assert model.sla_profiles[0].step_sla[0].timeout_hours == 4
    assert model.schema_version == 1


def test_cash_closing_projection_builders_support_analysis_reporting_and_detail():
    snapshot = read_models.project_cash_closing_read_model(
        tenant_id="tenant-wave4",
        closing_rows=[
            {
                "id": "c1",
                "abschluss_datum": "2026-03-10",
                "status": "offen",
                "verantwortlicher": "Meyer",
                "items": {
                    "umsatz_gesamt": 120.0,
                    "umsatz_bar": 70.0,
                    "bargeld_gezaehlt": 68.0,
                    "differenz_bar": -2.0,
                    "umsatz_ec": 40.0,
                    "ec_abrechnung": 40.0,
                    "umsatz_paypal": 10.0,
                    "paypal_abrechnung": 10.0,
                    "belegnummer": "KA-1",
                    "tse_transaktionen": 4,
                },
            },
            {
                "id": "c2",
                "abschluss_datum": "2026-03-09",
                "status": "gebucht",
                "verantwortlicher": "Schulz",
                "items": {
                    "umsatz_gesamt": 80.0,
                    "umsatz_bar": 20.0,
                    "bargeld_gezaehlt": 20.0,
                    "differenz_bar": 0.0,
                    "umsatz_ec": 60.0,
                    "ec_abrechnung": 60.0,
                    "belegnummer": "KA-2",
                },
            },
        ],
        tenant_cash_movement_count=3,
        journal_resolver=lambda row: (
            {"id": "j2", "entry_number": "KA-2", "posting_date": "2026-03-09", "status": "posted"}
            if row["id"] == "c2"
            else None
        ),
    )

    analysis = read_models.project_cash_closing_analysis(snapshot)
    reporting = read_models.project_cash_closing_reporting(snapshot)
    detail = read_models.project_cash_closing_detail(snapshot, "c2")

    assert snapshot.total_count == 2
    assert analysis.exception_count == 1
    assert analysis.missing_posting_count == 1
    assert analysis.top_exception_operators[0].key == "Meyer"
    assert reporting.total_gross == 200.0
    assert reporting.periods[0].period_key == "2026-03"
    assert detail is not None
    assert detail.posting.journal_entry_number == "KA-2"


def test_rebuild_finance_projection_store_populates_projection_cache():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()

    result = read_models.rebuild_finance_projection_store(tenant_id="tenant-wave4", db=None)
    cached_ap = read_models._load_projection("tenant-wave4", "ap-invoice-cockpit", APInvoiceCockpitReadModel)
    cached_process = read_models._load_projection("tenant-wave4", "process-observation", ProcessObservationReadModel)
    status = read_models.get_projection_status("tenant-wave4")

    assert result.tenant_id == "tenant-wave4"
    assert result.schema_version == 1
    assert any(entry.projection_key == "cash-closings/reporting" for entry in result.projections)
    assert cached_ap is not None
    assert cached_ap.tenant_id == "tenant-wave4"
    assert cached_process is not None
    assert cached_process.tenant_id == "tenant-wave4"
    assert status.last_rebuilt_at == result.rebuilt_at
    assert status.cache_hits == 2
    assert status.cache_misses == 0
    assert status.projection_count >= 6


def test_cash_closing_detail_uses_projection_cache_without_db_lookup():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    cached_detail = read_models.CashClosingSnapshot(
        id="cached-1",
        closing_date="2026-03-11",
        operator_name="Cache",
        totals=read_models.CashClosingTotals(gross_total=10.0),
        posting=read_models.CashClosingPosting(),
        import_context=read_models.CashClosingImportContext(),
        reference_context=read_models.CashClosingReferenceContext(),
        exception_flags=read_models.CashClosingExceptionFlags(),
    )
    read_models._cache_projection("tenant-wave4", "cash-closings/detail/cached-1", cached_detail)

    detail = read_models._load_projection(
        "tenant-wave4",
        "cash-closings/detail/cached-1",
        read_models.CashClosingSnapshot,
    )

    assert detail is not None
    assert detail.id == "cached-1"


def test_projection_status_tracks_cache_misses():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()

    missing = read_models._load_projection("tenant-wave4", "does-not-exist", APInvoiceCockpitReadModel)
    status = read_models.get_projection_status("tenant-wave4")

    assert missing is None
    assert status.cache_hits == 0
    assert status.cache_misses == 1
    assert status.projection_count == 0


def test_projection_status_reads_persisted_registry_entries():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        select_rows=[
            {
                "projection_key": "cash-closings",
                "item_count": 3,
                "last_rebuilt_at": "2026-03-11T10:00:00+00:00",
            }
        ]
    )

    status = read_models.get_projection_status("tenant-wave4", db=fake_db)

    assert status.projection_count == 1
    assert status.last_rebuilt_at == "2026-03-11T10:00:00+00:00"
    assert status.projections[0].projection_key == "cash-closings"
    assert status.projections[0].item_count == 3


def test_projection_status_reads_persisted_snapshot_metadata():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        snapshot_rows=[
            {
                "projection_key": "cash-closings",
                "rebuilt_at": "2026-03-11T11:00:00+00:00",
            },
            {
                "projection_key": "cash-closings/analysis",
                "rebuilt_at": "2026-03-11T11:05:00+00:00",
            },
        ]
    )

    status = read_models.get_projection_status("tenant-wave4", db=fake_db)

    assert status.persisted_snapshot_count == 2
    assert status.last_snapshot_at == "2026-03-11T11:05:00+00:00"


def test_projection_status_reads_persisted_cursor_metadata():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        cursor_rows=[
            {
                "consumer_id": "finance-projections-01",
                "projection_key": "cash-closings",
                "updated_at": "2026-03-11T11:10:00+00:00",
                "last_event_id": None,
            },
            {
                "consumer_id": "finance-projections-01",
                "projection_key": "cash-closings/reporting",
                "updated_at": "2026-03-11T11:15:00+00:00",
                "last_event_id": "replay-workflow-PO-1-1741691700",
            },
        ]
    )

    status = read_models.get_projection_status("tenant-wave4", db=fake_db)

    assert status.persisted_cursor_count == 2
    assert status.last_cursor_advanced_at == "2026-03-11T11:15:00+00:00"
    assert status.last_processed_event_id == "replay-workflow-PO-1-1741691700"
    cash_reporting = next(entry for entry in status.projections if entry.projection_key == "cash-closings/reporting")
    assert cash_reporting.cursor_status is None
    assert cash_reporting.cursor_source == "workflow_audit"
    assert cash_reporting.cursor_updated_at == "2026-03-11T11:15:00+00:00"
    assert cash_reporting.last_processed_event_id == "replay-workflow-PO-1-1741691700"


def test_projection_status_exposes_per_projection_cursor_details():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        select_rows=[
            {
                "projection_key": "payment-run-cockpit",
                "item_count": 2,
                "last_rebuilt_at": "2026-03-12T09:00:00+00:00",
            }
        ],
        cursor_rows=[
            {
                "consumer_id": "finance-projections-01",
                "projection_key": "payment-run-cockpit",
                "updated_at": "2026-03-12T09:05:00+00:00",
                "last_event_id": "evt-pay-77",
                "status": "ready",
                "replay_from_event_id": None,
                "replay_to_event_id": None,
            }
        ],
    )

    status = read_models.get_projection_status("tenant-wave4", db=fake_db)

    entry = next(entry for entry in status.projections if entry.projection_key == "payment-run-cockpit")
    assert entry.item_count == 2
    assert entry.cursor_status == "ready"
    assert entry.cursor_source == "outbox_events"
    assert entry.cursor_updated_at == "2026-03-12T09:05:00+00:00"
    assert entry.last_processed_event_id == "evt-pay-77"


def test_rebuild_process_observation_cursor_uses_latest_workflow_event_id():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        workflow_event_rows=[
            {
                "domain": "workflow",
                "doc_number": "PO-42",
                "ts": 1741691700,
            }
        ]
    )

    read_models.rebuild_finance_projection_store("tenant-wave4", db=fake_db)

    cursor_commands = [
        params for sql, params in fake_db.commands
        if "INSERT INTO domain_shared.process_projection_cursors" in sql
        and params
        and params.get("projection_key") == "process-observation"
    ]
    assert cursor_commands
    assert cursor_commands[-1]["last_event_id"] == "replay-workflow-PO-42-1741691700"


def test_rebuild_ap_invoice_cursor_uses_latest_outbox_event_id():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        outbox_rows=[
            {
                "id": "evt-ap-99",
                "event_type": "APInvoiceApproved",
                "timestamp": "2026-03-11T12:30:00+00:00",
            }
        ]
    )

    read_models.rebuild_finance_projection_store("tenant-wave4", db=fake_db)

    cursor_commands = [
        params for sql, params in fake_db.commands
        if "INSERT INTO domain_shared.process_projection_cursors" in sql
        and params
        and params.get("projection_key") == "ap-invoice-cockpit"
    ]
    assert cursor_commands
    assert cursor_commands[-1]["last_event_id"] == "evt-ap-99"


def test_rebuild_payment_run_cursor_uses_latest_outbox_event_id():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        outbox_rows=[
            {
                "id": "evt-pay-77",
                "event_type": "payment_run.executed",
                "timestamp": "2026-03-11T12:40:00+00:00",
            }
        ]
    )

    read_models.rebuild_finance_projection_store("tenant-wave4", db=fake_db)

    cursor_commands = [
        params for sql, params in fake_db.commands
        if "INSERT INTO domain_shared.process_projection_cursors" in sql
        and params
        and params.get("projection_key") == "payment-run-cockpit"
    ]
    assert cursor_commands
    assert cursor_commands[-1]["last_event_id"] == "evt-pay-77"


def test_rebuild_payment_run_cursor_uses_returned_outbox_event_id():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        outbox_rows=[
            {
                "id": "evt-pay-ret-88",
                "event_type": "payment_run.returned",
                "timestamp": "2026-03-12T13:40:00+00:00",
            }
        ]
    )

    read_models.rebuild_finance_projection_store("tenant-wave4", db=fake_db)

    cursor_commands = [
        params for sql, params in fake_db.commands
        if "INSERT INTO domain_shared.process_projection_cursors" in sql
        and params
        and params.get("projection_key") == "payment-run-cockpit"
    ]
    assert cursor_commands
    assert cursor_commands[-1]["last_event_id"] == "evt-pay-ret-88"


def test_rebuild_cash_closing_cursors_use_latest_outbox_event_id():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb(
        outbox_rows=[
            {
                "id": "evt-cash-55",
                "event_type": "cash_closing.posted",
                "timestamp": "2026-03-11T12:45:00+00:00",
            }
        ]
    )

    read_models.rebuild_finance_projection_store("tenant-wave4", db=fake_db)

    cursor_commands = [
        params for sql, params in fake_db.commands
        if "INSERT INTO domain_shared.process_projection_cursors" in sql
        and params
        and params.get("projection_key") in {
            "cash-closings",
            "cash-closings/analysis",
            "cash-closings/reporting",
            "cash-closings/detail",
        }
    ]
    assert len(cursor_commands) == 4
    assert all(command["last_event_id"] == "evt-cash-55" for command in cursor_commands)


def test_rebuild_persists_projection_registry_entries_when_db_available():
    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()
    fake_db = FakeProjectionRegistryDb()

    result = read_models.rebuild_finance_projection_store("tenant-wave4", db=fake_db)

    assert result.tenant_id == "tenant-wave4"
    assert any("INSERT INTO domain_shared.process_projection_registry" in sql for sql, _ in fake_db.commands)
    assert any("INSERT INTO domain_shared.process_projection_snapshots" in sql for sql, _ in fake_db.commands)
    assert any("INSERT INTO domain_shared.process_projection_cursors" in sql for sql, _ in fake_db.commands)


# ---------------------------------------------------------------------------
# 5. TestClient — ap-invoice-cockpit endpoint returns 200 with correct schema
# ---------------------------------------------------------------------------

def test_ap_invoice_cockpit_endpoint_returns_200():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    # Build a minimal app with just the read-models router
    app = FastAPI()
    app.include_router(read_models.router)

    # Override get_tenant_id dependency to bypass header requirement
    from app.core.tenant import get_tenant_id
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-wave2"

    with TestClient(app) as client:
        response = client.get("/finance/read-models/ap-invoice-cockpit")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-wave2"
    assert body["schema_version"] == 1
    assert isinstance(body["buckets"], list)
    assert "total_count" in body
    assert "pending_approval_count" in body
    assert "ready_to_post_count" in body
    assert "overdue_count" in body


def test_process_observation_endpoint_returns_sla_profiles():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(read_models.router)

    from app.core.tenant import get_tenant_id
    from app.core.database import get_db

    app.dependency_overrides[get_tenant_id] = lambda: "tenant-wave2"
    app.dependency_overrides[get_db] = lambda: None

    with TestClient(app) as client:
        response = client.get("/finance/read-models/process-observation")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-wave2"
    assert body["schema_version"] == 1
    assert "sla_profiles" in body
    assert "overdue_instances" in body
    assert isinstance(body["sla_profiles"], list)
    assert any(profile["process_key"] == "annahme" for profile in body["sla_profiles"])


def test_rebuild_endpoint_returns_projection_summary():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    read_models._PROJECTION_STORE.clear()

    app = FastAPI()
    app.include_router(read_models.router)

    from app.core.tenant import get_tenant_id
    from app.core.database import get_db

    app.dependency_overrides[get_tenant_id] = lambda: "tenant-wave2"
    app.dependency_overrides[get_db] = lambda: None

    with TestClient(app) as client:
        response = client.post("/finance/read-models/_rebuild")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-wave2"
    assert body["schema_version"] == 1
    assert any(entry["projection_key"] == "cash-closings/detail" for entry in body["projections"])


def test_status_endpoint_returns_projection_metrics():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    read_models._PROJECTION_STORE.clear()
    read_models._PROJECTION_META.clear()

    app = FastAPI()
    app.include_router(read_models.router)

    from app.core.tenant import get_tenant_id
    from app.core.database import get_db

    app.dependency_overrides[get_tenant_id] = lambda: "tenant-wave2"
    app.dependency_overrides[get_db] = lambda: None

    with TestClient(app) as client:
        rebuild_response = client.post("/finance/read-models/_rebuild")
        assert rebuild_response.status_code == 200

        client.get("/finance/read-models/cash-closings/unknown")
        response = client.get("/finance/read-models/_status")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-wave2"
    assert body["schema_version"] == 1
    assert body["projection_count"] >= 6
    assert body["persisted_snapshot_count"] == 0
    assert body["persisted_cursor_count"] == 0
    assert body["cache_misses"] >= 1
    assert body["last_rebuilt_at"] is not None
    assert body["last_snapshot_at"] is None
    assert body["last_cursor_advanced_at"] is None
    assert body["last_processed_event_id"] is None
    assert any(entry["projection_key"] == "ap-invoice-cockpit" for entry in body["projections"])
