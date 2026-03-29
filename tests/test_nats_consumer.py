"""
Tests for NC-G2: NATS Consumer Framework.
Focus on handler registry and dispatch logic (no NATS runtime).
"""

import asyncio

from app.infrastructure.eventbus.nats_consumer import NATSEventConsumer


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
