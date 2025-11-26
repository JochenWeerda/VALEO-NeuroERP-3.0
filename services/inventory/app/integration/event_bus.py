"""Einfache NATS-basierte EventBus-Implementierung für den Inventory-Service."""

from __future__ import annotations

import json
import logging
from typing import Any, Awaitable, Callable, Optional

from nats.aio.client import Client as NATS


logger = logging.getLogger(__name__)


class EventBus:
    """Publiziert Domain-Events auf einem NATS-Subject."""

    def __init__(self, url: str, subject_prefix: str) -> None:
        self._url = url
        self._subject_prefix = subject_prefix.rstrip(".")
        self._client: Optional[NATS] = None
        self._subscriptions: list[int] = []

    async def connect(self) -> None:
        if self._client:
            return
        self._client = NATS()
        await self._client.connect(self._url)
        logger.info("Inventory EventBus verbunden (%s)", self._url)

    async def publish(self, event_type: str, tenant: str, data: dict[str, Any]) -> None:
        if not self._client:
            logger.debug("Inventory EventBus Publish verworfen: keine Verbindung (%s)", event_type)
            return
        subject = f"{self._subject_prefix}.{event_type}"
        payload = json.dumps({"event_type": event_type, "tenant": tenant, "data": data}).encode("utf-8")
        await self._client.publish(subject, payload)
        logger.debug("Inventory Event publiziert: %s", subject)

    async def subscribe(
        self,
        subject: str,
        handler: Callable[[dict[str, Any]], Awaitable[None]],
        queue: str | None = None,
    ) -> int:
        if not self._client:
            raise RuntimeError("EventBus ist nicht verbunden")

        async def _callback(msg):
            try:
                payload = json.loads(msg.data.decode("utf-8"))
            except json.JSONDecodeError as exc:  # noqa: BLE001
                logger.warning("Ungültige Event-Payload auf %s: %s", msg.subject, exc)
                return
            await handler(payload)

        sid = await self._client.subscribe(subject, queue=queue, cb=_callback)
        self._subscriptions.append(sid)
        logger.info("Inventory EventBus Subscription aktiviert: %s (sid=%s)", subject, sid)
        return sid

    async def unsubscribe(self, sid: int) -> None:
        if not self._client:
            return
        try:
            await self._client.unsubscribe(sid)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Konnte Subscription %s nicht aufheben: %s", sid, exc)
        if sid in self._subscriptions:
            self._subscriptions.remove(sid)

    async def close(self) -> None:
        if self._client:
            for sid in list(self._subscriptions):
                await self.unsubscribe(sid)
            await self._client.drain()
            await self._client.close()
            logger.info("Inventory EventBus Verbindung geschlossen")
            self._client = None

