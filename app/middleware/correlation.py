"""
Correlation ID Middleware (pure ASGI — PERF-MULTIUSER-001)

Generates and tracks correlation IDs for request tracing.

Reine ASGI-Middleware statt BaseHTTPMiddleware: vermeidet den anyio-
Stream-Overhead pro Request unter Multi-User-Last. Setzt Correlation-/
Tenant-Context als ContextVars (token-basiert zurueckgesetzt, kein Leak
zwischen nebenlaeufigen Requests) und spiegelt die Correlation-ID in den
Response-Header zurueck.
"""

import logging

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import correlation_id_var, tenant_id_var
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationMiddleware:
    """Pure ASGI middleware that propagates correlation ID and tenant context.

    ContextVars are set with token-based reset so values cannot leak between
    concurrent requests processed on the same thread/task.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        correlation_id = headers.get(CORRELATION_ID_HEADER) or uuid7()

        tok_cid = correlation_id_var.set(correlation_id)
        tok_tid = tenant_id_var.set(headers.get("X-Tenant-ID", ""))

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[CORRELATION_ID_HEADER] = correlation_id
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            correlation_id_var.reset(tok_cid)
            tenant_id_var.reset(tok_tid)
