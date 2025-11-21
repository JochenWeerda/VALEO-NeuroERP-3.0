"""Einfache NATS-Eventbus-Integration für den InfraStat-Service."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from nats.aio.client import Client as NATS


logger = logging.getLogger(__name__)


class EventBus:
    """Publiziert Events an NATS-basierte Topics."""

    def __init__(self, url: str, subject_prefix: str) -> None:
        self._url = url
        self._subject_prefix = subject_prefix.rstrip(".")
        self._client: Optional[NATS] = None

    async def connect(self) -> None:
        if self._client:
            return
        self._client = NATS()
        await self._client.connect(self._url)
        logger.info("EventBus verbunden (%s)", self._url)

    async def publish(self, event_type: str, tenant: str, data: dict[str, Any]) -> None:
        if not self._client:
            logger.debug("EventBus Publish verworfen: keine Verbindung (%s)", event_type)
            return
        subject = f"{self._subject_prefix}.{event_type}"
        payload = json.dumps({"event_type": event_type, "tenant": tenant, "data": data}).encode("utf-8")
        await self._client.publish(subject, payload)
        logger.debug("Event publiziert: %s", subject)

    async def close(self) -> None:
        if self._client:
            await self._client.drain()
            await self._client.close()
            logger.info("EventBus Verbindung geschlossen")
            self._client = None

