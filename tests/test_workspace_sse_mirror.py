"""Pure Unit-Tests: Ist-Events auf stream=workspace spiegeln (kein DB, kein MagicMock-DB)."""

from __future__ import annotations

import asyncio
from datetime import datetime

import pytest

from app.core.sse import SSEHub
from app.domains.shared.events import IntegrationEvent
from app.domains.shared.process_events import APInvoiceApprovalRequested
from app.infrastructure.eventbus.nats_consumer import NATSEventConsumer
from app.workspace.events import (
    IST_TO_SOLL,
    handle_nats_event_for_workspace,
    mirror_ist_event_to_workspace,
    project_workspace_event,
    publish_workspace_sse,
    register_workspace_sse_mirror,
    reset_workspace_sse_dedup,
    resolve_ist_event_type,
    should_mirror_ist_event,
)

ON_STREAM = (
    "logistik.tour.created",
    "lkw.registered",
    "LOADING_STARTED",
    "LOADING_FINISHED",
    "finance.ap_invoice.approved",
    "finance.ap_invoice.approval_granted",
    "finance.ap_invoice.approval_requested",
    "finance.ap_invoice.posted",
    "goods_receipt.created",
    "docflow.document.posted",
    "sales.invoice.posted",
    "sales.invoice.proposed",
    "sales.gutschrift.proposed",
    "lager.einlagerung.created",
    "agrar.weighing_ticket.allocated",
    "agrar.quality_protocol.completed",
)

OFF_STREAM = (
    "sales.offer.created",
    "agrar.contract.reminder.create",
    "assignment_confirmed",
    "document_proposed",
    "document_posted",
    "audit.entry_created",
    "inventory.movement_created",
    # Kurzform ohne Domain — kein Ist-Key
    "quality_protocol.completed",
    # Waage-Begleiter / nicht Wiegeschein-Typ
    "agrar.contract.allocated",
)


@pytest.fixture(autouse=True)
def _clear_sse_dedup() -> None:
    reset_workspace_sse_dedup()


@pytest.mark.unit
@pytest.mark.parametrize("ist_type", ON_STREAM)
def test_mapped_ist_types_resolve_without_rename(ist_type: str) -> None:
    assert resolve_ist_event_type(ist_type) == ist_type
    envelope = project_workspace_event(ist_type, tenant_id="t-1")
    assert envelope is not None
    assert envelope["type"] == ist_type
    assert envelope["event_type"] == ist_type
    assert envelope["canonical"] == IST_TO_SOLL[ist_type]
    assert envelope["canonical"] not in ON_STREAM
    assert envelope["wired"] is True
    assert envelope["stream"] == "workspace"


@pytest.mark.unit
@pytest.mark.parametrize("ist_type", OFF_STREAM)
def test_unmapped_and_soll_names_stay_off_stream(ist_type: str) -> None:
    assert resolve_ist_event_type(ist_type) is None
    assert project_workspace_event(ist_type, tenant_id="t-1") is None
    assert should_mirror_ist_event(ist_type) is False


@pytest.mark.unit
def test_process_kernel_and_tenant_subject_resolve_to_ist_name() -> None:
    assert resolve_ist_event_type("APInvoiceApprovalRequested") == "finance.ap_invoice.approval_requested"
    assert resolve_ist_event_type("QualityProtocolCompleted") == "agrar.quality_protocol.completed"
    assert (
        resolve_ist_event_type("tenant-a.finance.ap_invoice.approval_requested")
        == "finance.ap_invoice.approval_requested"
    )
    assert (
        resolve_ist_event_type("tenant1.agrar.quality_protocol.completed")
        == "agrar.quality_protocol.completed"
    )
    event = APInvoiceApprovalRequested(
        aggregate_id="inv-1",
        timestamp=datetime.utcnow(),
        tenant_id="t-1",
        invoice_id="inv-1",
        requested_by="user-1",
        required_approvals=2,
        rule_id="ap.approval.default",
    )
    assert resolve_ist_event_type(event) == "finance.ap_invoice.approval_requested"


@pytest.mark.unit
def test_hub_receives_ist_type_not_soll_name() -> None:
    async def exercise() -> None:
        hub = SSEHub()
        queue = await hub.subscribe("workspace", tenant_id="t-1")
        other = await hub.subscribe("workspace", tenant_id="t-2")
        envelope = await publish_workspace_sse(
            "logistik.tour.created",
            tenant_id="t-1",
            payload={"id": "tour-1"},
            event_id="evt-1",
            hub=hub,
        )
        assert envelope is not None
        delivered = queue.get_nowait()
        assert delivered["type"] == "logistik.tour.created"
        assert delivered["event_type"] == "logistik.tour.created"
        assert delivered["canonical"] == "assignment_confirmed"
        assert delivered["payload"]["id"] == "tour-1"
        assert other.empty()
        skipped = await publish_workspace_sse(
            "sales.offer.created",
            tenant_id="t-1",
            hub=hub,
        )
        assert skipped is None
        assert queue.empty()
        await hub.unsubscribe("workspace", queue, tenant_id="t-1")
        await hub.unsubscribe("workspace", other, tenant_id="t-2")

    asyncio.run(exercise())


@pytest.mark.unit
def test_mirror_from_integration_event_and_dedup() -> None:
    async def exercise() -> None:
        hub = SSEHub()
        queue = await hub.subscribe("workspace", tenant_id="tenant-a")
        event = IntegrationEvent(
            aggregate_id="gr-1",
            timestamp=datetime.utcnow(),
            event_id="outbox-1",
            event_type="goods_receipt.created",
            payload={"id": "gr-1"},
        )
        first = await mirror_ist_event_to_workspace(event, tenant_id="tenant-a", hub=hub)
        second = await mirror_ist_event_to_workspace(event, tenant_id="tenant-a", hub=hub)
        assert first is not None
        assert first["event_type"] == "goods_receipt.created"
        assert second is None
        assert queue.get_nowait()["event_type"] == "goods_receipt.created"
        assert queue.empty()
        await hub.unsubscribe("workspace", queue, tenant_id="tenant-a")

    asyncio.run(exercise())


@pytest.mark.unit
def test_nats_handler_mirrors_docflow_and_approval_requested() -> None:
    async def exercise() -> None:
        hub = SSEHub()
        queue = await hub.subscribe("workspace", tenant_id="t-9")
        await handle_nats_event_for_workspace(
            {
                "event_type": "docflow.document.posted",
                "event_id": "nats-1",
                "tenant_id": "t-9",
                "payload": {"document_id": "doc-1"},
            },
            hub=hub,
        )
        await handle_nats_event_for_workspace(
            {
                "event_type": "finance.ap_invoice.approval_requested",
                "event_id": "nats-2",
                "tenant_id": "t-9",
                "payload": {"invoice_id": "inv-9"},
            },
            hub=hub,
        )
        first = queue.get_nowait()
        second = queue.get_nowait()
        assert first["type"] == "docflow.document.posted"
        assert second["type"] == "finance.ap_invoice.approval_requested"
        await hub.unsubscribe("workspace", queue, tenant_id="t-9")

    asyncio.run(exercise())


class _FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, obj: object) -> None:
        self.added.append(obj)


@pytest.mark.unit
def test_outbox_store_event_defers_ist_type_until_committed_worker() -> None:
    async def exercise() -> None:
        from app.core.sse import sse_hub
        from app.infrastructure.eventbus.outbox import OutboxPublisher

        queue = await sse_hub.subscribe("workspace", tenant_id="t-outbox")
        try:
            outbox = OutboxPublisher(_FakeSession(), event_publisher=None)
            event = IntegrationEvent(
                aggregate_id="lkw-1",
                timestamp=datetime.utcnow(),
                event_id="outbox-lkw-1",
                event_type="lkw.registered",
                payload={"id": "lkw-1"},
            )
            await outbox.store_event(event, tenant_id="t-outbox")
            assert queue.empty(), "Uncommitted rows must not produce SSE"
            assert outbox.db.added[0].event_type == "lkw.registered"
        finally:
            await sse_hub.unsubscribe("workspace", queue, tenant_id="t-outbox")

    asyncio.run(exercise())


@pytest.mark.unit
@pytest.mark.parametrize("ist_type", ("LOADING_STARTED", "LOADING_FINISHED"))
def test_outbox_store_event_defers_loading_ist_until_committed_worker(ist_type: str) -> None:
    async def exercise() -> None:
        from app.core.sse import sse_hub
        from app.infrastructure.eventbus.outbox import OutboxPublisher

        queue = await sse_hub.subscribe("workspace", tenant_id="t-loading")
        try:
            outbox = OutboxPublisher(_FakeSession(), event_publisher=None)
            event = IntegrationEvent(
                aggregate_id="tour-1",
                timestamp=datetime.utcnow(),
                event_id=f"outbox-{ist_type}",
                event_type=ist_type,
                payload={"id": "tour-1", "tour_id": "tour-1"},
            )
            await outbox.store_event(event, tenant_id="t-loading")
            assert queue.empty(), "Uncommitted rows must not produce SSE"
            assert outbox.db.added[0].event_type == ist_type
        finally:
            await sse_hub.unsubscribe("workspace", queue, tenant_id="t-loading")

    asyncio.run(exercise())


@pytest.mark.unit
def test_outbox_store_event_defers_quality_protocol_until_committed_worker() -> None:
    async def exercise() -> None:
        from app.core.sse import sse_hub
        from app.infrastructure.eventbus.outbox import OutboxPublisher

        queue = await sse_hub.subscribe("workspace", tenant_id="t-qs")
        try:
            outbox = OutboxPublisher(_FakeSession(), event_publisher=None)
            event = IntegrationEvent(
                aggregate_id="qp-1",
                timestamp=datetime.utcnow(),
                event_id="outbox-qp-1",
                event_type="agrar.quality_protocol.completed",
                payload={"protocol_id": "qp-1", "is_final": True},
            )
            await outbox.store_event(event, tenant_id="t-qs")
            assert queue.empty(), "Uncommitted rows must not produce SSE"
            assert outbox.db.added[0].event_type == "agrar.quality_protocol.completed"
        finally:
            await sse_hub.unsubscribe("workspace", queue, tenant_id="t-qs")

    asyncio.run(exercise())


class _RecordingPublisher:
    def __init__(self) -> None:
        self.published: list[IntegrationEvent] = []

    async def publish(self, event: IntegrationEvent) -> None:
        self.published.append(event)


class _PendingQuery:
    def __init__(self, rows: list[object]) -> None:
        self._rows = rows

    def filter(self, *_args: object, **_kwargs: object) -> "_PendingQuery":
        return self

    def order_by(self, *_args: object) -> "_PendingQuery":
        return self

    def limit(self, *_args: object) -> "_PendingQuery":
        return self

    def all(self) -> list[object]:
        return self._rows


class _PendingSession(_FakeSession):
    def __init__(self, rows: list[object]) -> None:
        super().__init__()
        self._rows = rows
        self.committed = False

    def query(self, *_args: object) -> _PendingQuery:
        return _PendingQuery(self._rows)

    def commit(self) -> None:
        self.committed = True


class _PendingOutboxRow:
    """Minimaler Outbox-Eintrag fuer publish_pending ohne SQLAlchemy-Session."""

    def __init__(self, *, event_type: str) -> None:
        import json

        self.id = f"pending-{event_type}"
        self.event_type = event_type
        self.aggregate_id = "tour-pending-1"
        self.payload = json.dumps(
            {
                "aggregate_id": "tour-pending-1",
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"pending-{event_type}",
                "event_type": event_type,
                "payload": {"id": "tour-pending-1", "tour_id": "tour-pending-1"},
            }
        )
        self.timestamp = datetime.utcnow()
        self.published = False
        self.published_at = None
        self.retry_count = 0
        self.tenant_id = "t-pending"


@pytest.mark.unit
@pytest.mark.parametrize("ist_type", ("LOADING_STARTED", "LOADING_FINISHED"))
def test_publish_pending_keeps_loading_event_type_for_nats(ist_type: str) -> None:
    """LOADING_* liegt in outbox_events; publish_pending reicht event_type an den Bus weiter."""
    from app.infrastructure.eventbus.outbox import OutboxPublisher

    async def exercise() -> None:
        reset_workspace_sse_dedup()
        entry = _PendingOutboxRow(event_type=ist_type)
        publisher = _RecordingPublisher()
        outbox = OutboxPublisher(_PendingSession([entry]), publisher)
        count = await outbox.publish_pending_events(limit=10)
        assert count == 1
        assert len(publisher.published) == 1
        assert publisher.published[0].event_type == ist_type
        assert entry.published is True
        assert outbox.db.committed is True

    asyncio.run(exercise())


@pytest.mark.unit
def test_register_workspace_sse_mirror_is_additive() -> None:
    consumer = NATSEventConsumer(enabled=False)
    seen: list[str] = []

    async def existing(event: dict) -> None:
        seen.append(str(event.get("event_type")))

    consumer.register_handler("audit.entry_created", existing)
    register_workspace_sse_mirror(consumer)
    assert "logistik.tour.created" in consumer._handlers
    assert "finance.ap_invoice.approval_requested" in consumer._handlers
    assert handle_nats_event_for_workspace in consumer._default_handlers
    assert existing in consumer._handlers["audit.entry_created"]
    assert handle_nats_event_for_workspace not in consumer._handlers["audit.entry_created"]
