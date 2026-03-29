"""
Event Schema Registry — NC-G1
Pydantic-basierte Event-Schemas mit Version-Header fuer Domain-Events.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EventHeader(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    version: str = "1.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tenant_id: str = "system"
    correlation_id: Optional[str] = None
    source: str = "valeo-neuro-erp"


class DomainEvent(BaseModel):
    header: EventHeader
    payload: dict[str, Any] = Field(default_factory=dict)


class AuditEvent(DomainEvent):
    pass


class InventoryMovementEvent(DomainEvent):
    pass


class SettlementCreatedEvent(DomainEvent):
    pass


class OrderStateChangedEvent(DomainEvent):
    pass


class ComplianceViolationEvent(DomainEvent):
    pass


class ConsentChangedEvent(DomainEvent):
    pass


EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "audit.entry_created": AuditEvent,
    "inventory.movement_created": InventoryMovementEvent,
    "settlement.created": SettlementCreatedEvent,
    "order.state_changed": OrderStateChangedEvent,
    "compliance.violation_detected": ComplianceViolationEvent,
    "consent.changed": ConsentChangedEvent,
}


def create_event(event_type: str, payload: dict, tenant_id: str = "system", correlation_id: Optional[str] = None) -> DomainEvent:
    event_class = EVENT_REGISTRY.get(event_type, DomainEvent)
    header = EventHeader(
        event_type=event_type,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )
    return event_class(header=header, payload=payload)


def list_event_types() -> list[dict]:
    return [
        {"event_type": k, "schema_class": v.__name__, "version": "1.0"}
        for k, v in EVENT_REGISTRY.items()
    ]


def validate_event(event_type: str, payload: dict) -> dict:
    if event_type not in EVENT_REGISTRY:
        return {"valid": False, "error": f"Unbekannter Event-Typ: {event_type}"}
    try:
        event = create_event(event_type, payload)
        return {"valid": True, "event_id": event.header.event_id}
    except Exception as exc:
        return {"valid": False, "error": str(exc)}
