"""
Tests for NC-G2: NATS Consumer Framework.
Focus on handler registry and dispatch logic (no NATS runtime).
"""

import asyncio
import json

from app.infrastructure.eventbus.nats_consumer import NATSEventConsumer


class _Metadata:
    def __init__(self, *, num_delivered: int = 1, sequence: int | None = None):
        self.num_delivered = num_delivered
        self.sequence = sequence


class _FakeMessage:
    def __init__(self, payload: dict | str, *, num_delivered: int = 1, sequence: int | None = None):
        if isinstance(payload, str):
            self.data = payload.encode()
        else:
            self.data = json.dumps(payload).encode()
        self.metadata = _Metadata(num_delivered=num_delivered, sequence=sequence)
        self.ack_count = 0
        self.nak_count = 0
        self.term_count = 0

    async def ack(self):
        self.ack_count += 1

    async def nak(self):
        self.nak_count += 1

    async def term(self):
        self.term_count += 1


class TestNATSConsumerHandlers:
    def test_dispatches_registered_handler(self):
        consumer = NATSEventConsumer(enabled=False)
        calls = []

        async def handler(event):
            calls.append(event["event_type"])

        consumer.register_handler("inventory.movement_created", handler)

        asyncio.run(
            consumer.dispatch_event({"event_type": "inventory.movement_created", "payload": {}})
        )
        assert calls == ["inventory.movement_created"]

    def test_dispatches_default_handler_when_no_specific(self):
        consumer = NATSEventConsumer(enabled=False)
        calls = []

        async def handler(event):
            calls.append(event.get("event_type"))

        consumer.register_default_handler(handler)

        asyncio.run(
            consumer.dispatch_event({"event_type": "unknown.event", "payload": {}})
        )
        assert calls == ["unknown.event"]

    def test_ignores_when_no_handlers(self):
        consumer = NATSEventConsumer(enabled=False)
        asyncio.run(consumer.dispatch_event({"event_type": "no.handler"}))

    def test_duplicate_event_id_is_acked_without_handler_replay(self):
        consumer = NATSEventConsumer(enabled=False)
        calls = []

        async def handler(event):
            calls.append(event["event_id"])

        consumer.register_handler("inventory.movement_created", handler)

        first = _FakeMessage({"event_id": "evt-1", "event_type": "inventory.movement_created"})
        second = _FakeMessage({"event_id": "evt-1", "event_type": "inventory.movement_created"})

        asyncio.run(consumer._handle_message(first))
        asyncio.run(consumer._handle_message(second))

        assert calls == ["evt-1"]
        assert first.ack_count == 1
        assert second.ack_count == 1

    def test_decode_error_moves_message_to_dead_letter_queue(self):
        consumer = NATSEventConsumer(enabled=False)
        message = _FakeMessage("{not-json")

        asyncio.run(consumer._handle_message(message))

        dead_letters = consumer.get_dead_letters()
        assert len(dead_letters) == 1
        assert dead_letters[0]["reason"] == "decode_error"
        assert message.term_count == 1
        assert message.nak_count == 0

    def test_handler_failure_naks_before_dead_letter_threshold(self):
        consumer = NATSEventConsumer(enabled=False, max_redeliveries=3)

        async def handler(_event):
            raise RuntimeError("boom")

        consumer.register_handler("inventory.movement_created", handler)
        message = _FakeMessage(
            {"event_id": "evt-2", "event_type": "inventory.movement_created"},
            num_delivered=2,
        )

        asyncio.run(consumer._handle_message(message))

        assert message.nak_count == 1
        assert message.term_count == 0
        assert consumer.get_dead_letters() == []

    def test_handler_failure_terms_and_records_dead_letter_after_threshold(self):
        consumer = NATSEventConsumer(enabled=False, max_redeliveries=3)

        async def handler(_event):
            raise RuntimeError("boom")

        consumer.register_handler("inventory.movement_created", handler)
        message = _FakeMessage(
            {"event_id": "evt-3", "event_type": "inventory.movement_created"},
            num_delivered=3,
        )

        asyncio.run(consumer._handle_message(message))

        dead_letters = consumer.get_dead_letters()
        assert len(dead_letters) == 1
        assert dead_letters[0]["event_id"] == "evt-3"
        assert dead_letters[0]["reason"] == "handler_error:RuntimeError"
        assert message.term_count == 1
        assert message.nak_count == 0
