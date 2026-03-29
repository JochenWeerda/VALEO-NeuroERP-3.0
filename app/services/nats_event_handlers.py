"""
NC-G3 -- Core NATS event handlers.

Registers baseline handlers for audit, inventory movement and settlement events.
Handlers validate schema and emit structured logs for downstream processing.
"""

from __future__ import annotations

import logging
from typing import Any

from app.infrastructure.eventbus.nats_consumer import NATSEventConsumer
from app.services.event_schema_registry import validate_event

logger = logging.getLogger(__name__)


async def handle_audit_event(event: dict[str, Any]) -> None:
    payload = event.get("payload", {})
    result = validate_event("audit.entry_created", payload)
    if not result.get("valid"):
        logger.warning("Audit event validation failed: %s", result.get("error"))
        return
    logger.info("Audit event handled: %s", event.get("event_id"))


async def handle_inventory_movement_event(event: dict[str, Any]) -> None:
    payload = event.get("payload", {})
    result = validate_event("inventory.movement_created", payload)
    if not result.get("valid"):
        logger.warning("Inventory movement validation failed: %s", result.get("error"))
        return
    logger.info("Inventory movement handled: %s", event.get("event_id"))


async def handle_settlement_created_event(event: dict[str, Any]) -> None:
    payload = event.get("payload", {})
    result = validate_event("settlement.created", payload)
    if not result.get("valid"):
        logger.warning("Settlement validation failed: %s", result.get("error"))
        return
    logger.info("Settlement event handled: %s", event.get("event_id"))


def register_core_event_handlers(consumer: NATSEventConsumer) -> None:
    consumer.register_handler("audit.entry_created", handle_audit_event)
    consumer.register_handler("inventory.movement_created", handle_inventory_movement_event)
    consumer.register_handler("settlement.created", handle_settlement_created_event)
