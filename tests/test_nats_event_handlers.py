"""
Tests for NC-G3 NATS core event handlers.
"""

from app.infrastructure.eventbus.nats_consumer import NATSEventConsumer
from app.services.nats_event_handlers import register_core_event_handlers


def test_register_core_event_handlers():
    consumer = NATSEventConsumer(enabled=False)
    register_core_event_handlers(consumer)

    assert "audit.entry_created" in consumer._handlers
    assert "inventory.movement_created" in consumer._handlers
    assert "settlement.created" in consumer._handlers
