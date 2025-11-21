"""Event-Publisher mit NATS-Anbindung."""

from __future__ import annotations

import asyncio
import json
import logging
from decimal import Decimal
from typing import Any, Callable

from finance_shared.events import BookingCreatedEvent, serialize_event
from nats.aio.client import Client as NATS

logger = logging.getLogger(__name__)


class FiBuEventPublisher:
    """Publiziert FiBu-Events (Standard: NATS, optional deaktivierbar)."""

    def __init__(
        self,
        *,
        enabled: bool,
        url: str,
        subject_booking_created: str,
        client_factory: Callable[[], NATS] = NATS,
    ) -> None:
        self._enabled = enabled
        self._url = url
        self._subject_booking_created = subject_booking_created
        self._client_factory = client_factory
        self._client: NATS | None = None
        self._lock = asyncio.Lock()

    async def publish_booking_created(
        self,
        *,
        tenant_id: str,
        booking_id: Any,
        account_id: str,
        amount: Decimal,
        currency: str,
        period: str,
        document_id: Any | None = None,
        approved: bool = False,
        correlation_id: str | None = None,
    ) -> None:
        if not self._enabled:
            logger.debug("Event-Publisher deaktiviert, überspringe Publish.")
            return

        event = BookingCreatedEvent.from_values(
            tenant_id=tenant_id,
            booking_id=booking_id,
            account_id=account_id,
            amount=amount,
            currency=currency,
            period=period,
            document_id=document_id,
            approved=approved,
            correlation_id=correlation_id,
        )
        payload = serialize_event(event)
        await self._publish(self._subject_booking_created, payload)

    @property
    def is_connected(self) -> bool:
        return bool(self._client and getattr(self._client, "is_connected", False))

    async def connect(self) -> None:
        if not self._enabled:
            return
        await self._ensure_connection()

    async def close(self) -> None:
        if self._client and getattr(self._client, "is_connected", False):
            await self._client.drain()
            await self._client.close()
        self._client = None

    async def _publish(self, subject: str, payload: dict[str, Any]) -> None:
        try:
            client = await self._ensure_connection()
            await client.publish(subject, json.dumps(payload).encode("utf-8"))
            logger.debug("Event auf NATS publiziert", extra={"subject": subject})
        except Exception:  # noqa: BLE001
            logger.exception("Event-Publish fehlgeschlagen – fällt auf Logging zurück.")
            logger.info("FiBu-Event (Fallback-Logging)", extra={"event": payload, "subject": subject})

    async def _ensure_connection(self) -> NATS:
        if self._client and getattr(self._client, "is_connected", False):
            return self._client
        async with self._lock:
            if self._client and getattr(self._client, "is_connected", False):
                return self._client
            client = self._client_factory()
            await client.connect(servers=[self._url], name="fibu-gateway")
            self._client = client
            return client



