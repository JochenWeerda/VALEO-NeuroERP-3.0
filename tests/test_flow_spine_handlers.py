"""Tests fuer Flow-Spine Event Handlers und Observability (NC-14)."""

import asyncio
import pytest

from app.infrastructure.eventbus.flow_spine_handlers import (
    FLOW_SPINE_HANDLER_REGISTRY,
    handle_order_state_changed,
    handle_invoice_created,
    handle_settlement_completed,
    handle_inventory_movement,
    handle_contract_position_changed,
    handle_neuro_decision,
    handle_channel_message,
    register_flow_spine_handlers,
)
from app.infrastructure.eventbus.observability import EventBusObserver


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestFlowSpineHandlerRegistry:
    def test_registry_has_all_handlers(self):
        assert len(FLOW_SPINE_HANDLER_REGISTRY) >= 7
        assert "order.state_changed" in FLOW_SPINE_HANDLER_REGISTRY
        assert "invoice.created" in FLOW_SPINE_HANDLER_REGISTRY
        assert "settlement.completed" in FLOW_SPINE_HANDLER_REGISTRY
        assert "inventory.movement" in FLOW_SPINE_HANDLER_REGISTRY
        assert "contract.position_changed" in FLOW_SPINE_HANDLER_REGISTRY
        assert "neuro.decision" in FLOW_SPINE_HANDLER_REGISTRY
        assert "channel.message_received" in FLOW_SPINE_HANDLER_REGISTRY

    def test_all_handlers_are_async(self):
        for event_type, handler in FLOW_SPINE_HANDLER_REGISTRY.items():
            assert asyncio.iscoroutinefunction(handler), f"{event_type} handler is not async"


class TestOrderStateHandler:
    def test_order_approved(self):
        event = {"payload": {"order_id": "ORD-001", "new_state": "approved", "old_state": "created"}}
        _run(handle_order_state_changed(event))

    def test_order_cancelled(self):
        event = {"payload": {"order_id": "ORD-002", "new_state": "cancelled", "old_state": "approved"}}
        _run(handle_order_state_changed(event))

    def test_order_minimal(self):
        _run(handle_order_state_changed({}))


class TestInvoiceHandler:
    def test_invoice_created(self):
        event = {"payload": {"invoice_id": "INV-001", "total_amount": 15000.0}}
        _run(handle_invoice_created(event))


class TestSettlementHandler:
    def test_settlement_completed(self):
        event = {"payload": {"settlement_id": "SET-001", "settlement_type": "ernte"}}
        _run(handle_settlement_completed(event))


class TestInventoryHandler:
    def test_positive_movement(self):
        event = {"payload": {"article_id": "ART-001", "warehouse_id": "WH-01", "quantity": 100, "movement_type": "eingang"}}
        _run(handle_inventory_movement(event))

    def test_negative_movement_warns(self):
        event = {"payload": {"article_id": "ART-002", "warehouse_id": "WH-01", "quantity": -50, "movement_type": "ausgang"}}
        _run(handle_inventory_movement(event))


class TestContractPositionHandler:
    def test_short_position_warns(self):
        event = {"payload": {"contract_id": "CON-001", "article_group": "Sojaschrot", "net_position_mt": -150}}
        _run(handle_contract_position_changed(event))

    def test_long_position(self):
        event = {"payload": {"contract_id": "CON-002", "article_group": "Mais", "net_position_mt": 300}}
        _run(handle_contract_position_changed(event))


class TestNeuroDecisionHandler:
    def test_neuro_decision(self):
        event = {"payload": {"decision_id": "DEC-001", "intent": "bestellung_anlegen", "confidence_score": 0.92}}
        _run(handle_neuro_decision(event))


class TestChannelMessageHandler:
    def test_channel_message(self):
        event = {"payload": {"channel_type": "whatsapp", "sender_id": "+4917012345"}}
        _run(handle_channel_message(event))


class TestRegisterHandlers:
    def test_register_all(self):
        class MockConsumer:
            def __init__(self):
                self.registered = {}
            def register_handler(self, event_type, handler):
                self.registered[event_type] = handler

        consumer = MockConsumer()
        register_flow_spine_handlers(consumer)
        assert len(consumer.registered) == len(FLOW_SPINE_HANDLER_REGISTRY)


class TestEventBusObserver:
    def test_initial_health_idle(self):
        observer = EventBusObserver()
        health = observer.get_health()
        assert health["status"] == "idle"

    def test_record_and_metrics(self):
        observer = EventBusObserver()
        observer.record_event_received("order.state_changed")
        observer.record_event_processed("order.state_changed", "handle_order", 12.5)
        observer.record_event_received("invoice.created")
        observer.record_event_processed("invoice.created", "handle_invoice", 8.3)

        metrics = observer.get_metrics()
        assert metrics["events_received"] == 2
        assert metrics["events_processed"] == 2
        assert metrics["events_failed"] == 0
        assert metrics["by_type"]["order.state_changed"] == 1
        assert metrics["by_handler"]["handle_order"] == 1

    def test_health_degraded_on_many_failures(self):
        observer = EventBusObserver()
        for _ in range(10):
            observer.record_event_received("test")
        for _ in range(5):
            observer.record_event_failed("test", "error")
        health = observer.get_health()
        assert health["status"] == "degraded"

    def test_health_warning_on_dlq(self):
        observer = EventBusObserver()
        observer.record_event_received("test")
        observer.record_event_processed("test", "h", 1.0)
        observer.record_dlq_entry("test")
        health = observer.get_health()
        assert health["status"] == "warning"

    def test_reset(self):
        observer = EventBusObserver()
        observer.record_event_received("x")
        observer.reset()
        assert observer.get_metrics()["events_received"] == 0

    def test_recent_errors_limited(self):
        observer = EventBusObserver(max_error_history=5)
        for i in range(10):
            observer.record_event_failed("test", f"error-{i}")
        errors = observer.get_recent_errors()
        assert len(errors) == 5
