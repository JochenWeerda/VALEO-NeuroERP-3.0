"""
NATS Event Consumer -- NC-G2

Generic NATS JetStream consumer with handler registry, retry-aware acking,
and in-memory fallback for disabled environments.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict[str, Any]], Awaitable[None] | None]


class NATSEventConsumer:
    """
    NATS JetStream-based consumer with handler registry.

    When disabled, the consumer will not connect and will simply log dispatches.
    """

    def __init__(
        self,
        nats_url: str = "nats://localhost:4222",
        enabled: bool = False,
        subject: str = "domain.>",
        durable_name: str = "valeo-neuro-consumer",
        ack_wait_seconds: int = 30,
        max_ack_pending: int = 200,
    ) -> None:
        self.nats_url = nats_url
        self.enabled = enabled
        self.subject = subject
        self.durable_name = durable_name
        self.ack_wait_seconds = ack_wait_seconds
        self.max_ack_pending = max_ack_pending

        self._nc: Optional[object] = None
        self._js: Optional[object] = None
        self._sub: Optional[object] = None
        self._connected = False
        self._handlers: dict[str, list[EventHandler]] = {}
        self._default_handlers: list[EventHandler] = []

        if enabled:
            logger.info("NATS Consumer initialized (URL: %s)", nats_url)
        else:
            logger.info("NATS Consumer disabled -- using log-only fallback")

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)
        logger.debug("Registered NATS handler for %s", event_type)

    def register_default_handler(self, handler: EventHandler) -> None:
        self._default_handlers.append(handler)
        logger.debug("Registered NATS default handler")

    async def connect(self) -> None:
        if not self.enabled:
            self._connected = False
            return

        try:
            import nats  # nats-py package

            self._nc = await nats.connect(self.nats_url)
            self._js = self._nc.jetstream()
            self._connected = True
            logger.info("NATS consumer connection established")
        except Exception as exc:
            logger.error("Failed to connect NATS consumer: %s", exc, exc_info=True)
            self._connected = False
            self.enabled = False

    async def disconnect(self) -> None:
        if self._sub is not None:
            try:
                await self._sub.unsubscribe()
            except Exception:
                pass
            self._sub = None
        if self._nc:
            try:
                await self._nc.close()
            except Exception:
                pass
        self._connected = False

    async def start(self) -> None:
        """Start consuming from NATS JetStream."""
        if not self.enabled:
            logger.info("NATS consumer not started (disabled)")
            return

        if not self._connected:
            await self.connect()

        if not self._connected or self._js is None:
            logger.warning("NATS consumer not connected; start skipped")
            return

        self._sub = await self._js.subscribe(
            self.subject,
            durable=self.durable_name,
            ack_wait=self.ack_wait_seconds,
            max_ack_pending=self.max_ack_pending,
            cb=self._handle_message,
        )
        logger.info(
            "NATS consumer subscribed: subject=%s durable=%s",
            self.subject,
            self.durable_name,
        )

    async def stop(self) -> None:
        await self.disconnect()

    async def dispatch_event(self, event: dict[str, Any]) -> None:
        """Dispatch a decoded event to registered handlers."""
        event_type = (
            event.get("event_type")
            or event.get("type")
            or event.get("header", {}).get("event_type")
        )
        handlers = self._handlers.get(event_type or "", [])

        if not handlers and not self._default_handlers:
            logger.info("NATS event dropped (no handler): %s", event_type)
            return

        tasks = []
        for handler in handlers or self._default_handlers:
            result = handler(event)
            if asyncio.iscoroutine(result):
                tasks.append(result)
        if tasks:
            await asyncio.gather(*tasks)

    async def _handle_message(self, msg: Any) -> None:
        try:
            raw = msg.data.decode() if hasattr(msg, "data") else ""
            event = json.loads(raw) if raw else {}
        except Exception as exc:
            logger.error("Failed to decode NATS message: %s", exc, exc_info=True)
            await self._ack_message(msg, success=False)
            return

        try:
            await self.dispatch_event(event)
            await self._ack_message(msg, success=True)
        except Exception as exc:
            logger.error("NATS handler error: %s", exc, exc_info=True)
            await self._ack_message(msg, success=False)

    async def _ack_message(self, msg: Any, success: bool) -> None:
        if not msg:
            return
        if success and hasattr(msg, "ack"):
            await msg.ack()
            return
        if not success:
            if hasattr(msg, "nak"):
                await msg.nak()
                return
            if hasattr(msg, "term"):
                await msg.term()


nats_consumer = NATSEventConsumer()
