"""Correlation-ID Middleware."""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Callable, Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from structlog import contextvars as structlog_ctx

CORRELATION_HEADER = "X-Correlation-ID"
_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    """Expose the current correlation id."""
    return _correlation_id_ctx.get()


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Ensures every request carries a correlation id."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        incoming_id = request.headers.get(CORRELATION_HEADER)
        correlation_id = incoming_id or str(uuid.uuid4())

        request.state.correlation_id = correlation_id
        token = _correlation_id_ctx.set(correlation_id)
        structlog_ctx.bind_contextvars(correlation_id=correlation_id)

        try:
            response = await call_next(request)
        finally:
            structlog_ctx.unbind_contextvars("correlation_id")
            _correlation_id_ctx.reset(token)

        response.headers[CORRELATION_HEADER] = correlation_id
        return response

