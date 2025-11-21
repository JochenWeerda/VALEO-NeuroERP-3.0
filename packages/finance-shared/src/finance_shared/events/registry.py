"""Einfache Registry für FiBu-Events."""

from __future__ import annotations

from typing import Dict, Type, cast

from .enums import FiBuEventType
from .models import (
    AccountUpdatedEvent,
    BookingApprovedEvent,
    BookingCreatedEvent,
    FiBuEventEnvelope,
    FiBuEventPayload,
    OpenItemCreatedEvent,
)

EVENT_REGISTRY: Dict[FiBuEventType, Type[FiBuEventEnvelope]] = {
    FiBuEventType.BOOKING_CREATED: BookingCreatedEvent,
    FiBuEventType.BOOKING_APPROVED: BookingApprovedEvent,
    FiBuEventType.MASTER_DATA_ACCOUNT_UPDATED: AccountUpdatedEvent,
    FiBuEventType.OPEN_ITEM_CREATED: OpenItemCreatedEvent,
}


def get_event_model(event_type: FiBuEventType) -> Type[FiBuEventEnvelope]:
    try:
        return EVENT_REGISTRY[event_type]
    except KeyError as exc:
        raise KeyError(f"Kein Event-Modell für {event_type.value} registriert") from exc


def serialize_event(event: FiBuEventEnvelope) -> dict:
    return cast(dict, event.serialize())


