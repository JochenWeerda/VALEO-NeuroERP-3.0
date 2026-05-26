"""
Correlation ID Middleware
Generates and tracks correlation IDs for request tracing
"""

import logging
from app.core.uuid7 import uuid7
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import set_correlation_id, set_log_context

logger = logging.getLogger(__name__)

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware that propagates correlation ID and tenant context to log ContextVars."""

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or uuid7()
        set_correlation_id(correlation_id)

        # Propagate tenant_id so all log lines carry it without explicit extra=
        set_log_context(tenant_id=request.headers.get("X-Tenant-ID", ""))

        response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response

