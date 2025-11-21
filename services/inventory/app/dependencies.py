"""Zentrale FastAPI-Dependencies für den Inventory-Service."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import Header

from app.config import settings
from app.db.session import get_session_factory
from app.integration.event_bus import EventBus
from app.integration.subscribers import InventoryEventSubscribers


logger = logging.getLogger(__name__)

_event_bus: Optional[EventBus] = None
_subscribers: Optional[InventoryEventSubscribers] = None


async def init_event_bus() -> None:
    """EventBus-Verbindung bei Service-Start initialisieren."""
    global _event_bus, _subscribers
    if not settings.EVENT_BUS_ENABLED or _event_bus is not None:
        return

    bus = EventBus(settings.EVENT_BUS_URL, settings.EVENT_BUS_SUBJECT_PREFIX)
    try:
        await bus.connect()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Inventory EventBus konnte nicht verbunden werden: %s", exc)
        return

    _event_bus = bus
    subscribers = InventoryEventSubscribers(bus, get_session_factory())
    await subscribers.start()
    _subscribers = subscribers


def get_event_bus() -> Optional[EventBus]:
    """EventBus für Request-Kontext liefern (kann `None` sein)."""
    return _event_bus


async def shutdown_event_bus() -> None:
    """EventBus-Verbindung sauber abbauen."""
    global _event_bus, _subscribers
    if _subscribers:
        await _subscribers.stop()
        _subscribers = None
    if _event_bus:
        await _event_bus.close()
        _event_bus = None


def resolve_tenant_id(x_tenant_id: Optional[str] = Header(default=None)) -> str:
    """Mandanten-ID aus Header ableiten (Fallback auf Default)."""
    if x_tenant_id and x_tenant_id.strip():
        return x_tenant_id.strip()
    return settings.DEFAULT_TENANT

