"""
NATS Event Publisher
Production event bus using NATS JetStream.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from app.domains.shared.events import DomainEvent, IEventPublisher

logger = logging.getLogger(__name__)


class NATSEventPublisher(IEventPublisher):
    """
    NATS JetStream-based event publisher.

    Falls back to logging if NATS is unavailable or disabled.
    """

    def __init__(self, nats_url: str = "nats://localhost:4222", enabled: bool = False):
        self.nats_url = nats_url
        self.enabled = enabled
        self._nc: Optional[object] = None
        self._js: Optional[object] = None
        self._connected: bool = False

        if enabled:
            logger.info("NATS Publisher initialized (URL: %s)", nats_url)
        else:
            logger.info("NATS Publisher disabled — using log-only fallback")

    async def publish(self, event: DomainEvent) -> None:
        """Publish event to NATS JetStream or fallback to logging."""

        event_data = {
            "event_type": event.__class__.__name__,
            "event_id": event.event_id,
            "aggregate_id": event.aggregate_id,
            "timestamp": event.timestamp.isoformat(),
            "payload": self._serialize_event(event),
        }

        if not self._connected or self._js is None:
            logger.info(
                "Event (fallback): %s id=%s",
                event.__class__.__name__,
                event.event_id,
            )
            return

        subject = f"domain.{event.__class__.__module__.split('.')[-2]}.{event.__class__.__name__}"

        try:
            ack = await self._js.publish(subject, json.dumps(event_data).encode())
            logger.info(
                "Event published to NATS: %s (stream=%s, seq=%s)",
                subject,
                ack.stream,
                ack.seq,
            )
        except Exception as e:
            logger.error("Failed to publish event to NATS: %s", e, exc_info=True)
            logger.warning("Event fallback-logged: %s", event.__class__.__name__)

    def _serialize_event(self, event: DomainEvent) -> dict:
        from dataclasses import asdict

        data = asdict(event)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    async def connect(self) -> None:
        """Connect to NATS server and obtain JetStream context."""
        if not self.enabled:
            self._connected = False
            return

        try:
            import nats  # nats-py package

            self._nc = await nats.connect(self.nats_url)
            self._js = self._nc.jetstream()
            self._connected = True
            logger.info("NATS JetStream connection established")
        except Exception as e:
            logger.error("Failed to connect to NATS: %s", e)
            self._connected = False
            self.enabled = False

    async def disconnect(self) -> None:
        """Disconnect from NATS server."""
        if self._nc:
            try:
                await self._nc.close()
            except Exception:
                pass
            logger.info("NATS connection closed")
        self._connected = False


def _create_publisher() -> NATSEventPublisher:
    """Create publisher from application config."""
    try:
        from app.core.config import settings
        enabled = settings.EVENT_BUS_ENABLED and settings.EVENT_BUS_PROVIDER == "nats"
        return NATSEventPublisher(
            nats_url=settings.EVENT_BUS_NATS_URL,
            enabled=enabled,
        )
    except Exception:
        return NATSEventPublisher(enabled=False)


nats_publisher = _create_publisher()
