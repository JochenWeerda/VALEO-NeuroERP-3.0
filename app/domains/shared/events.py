"""
Domain Events Infrastructure
Provides event abstractions and runtime-configurable publisher selection.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type
from uuid import uuid4

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class DomainEvent(ABC):
    """Base class for all domain events."""

    aggregate_id: str
    timestamp: datetime
    event_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(kw_only=True)
class IntegrationEvent(DomainEvent):
    """Generic integration event for outbox/event-bus transport."""

    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)


class IEventPublisher(ABC):
    """Interface for event publishing."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""


class InMemoryEventPublisher(IEventPublisher):
    """In-memory publisher, useful for local fallback and tests."""

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
        self._event_log: List[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        logger.info(
            "Event published in-memory: %s",
            event.__class__.__name__,
            extra={
                "event_id": event.event_id,
                "aggregate_id": event.aggregate_id,
                "timestamp": event.timestamp.isoformat(),
            },
        )
        self._event_log.append(event)

        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as exc:
                logger.error("Event handler failed: %s", exc, exc_info=True)

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        self._handlers.setdefault(event_type, []).append(handler)
        logger.debug("Registered handler for %s", event_type.__name__)

    def get_events(self, limit: int = 100) -> List[DomainEvent]:
        return self._event_log[-limit:]


_event_publisher: Optional[IEventPublisher] = None


def _build_publisher() -> IEventPublisher:
    provider = getattr(settings, "EVENT_BUS_PROVIDER", "memory")
    enabled = bool(getattr(settings, "EVENT_BUS_ENABLED", False))

    if enabled and provider == "nats":
        from app.infrastructure.eventbus.nats_publisher import nats_publisher

        nats_publisher.enabled = True
        nats_publisher.nats_url = getattr(settings, "EVENT_BUS_NATS_URL", nats_publisher.nats_url)
        logger.info("Using NATS event publisher")
        return nats_publisher

    logger.info("Using in-memory event publisher")
    return InMemoryEventPublisher()


def get_event_publisher() -> IEventPublisher:
    """Get (or initialize) the global event publisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = _build_publisher()
    return _event_publisher


async def startup_event_publisher() -> None:
    """Initialize publisher and connect if supported."""
    publisher = get_event_publisher()
    connect = getattr(publisher, "connect", None)
    if callable(connect):
        await connect()


async def shutdown_event_publisher() -> None:
    """Disconnect publisher if supported."""
    publisher = get_event_publisher()
    disconnect = getattr(publisher, "disconnect", None)
    if callable(disconnect):
        await disconnect()


async def startup_event_consumer() -> None:
    """Initialize NATS consumer and register core handlers if enabled."""
    from app.infrastructure.eventbus.nats_consumer import nats_consumer
    from app.services.nats_event_handlers import register_core_event_handlers

    enabled = bool(getattr(settings, "EVENT_BUS_ENABLED", False))
    provider = getattr(settings, "EVENT_BUS_PROVIDER", "memory")
    if not enabled or provider != "nats":
        logger.info("Event consumer disabled (provider=%s, enabled=%s)", provider, enabled)
        return

    nats_consumer.enabled = True
    nats_consumer.nats_url = getattr(settings, "EVENT_BUS_NATS_URL", nats_consumer.nats_url)
    register_core_event_handlers(nats_consumer)
    await nats_consumer.start()


async def shutdown_event_consumer() -> None:
    """Stop the NATS consumer if running."""
    from app.infrastructure.eventbus.nats_consumer import nats_consumer

    await nats_consumer.stop()
