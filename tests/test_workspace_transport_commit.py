"""Durable workspace transport: committed outbox, trusted tenant and NATS wire format.

SQLite lives only in memory. No PostgreSQL database or container is created.
"""
import asyncio
import json
from datetime import datetime
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.domains.shared.events import IntegrationEvent
from app.infrastructure.eventbus.nats_publisher import NATSEventPublisher
from app.infrastructure.eventbus.outbox import OutboxEvent, OutboxPublisher
from app.workspace.events import handle_nats_event_for_workspace, reset_workspace_sse_dedup


@pytest.fixture
def engine():
    database = create_engine("sqlite://", poolclass=StaticPool,
                             connect_args={"check_same_thread": False})
    OutboxEvent.__table__.create(database)
    yield database
    database.dispose()


def _event(*, tenant_id="tenant-own", event_id="evt-workspace-1"):
    return IntegrationEvent(
        aggregate_id="invoice-1", timestamp=datetime(2026, 10, 23, 12, 0),
        event_id=event_id, event_type="finance.ap_invoice.posted",
        tenant_id=tenant_id,
        payload={"invoice_id": "invoice-1", "status": "POSTED"},
    )


class CaptureJetStream:
    def __init__(self, error=None):
        self.messages = []
        self.error = error

    async def publish(self, subject, body):
        if self.error:
            raise self.error
        self.messages.append((subject, json.loads(body)))
        return SimpleNamespace(stream="TEST", seq=len(self.messages))


class CaptureHub:
    def __init__(self):
        self.calls = []

    async def broadcast(self, channel, envelope, *, tenant_id):
        self.calls.append((channel, envelope, tenant_id))


def _publisher(js=None):
    publisher = NATSEventPublisher(enabled=True)
    publisher._connected = js is not None
    publisher._js = js
    return publisher


def test_outbox_store_commit_and_rollback_are_durable(engine):
    with Session(engine) as db:
        asyncio.run(OutboxPublisher(db, _publisher()).store_event(
            _event(event_id="rolled-back"), tenant_id="tenant-own", mirror_on_store=False))
        db.rollback()
    with Session(engine) as verify:
        assert verify.scalars(select(OutboxEvent)).all() == []

    with Session(engine) as db:
        asyncio.run(OutboxPublisher(db, _publisher()).store_event(
            _event(), tenant_id="tenant-own", mirror_on_store=False))
        db.commit()
    with Session(engine) as verify:
        stored = verify.scalars(select(OutboxEvent)).one()
        assert stored.id == "evt-workspace-1"
        assert stored.tenant_id == "tenant-own" and stored.published is False


def test_committed_outbox_nats_wire_reaches_actual_workspace_handler(engine, monkeypatch):
    async def no_early_mirror(*args, **kwargs):
        return None
    monkeypatch.setattr("app.infrastructure.eventbus.outbox._mirror_workspace_sse", no_early_mirror)
    reset_workspace_sse_dedup()
    with Session(engine) as db:
        asyncio.run(OutboxPublisher(db, _publisher()).store_event(
            _event(), tenant_id="tenant-own", mirror_on_store=False))
        db.commit()

    js = CaptureJetStream()
    with Session(engine) as db:
        assert asyncio.run(OutboxPublisher(db, _publisher(js)).publish_pending_events()) == 1
        stored = db.get(OutboxEvent, "evt-workspace-1")
        assert stored.published is True and stored.published_at is not None
    assert len(js.messages) == 1
    subject, wire = js.messages[0]
    assert subject.startswith("domain.")
    assert wire["event_type"] == "finance.ap_invoice.posted"
    assert wire["tenant_id"] == "tenant-own"
    assert wire["event_id"] == "evt-workspace-1"
    assert wire["payload"] == {"invoice_id": "invoice-1", "status": "POSTED"}

    hub = CaptureHub()
    asyncio.run(handle_nats_event_for_workspace(wire, hub=hub))
    assert len(hub.calls) == 1
    channel, envelope, tenant = hub.calls[0]
    assert channel == "workspace" and tenant == "tenant-own"
    assert envelope["event_type"] == "finance.ap_invoice.posted"
    assert envelope["payload"] == wire["payload"]
    reset_workspace_sse_dedup()


@pytest.mark.parametrize("failure", ["disconnected", "transport"])
def test_enabled_transport_failure_never_marks_outbox_published(engine, failure):
    with Session(engine) as db:
        asyncio.run(OutboxPublisher(db, _publisher()).store_event(
            _event(), tenant_id="tenant-own", mirror_on_store=False))
        db.commit()
    js = CaptureJetStream(error=RuntimeError("NATS offline")) if failure == "transport" else None
    with Session(engine) as db:
        outbox = OutboxPublisher(db, _publisher(js))
        for attempt in range(1, 4):
            assert asyncio.run(outbox.publish_pending_events()) == 0
            db.expire_all()
            row = db.get(OutboxEvent, "evt-workspace-1")
            assert row.retry_count == attempt
            assert row.published is False and row.published_at is None
    assert js is None or js.messages == []


def test_store_rejects_conflicting_event_and_verified_tenant(engine):
    with Session(engine) as db:
        with pytest.raises(ValueError):
            asyncio.run(OutboxPublisher(db, _publisher()).store_event(
                _event(tenant_id="tenant-foreign"), tenant_id="tenant-own", mirror_on_store=False))
        db.rollback()
    with Session(engine) as verify:
        assert verify.scalars(select(OutboxEvent)).all() == []


def test_store_rejects_conflicting_business_payload_tenant_and_early_mirror(engine):
    event = _event()
    event.payload["tenant_id"] = "tenant-foreign"
    with Session(engine) as db:
        with pytest.raises(ValueError):
            asyncio.run(OutboxPublisher(db, _publisher()).store_event(
                event, tenant_id="tenant-own", mirror_on_store=False))
        with pytest.raises(ValueError):
            asyncio.run(OutboxPublisher(db, _publisher()).store_event(
                _event(), tenant_id="tenant-own", mirror_on_store=True))
        db.rollback()
    with Session(engine) as verify:
        assert verify.scalars(select(OutboxEvent)).all() == []


@pytest.mark.parametrize("location", ["event", "business"])
def test_outbox_row_tenant_cannot_be_overridden_by_serialized_payload(engine, monkeypatch, location):
    async def no_early_mirror(*args, **kwargs):
        return None
    monkeypatch.setattr("app.infrastructure.eventbus.outbox._mirror_workspace_sse", no_early_mirror)
    forged = _event(tenant_id="tenant-foreign" if location == "event" else "tenant-own")
    if location == "business":
        forged.payload["tenant_id"] = "tenant-foreign"
    from dataclasses import asdict
    with Session(engine) as db:
        db.add(OutboxEvent(
            id=forged.event_id, event_type=forged.event_type,
            aggregate_id=forged.aggregate_id, timestamp=forged.timestamp,
            payload=json.dumps(asdict(forged), default=str), tenant_id="tenant-own",
            published=False, retry_count=0,
        ))
        db.commit()
    js = CaptureJetStream()
    with Session(engine) as db:
        assert asyncio.run(OutboxPublisher(db, _publisher(js)).publish_pending_events()) == 0
        db.expire_all()
        row = db.get(OutboxEvent, forged.event_id)
        assert row.published is False and row.retry_count == 1
    assert js.messages == []


@pytest.mark.parametrize("event_tenant", [None, "tenant-own"])
def test_direct_nats_publish_rejects_payload_tenant_override(event_tenant):
    js = CaptureJetStream()
    event = _event(tenant_id=event_tenant)
    event.payload["tenant_id"] = "tenant-foreign"
    with pytest.raises(ValueError):
        asyncio.run(_publisher(js).publish(event))
    assert js.messages == []
