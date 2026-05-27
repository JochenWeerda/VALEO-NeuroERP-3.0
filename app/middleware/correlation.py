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
    """Middleware that propagates correlation ID and tenant context to log ContextVars.

    ContextVars are set with token-based reset so values cannot leak between
    concurrent requests processed on the same thread/task.
    """

    async def dispatch(self, request: Request, call_next):
        from app.core.logging import correlation_id_var, tenant_id_var

        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or uuid7()

        # Token-based set/reset guarantees cleanup even on exceptions.
        tok_cid = correlation_id_var.set(correlation_id)
        tok_tid = tenant_id_var.set(request.headers.get("X-Tenant-ID", ""))
        try:
            response = await call_next(request)
        finally:
            correlation_id_var.reset(tok_cid)
            tenant_id_var.reset(tok_tid)

        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response

