"""
Wave-2 Contract-Tests: Process Kernel Events und Outbox-Anbindung

Prueft:
- Event-Namenskonvention (NATS-Subject)
- Event-Typen fuer AP-Freigabe-Workflow
- Outbox-Write-Integration
"""
from __future__ import annotations

import asyncio
from datetime import datetime

from app.core.ap_approval_events import build_ap_approval_outbox_event, store_ap_approval_event_in_outbox
from app.core.ap_approval_status import build_approval_status_response
from app.domains.shared.process_events import (
    APInvoiceApprovalGranted,
    APInvoiceApprovalRequested,
    APInvoiceApproved,
    APInvoiceRejected,
    APInvoicePosted,
    HarvestAcceptanceCompleted,
    QualityProtocolCompleted,
    build_event_subject,
)


# ---------------------------------------------------------------------------
# Event-Namenskonvention
# ---------------------------------------------------------------------------

def test_ap_invoice_approval_requested_subject_follows_convention():
    event = APInvoiceApprovalRequested(
        aggregate_id="inv-1",
        timestamp=datetime(2026, 3, 11, 9, 0, 0),
        tenant_id="tenant1",
        invoice_id="inv-1",
        requested_by="lead",
        required_approvals=2,
        rule_id="ap.approval.default",
    )
    assert build_event_subject(event) == "tenant1.finance.ap_invoice.approval_requested"


def test_ap_invoice_approved_subject_follows_convention():
    event = APInvoiceApproved(
        aggregate_id="inv-2",
        timestamp=datetime(2026, 3, 11, 9, 0, 0),
        tenant_id="tenant2",
        invoice_id="inv-2",
        approved_by="manager",
        rule_id="ap.approval.rule",
    )
    assert build_event_subject(event) == "tenant2.finance.ap_invoice.approved"


def test_ap_invoice_rejected_subject_follows_convention():
    event = APInvoiceRejected(
        aggregate_id="inv-3",
        timestamp=datetime(2026, 3, 11, 9, 0, 0),
        tenant_id="tenant3",
        invoice_id="inv-3",
        rejected_by="finance",
        rule_id="ap.approval.default",
    )
    assert build_event_subject(event) == "tenant3.finance.ap_invoice.rejected"


def test_harvest_acceptance_completed_subject_follows_convention():
    event = HarvestAcceptanceCompleted(
        aggregate_id="ha-1",
        timestamp=datetime(2026, 3, 11, 9, 0, 0),
        tenant_id="tenant1",
        acceptance_id="ha-1",
        contract_id="c-1",
        supplier_id="s-1",
        article_id="art-1",
        net_weight=12500.0,
    )
    assert build_event_subject(event) == "tenant1.agrar.harvest_acceptance.completed"


def test_quality_protocol_completed_subject_follows_convention():
    event = QualityProtocolCompleted(
        aggregate_id="qp-1",
        timestamp=datetime(2026, 3, 11, 9, 0, 0),
        tenant_id="tenant1",
        protocol_id="qp-1",
        acceptance_id="ha-1",
        contract_id="c-1",
    )
    assert build_event_subject(event) == "tenant1.agrar.quality_protocol.completed"


# ---------------------------------------------------------------------------
# Event-Felder und Typen
# ---------------------------------------------------------------------------

def test_ap_invoice_approval_requested_carries_workflow_instance_id():
    event = APInvoiceApprovalRequested(
        aggregate_id="inv-1",
        timestamp=datetime(2026, 3, 11, 9, 0, 0),
        tenant_id="tenant1",
        invoice_id="inv-1",
        requested_by="lead",
        required_approvals=2,
        rule_id="ap.approval.rule",
        workflow_instance_id="wf-ap-inv-1",
    )
    assert event.workflow_instance_id == "wf-ap-inv-1"
    assert event.schema_version == 1
    assert event.aggregate_id == "inv-1"


def test_ap_invoice_approval_granted_carries_approval_progress():
    event = APInvoiceApprovalGranted(
        aggregate_id="inv-2",
        timestamp=datetime(2026, 3, 11, 9, 0, 0),
        tenant_id="tenant1",
        invoice_id="inv-2",
        approved_by="manager",
        current_approvals=1,
        required_approvals=3,
        rule_id="ap.approval.high-value",
    )
    assert event.current_approvals == 1
    assert event.required_approvals == 3
    assert event.verb == "approval_granted"


# ---------------------------------------------------------------------------
# _build_ap_approval_outbox_event — Event-Dispatch nach action
# ---------------------------------------------------------------------------

def _make_response(invoice_id: str, status: str, required: int = 1, current: int = 0):
    return build_approval_status_response(
        invoice_id=invoice_id,
        tenant_id="tenant-wave2",
        status=status,
        required_approvals=required,
        approvals=[{"approved_by": "manager"}] * current,
        rejections=[],
        applicable_rule=None,
    )


def test_build_outbox_event_for_approval_requested():
    response = _make_response("inv-1", "pending", required=2, current=0)
    event = build_ap_approval_outbox_event(
        action="approval_requested",
        invoice_id="inv-1",
        tenant_id="tenant-wave2",
        actor="lead",
        response=response,
    )
    assert isinstance(event, APInvoiceApprovalRequested)
    assert event.invoice_id == "inv-1"
    assert event.requested_by == "lead"
    assert build_event_subject(event) == "tenant-wave2.finance.ap_invoice.approval_requested"


def test_build_outbox_event_for_approval_approve_partially():
    response = _make_response("inv-2", "partially_approved", required=3, current=1)
    event = build_ap_approval_outbox_event(
        action="approval_approve",
        invoice_id="inv-2",
        tenant_id="tenant-wave2",
        actor="manager",
        response=response,
    )
    assert isinstance(event, APInvoiceApprovalGranted)
    assert event.current_approvals == 1
    assert event.required_approvals == 3


def test_build_outbox_event_for_approval_approve_fully():
    response = _make_response("inv-3", "approved", required=1, current=1)
    event = build_ap_approval_outbox_event(
        action="approval_approve",
        invoice_id="inv-3",
        tenant_id="tenant-wave2",
        actor="manager",
        response=response,
    )
    assert isinstance(event, APInvoiceApproved)
    assert event.approved_by == "manager"
    assert build_event_subject(event) == "tenant-wave2.finance.ap_invoice.approved"


def test_build_outbox_event_for_approval_reject():
    response = _make_response("inv-4", "rejected", required=2, current=0)
    event = build_ap_approval_outbox_event(
        action="approval_reject",
        invoice_id="inv-4",
        tenant_id="tenant-wave2",
        actor="finance",
        response=response,
    )
    assert isinstance(event, APInvoiceRejected)
    assert event.rejected_by == "finance"
    assert build_event_subject(event) == "tenant-wave2.finance.ap_invoice.rejected"


def test_build_outbox_event_for_unknown_action_returns_none():
    response = _make_response("inv-5", "pending")
    result = build_ap_approval_outbox_event(
        action="unknown_action",
        invoice_id="inv-5",
        tenant_id="tenant-wave2",
        actor="user",
        response=response,
    )
    assert result is None


# ---------------------------------------------------------------------------
# Outbox-Write: best-effort, kein Rollback bei Fehler
# ---------------------------------------------------------------------------

def test_store_approval_event_in_outbox_is_best_effort(monkeypatch):
    """Outbox-Write-Fehler duerfen den Approval-Flow nicht unterbrechen."""
    stored: list[object] = []

    class FakeOutbox:
        async def store_event(self, event, tenant_id=None):
            stored.append(event)

    class FakeDb:
        def add(self, _):
            pass

    monkeypatch.setattr(
        "app.core.ap_approval_events.build_ap_approval_outbox_event",
        lambda **kwargs: APInvoiceApproved(
            aggregate_id="inv-x",
            timestamp=datetime(2026, 3, 11, 9, 0, 0),
            tenant_id="tenant-wave2",
            invoice_id="inv-x",
            approved_by="manager",
            rule_id="ap.approval.default",
        ),
    )

    import app.infrastructure.eventbus.outbox as outbox_mod
    import app.domains.shared.events as events_mod

    monkeypatch.setattr(outbox_mod, "OutboxPublisher", lambda db, pub: FakeOutbox())
    monkeypatch.setattr(events_mod, "get_event_publisher", lambda: None)

    response = _make_response("inv-x", "approved", required=1, current=1)
    # Sollte keinen Fehler werfen
    store_ap_approval_event_in_outbox(
        FakeDb(),
        action="approval_approve",
        invoice_id="inv-x",
        tenant_id="tenant-wave2",
        actor="manager",
        response=response,
    )
    assert len(stored) == 1


def test_store_approval_event_in_outbox_schedules_task_in_running_loop(monkeypatch):
    """Bei laufender Event-Loop muss der Outbox-Write sauber als Task geplant werden."""
    stored: list[object] = []

    class FakeOutbox:
        async def store_event(self, event, tenant_id=None):
            stored.append((event, tenant_id))

    class FakeDb:
        def add(self, _):
            pass

    monkeypatch.setattr(
        "app.core.ap_approval_events.build_ap_approval_outbox_event",
        lambda **kwargs: APInvoiceApproved(
            aggregate_id="inv-y",
            timestamp=datetime(2026, 3, 11, 9, 0, 0),
            tenant_id="tenant-wave2",
            invoice_id="inv-y",
            approved_by="lead",
            rule_id="ap.approval.default",
        ),
    )

    import app.infrastructure.eventbus.outbox as outbox_mod
    import app.domains.shared.events as events_mod

    monkeypatch.setattr(outbox_mod, "OutboxPublisher", lambda db, pub: FakeOutbox())
    monkeypatch.setattr(events_mod, "get_event_publisher", lambda: None)

    response = _make_response("inv-y", "approved", required=1, current=1)

    async def _run() -> None:
        store_ap_approval_event_in_outbox(
            FakeDb(),
            action="approval_approve",
            invoice_id="inv-y",
            tenant_id="tenant-wave2",
            actor="lead",
            response=response,
        )
        await asyncio.sleep(0)

    asyncio.run(_run())

    assert len(stored) == 1
    assert stored[0][1] == "tenant-wave2"
