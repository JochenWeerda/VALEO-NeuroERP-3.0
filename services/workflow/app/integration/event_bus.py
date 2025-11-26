"""
NATS-basierte Event-Bus-Integration.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Awaitable, Callable, Optional

from nats.aio.client import Client as NATS


logger = logging.getLogger(__name__)


EventHandler = Callable[[dict], Awaitable[None]]


class EventBus:
    """Stellt Publikations- und Subscribe-Funktionalität gegen NATS bereit."""

    def __init__(self, url: str, subject_prefix: str) -> None:
        self._url = url
        self._subject_prefix = subject_prefix.rstrip(".")
        self._client: Optional[NATS] = None
        self._subscription = None

    async def connect(self, handler: EventHandler | None = None) -> None:
        self._client = NATS()
        await self._client.connect(self._url)
        logger.info("Mit Event-Bus %s verbunden", self._url)

        if handler:
            subject = f"{self._subject_prefix}.>"

            async def _callback(msg):
                try:
                    payload = json.loads(msg.data.decode("utf-8"))
                except json.JSONDecodeError:
                    logger.warning("Konnte Event-Bus-Payload nicht parsen: %s", msg.data)
                    return
                await handler(payload)

            self._subscription = await self._client.subscribe(subject, cb=_callback)
            logger.info("Event-Bus Subscription aktiv: %s", subject)

    async def publish(self, event_type: str, tenant: str, data: dict) -> None:
        if not self._client:
            logger.warning("EventBus publish aufgerufen ohne Verbindung.")
            return
        subject = f"{self._subject_prefix}.{event_type}"
        payload = json.dumps({"event_type": event_type, "tenant": tenant, "data": data}).encode("utf-8")
        await self._client.publish(subject, payload)
        logger.debug("EventBus publish -> %s", subject)

    async def close(self) -> None:
        if self._subscription is not None and self._client:
            await self._client.drain()
        if self._client:
            await self._client.close()
            logger.info("Event-Bus Verbindung geschlossen")


