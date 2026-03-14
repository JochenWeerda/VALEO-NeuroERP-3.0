"""
Wave-4 Contract-Tests: AP4 Operative Governance + AP5 Finance Follow-up + AP6 Runtime Operations
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.operational_governance import (
    GovernanceAuditEntry,
    GovernanceReviewStatus,
    DelegationReviewEntry,
    ExportReviewEntry,
    OperationalGovernanceStore,
)
from app.core.finance_followup import (
    MahnwesenPreview,
    MahnwesenExportFormat,
    MahnwesenExportResult,
    LastschriftPreview,
    LastschriftExportResult,
)
from app.core.runtime_operations import (
    RuntimeComponent,
    RuntimeHealthReport,
    ComponentHealth,
    ReplayRequest,
    RebuildRequest,
)
from app.api.v1.endpoints import runtime_operations, finance_read_models


# ---------------------------------------------------------------------------
# AP4: Operative Governance
# ---------------------------------------------------------------------------

def test_governance_audit_entry_schema_version():
    entry = GovernanceAuditEntry(
        entry_id="e-1",
        tenant_id="t1",
        governance_type="delegation",
        aggregate_type="agent",
        aggregate_id="agent-42",
        action="delegation_granted",
        actor_id="user-1",
        decision="approved",
    )
    assert entry.schema_version == 1
    assert entry.governance_type == "delegation"


def test_delegation_review_approve_sets_status():
    review = DelegationReviewEntry(
        review_id="r-1",
        tenant_id="t1",
        agent_id="agent-1",
        delegation_scope="APPROVE_INVOICE",
        requested_by="user-1",
    )
    assert review.status == GovernanceReviewStatus.PENDING
    review.approve("supervisor-1")
    assert review.status == GovernanceReviewStatus.APPROVED
    assert review.reviewer_id == "supervisor-1"
    assert review.reviewed_at is not None


def test_delegation_review_reject_sets_status():
    review = DelegationReviewEntry(
        review_id="r-2",
        tenant_id="t1",
        agent_id="agent-2",
        delegation_scope="CREATE_PAYMENT",
        requested_by="user-2",
    )
    review.reject("supervisor-2", reason="Scope too broad")
    assert review.status == GovernanceReviewStatus.REJECTED
    assert review.reviewer_id == "supervisor-2"
    assert review.reviewed_at is not None


def test_governance_store_get_audit_by_type():
    store = OperationalGovernanceStore()
    store.audit_entries.append(
        GovernanceAuditEntry(
            entry_id="a-1",
            tenant_id="t1",
            governance_type="delegation",
            aggregate_type="agent",
            aggregate_id="ag-1",
            action="delegation_granted",
            actor_id="u-1",
            decision="approved",
        )
    )
    store.audit_entries.append(
        GovernanceAuditEntry(
            entry_id="a-2",
            tenant_id="t1",
            governance_type="export",
            aggregate_type="report",
            aggregate_id="rep-1",
            action="export_approved",
            actor_id="u-1",
            decision="approved",
        )
    )
    # Filter by governance_type
    delegation_entries = store.get_audit_entries("t1", governance_type="delegation")
    assert len(delegation_entries) == 1
    assert delegation_entries[0].entry_id == "a-1"

    # Filter by different tenant
    other_tenant = store.get_audit_entries("t2")
    assert len(other_tenant) == 0

    # All entries for t1
    all_entries = store.get_audit_entries("t1")
    assert len(all_entries) == 2


def test_governance_store_get_pending_delegation_reviews():
    store = OperationalGovernanceStore()
    pending = DelegationReviewEntry(
        review_id="r-pending",
        tenant_id="t1",
        agent_id="ag-1",
        delegation_scope="READ",
        requested_by="u-1",
        status=GovernanceReviewStatus.PENDING,
    )
    approved = DelegationReviewEntry(
        review_id="r-approved",
        tenant_id="t1",
        agent_id="ag-2",
        delegation_scope="WRITE",
        requested_by="u-2",
        status=GovernanceReviewStatus.APPROVED,
    )
    store.delegation_reviews.extend([pending, approved])

    result = store.get_pending_delegation_reviews("t1")
    assert len(result) == 1
    assert result[0].review_id == "r-pending"


def test_governance_store_get_pending_export_reviews():
    store = OperationalGovernanceStore()
    pending_export = ExportReviewEntry(
        review_id="ex-1",
        tenant_id="t1",
        export_type="financial_report",
        target_zone="EU",
        classification="gobd_relevant",
        requested_by="u-1",
        status=GovernanceReviewStatus.PENDING,
    )
    rejected_export = ExportReviewEntry(
        review_id="ex-2",
        tenant_id="t1",
        export_type="customer_data",
        target_zone="non_EU",
        classification="gdpr_personal",
        requested_by="u-2",
        status=GovernanceReviewStatus.REJECTED,
    )
    store.export_reviews.extend([pending_export, rejected_export])

    result = store.get_pending_export_reviews("t1")
    assert len(result) == 1
    assert result[0].review_id == "ex-1"
    assert result[0].schema_version == 1


# ---------------------------------------------------------------------------
# AP5: Finance Follow-up
# ---------------------------------------------------------------------------

def test_mahnwesen_preview_schema_version():
    preview = MahnwesenPreview(
        tenant_id="t1",
        open_items_count=5,
        total_overdue_amount=12500.50,
        dunning_level_counts={"1": 3, "2": 2, "3": 0},
        export_ready=True,
    )
    assert preview.schema_version == 1
    assert preview.export_ready is True
    assert preview.dunning_level_counts["1"] == 3


def test_mahnwesen_export_result_schema_version():
    result = MahnwesenExportResult(
        export_id="exp-1",
        tenant_id="t1",
        format=MahnwesenExportFormat.PDF,
        record_count=5,
    )
    assert result.schema_version == 1
    assert result.format == MahnwesenExportFormat.PDF
    assert result.download_url is None
    assert isinstance(result.created_at, datetime)


def test_lastschrift_preview_sepa_ready_field():
    preview = LastschriftPreview(
        tenant_id="t1",
        direct_debit_run_id="run-001",
        total_amount=9800.00,
        debitor_count=10,
        mandate_valid_count=10,
        mandate_expired_count=0,
        sepa_ready=True,
    )
    assert preview.sepa_ready is True
    assert preview.schema_version == 1

    preview_not_ready = LastschriftPreview(
        tenant_id="t1",
        direct_debit_run_id="run-002",
        total_amount=5000.00,
        debitor_count=5,
        mandate_valid_count=3,
        mandate_expired_count=2,
        sepa_ready=False,
    )
    assert preview_not_ready.sepa_ready is False


def test_lastschrift_export_result_format():
    result = LastschriftExportResult(
        export_id="exp-2",
        tenant_id="t1",
        direct_debit_run_id="run-001",
        record_count=10,
    )
    assert result.format == "sepa_xml"
    assert result.schema_version == 1
    assert result.download_url is None


# ---------------------------------------------------------------------------
# AP6: Runtime Operations
# ---------------------------------------------------------------------------

def test_runtime_health_report_build_default():
    report = RuntimeHealthReport.build_default("t1")
    assert report.tenant_id == "t1"
    assert len(report.components) == 4
    component_ids = {c.component_id for c in report.components}
    assert "wf-engine-01" in component_ids
    assert "outbox-01" in component_ids
    assert "proj-consumer-01" in component_ids
    assert "sla-monitor-01" in component_ids


def test_runtime_health_report_schema_version():
    report = RuntimeHealthReport.build_default("t1")
    assert report.schema_version == 1
    for component in report.components:
        assert component.schema_version == 1


def test_runtime_health_compute_overall_healthy():
    report = RuntimeHealthReport.build_default("t1")
    # All components healthy by default
    overall = report.compute_overall_health()
    assert overall == ComponentHealth.HEALTHY


def test_runtime_health_compute_overall_degraded():
    report = RuntimeHealthReport.build_default("t1")
    # Mark one component as degraded
    report.components[0].health = ComponentHealth.DEGRADED
    overall = report.compute_overall_health()
    assert overall == ComponentHealth.DEGRADED


def test_runtime_health_compute_overall_unhealthy():
    report = RuntimeHealthReport.build_default("t1")
    # Mark one component as unhealthy — should override degraded
    report.components[0].health = ComponentHealth.DEGRADED
    report.components[1].health = ComponentHealth.UNHEALTHY
    overall = report.compute_overall_health()
    assert overall == ComponentHealth.UNHEALTHY


def test_replay_request_schema_version():
    req = ReplayRequest(
        replay_id="rpl-1",
        tenant_id="t1",
        target_type="projection",
        target_id="invoice-projection",
        requested_by="admin",
        reason="Data inconsistency detected",
    )
    assert req.schema_version == 1
    assert req.status == "pending"
    assert req.from_event_id is None
    assert req.to_event_id is None


def test_rebuild_request_schema_version():
    req = RebuildRequest(
        rebuild_id="rbd-1",
        tenant_id="t1",
        projection_name="InvoiceReadModel",
        requested_by="admin",
        reason="Schema migration",
    )
    assert req.schema_version == 1
    assert req.status == "pending"
    assert isinstance(req.created_at, datetime)


def test_runtime_component_default_health():
    comp = RuntimeComponent(
        component_id="test-comp-01",
        component_type="workflow_engine",
    )
    assert comp.health == ComponentHealth.HEALTHY
    assert comp.schema_version == 1
    assert comp.last_heartbeat is None
    assert comp.metrics == {}


def test_runtime_health_endpoint_includes_finance_projection_component():
    finance_read_models._PROJECTION_STORE.clear()
    finance_read_models._PROJECTION_META.clear()
    runtime_operations._replay_requests.clear()
    runtime_operations._rebuild_requests.clear()
    finance_read_models.rebuild_finance_projection_store("t1", db=None)

    app = FastAPI()
    app.include_router(runtime_operations.router)

    from app.core.tenant import get_tenant_id
    from app.core.database import get_db

    app.dependency_overrides[get_tenant_id] = lambda: "t1"
    app.dependency_overrides[get_db] = lambda: None

    with TestClient(app) as client:
        response = client.get("/runtime/health")

    assert response.status_code == 200
    body = response.json()
    finance_component = next(
        component for component in body["components"]
        if component["component_id"] == "finance-projections-01"
    )
    assert body["overall_health"] == "healthy"
    assert finance_component["metrics"]["projection_count"] >= 6
    assert finance_component["metrics"]["persisted_snapshot_count"] == 0
    assert finance_component["metrics"]["persisted_cursor_count"] == 0
    assert finance_component["metrics"]["last_rebuilt_at"] is not None
    assert finance_component["metrics"]["last_snapshot_at"] is None
    assert finance_component["metrics"]["last_cursor_advanced_at"] is None
    assert finance_component["metrics"]["last_event_processed"] is None
    assert finance_component["metrics"]["projection_cursors"] == []


def test_runtime_components_endpoint_exposes_finance_projection_metrics():
    finance_read_models._PROJECTION_STORE.clear()
    finance_read_models._PROJECTION_META.clear()
    runtime_operations._replay_requests.clear()
    runtime_operations._rebuild_requests.clear()

    finance_read_models._load_projection("t1", "missing-projection", finance_read_models.APInvoiceCockpitReadModel)

    app = FastAPI()
    app.include_router(runtime_operations.router)

    from app.core.tenant import get_tenant_id
    from app.core.database import get_db

    app.dependency_overrides[get_tenant_id] = lambda: "t1"
    app.dependency_overrides[get_db] = lambda: None

    with TestClient(app) as client:
        response = client.get("/runtime/components")

    assert response.status_code == 200
    components = response.json()
    finance_component = next(
        component for component in components
        if component["component_id"] == "finance-projections-01"
    )
    assert finance_component["metrics"]["cache_misses"] >= 1
    assert finance_component["metrics"]["cache_hits"] == 0
    assert finance_component["metrics"]["persisted_snapshot_count"] == 0
    assert finance_component["metrics"]["persisted_cursor_count"] == 0
    assert finance_component["metrics"]["last_event_processed"] is None
    assert finance_component["metrics"]["projection_cursors"] == []


def test_replay_request_persists_projection_cursor_when_db_available():
    runtime_operations._replay_requests.clear()

    class FakeDb:
        def __init__(self):
            self.commands = []

        def execute(self, statement, params=None):
            self.commands.append((str(statement), params))

            class _Result:
                def mappings(self):
                    return self

                def all(self):
                    return []

            return _Result()

        def commit(self):
            self.commands.append(("COMMIT", None))

        def rollback(self):
            self.commands.append(("ROLLBACK", None))

    fake_db = FakeDb()

    app = FastAPI()
    app.include_router(runtime_operations.router)

    from app.core.tenant import get_tenant_id
    from app.core.database import get_db

    app.dependency_overrides[get_tenant_id] = lambda: "t1"
    app.dependency_overrides[get_db] = lambda: fake_db

    with TestClient(app) as client:
        response = client.post(
            "/runtime/replay",
            json={
                "target_type": "projection",
                "target_id": "cash-closings",
                "from_event_id": "evt-10",
                "to_event_id": "evt-20",
                "requested_by": "tester",
                "reason": "resume after restart",
            },
        )

    assert response.status_code == 202
    assert any("INSERT INTO domain_shared.process_projection_cursors" in sql for sql, _ in fake_db.commands)


def test_runtime_components_expose_last_processed_event_from_cursor_metadata():
    finance_read_models._PROJECTION_STORE.clear()
    finance_read_models._PROJECTION_META.clear()
    runtime_operations._replay_requests.clear()
    runtime_operations._rebuild_requests.clear()

    class FakeDb:
        def execute(self, statement, params=None):
            sql = str(statement)

            class _Result:
                def __init__(self, rows):
                    self._rows = rows

                def mappings(self):
                    return self

                def all(self):
                    return list(self._rows)

            if "SELECT projection_key, item_count, last_rebuilt_at" in sql:
                return _Result([])
            if "SELECT projection_key, rebuilt_at" in sql:
                return _Result([])
            if "FROM domain_shared.process_projection_cursors" in sql:
                return _Result([
                    {
                        "consumer_id": "finance-projections-01",
                        "projection_key": "process-observation",
                        "updated_at": "2026-03-11T12:00:00+00:00",
                        "last_event_id": "replay-workflow-SO-77-1741694400",
                        "status": "ready",
                        "replay_from_event_id": None,
                        "replay_to_event_id": None,
                    }
                ])
            return _Result([])

        def commit(self):
            return None

        def rollback(self):
            return None

    app = FastAPI()
    app.include_router(runtime_operations.router)

    from app.core.tenant import get_tenant_id
    from app.core.database import get_db

    app.dependency_overrides[get_tenant_id] = lambda: "t1"
    app.dependency_overrides[get_db] = lambda: FakeDb()

    with TestClient(app) as client:
        response = client.get("/runtime/components")

    assert response.status_code == 200
    components = response.json()
    finance_component = next(
        component for component in components
        if component["component_id"] == "finance-projections-01"
    )
    assert finance_component["metrics"]["last_event_processed"] == "replay-workflow-SO-77-1741694400"
    assert finance_component["metrics"]["projection_cursors"] == [
        {
            "projection_key": "process-observation",
            "cursor_status": "ready",
            "cursor_source": "workflow_audit",
            "cursor_updated_at": "2026-03-11T12:00:00+00:00",
            "last_event_processed": "replay-workflow-SO-77-1741694400",
        }
    ]
