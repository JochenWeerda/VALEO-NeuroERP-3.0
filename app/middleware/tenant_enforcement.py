"""
tenant_enforcement.py — Zentraler Tenant-Guard

Stellt sicher, dass alle /api/v1/* Requests (ausser Health/Metrics)
einen gueltigen X-Tenant-ID Header haben und setzt den Tenant-Kontext
fuer die gesamte Request-Verarbeitung.

Schuetzt gegen:
- Fehlende Tenant-ID auf API-Pfaden
- Leere oder nur aus Whitespace bestehende Tenant-IDs
- Tenant-Context-Leaks zwischen Requests (ContextVar wird pro Request gesetzt/zurueckgesetzt)
"""
from __future__ import annotations

import logging
import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.tenant_context import set_current_tenant_id, reset_current_tenant_id

logger = logging.getLogger("tenant_enforcement")

# Paths that don't require tenant identification
_EXEMPT_PATHS = frozenset({
    "/api/v1/health",
    "/api/v1/health/ready",
    "/api/v1/health/live",
    "/api/v1/metrics",
    "/api/v1/openapi.json",
    "/docs",
    "/redoc",
})

_EXEMPT_PREFIXES = (
    "/api/v1/health/",
    "/api/v1/.well-known/",
)

# Tenant ID must be non-empty, alphanumeric with hyphens/underscores, max 100 chars
_TENANT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,100}$")

_API_PREFIX = "/api/v1/"


class TenantEnforcementMiddleware(BaseHTTPMiddleware):
    """
    Validates X-Tenant-ID on every API request and sets the request-scoped
    tenant context variable. Rejects requests without valid tenant ID
    (except health/metrics/docs).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip non-API paths and exempt paths
        if not path.startswith(_API_PREFIX):
            return await call_next(request)

        if path in _EXEMPT_PATHS or any(path.startswith(p) for p in _EXEMPT_PREFIXES):
            return await call_next(request)

        # Extract tenant ID from header
        raw_tenant = (request.headers.get("X-Tenant-ID") or "").strip()

        # In dev mode, allow default tenant fallback
        if not raw_tenant and settings.API_DEV_TOKEN:
            raw_tenant = settings.DEFAULT_TENANT_ID

        if not raw_tenant:
            logger.warning("tenant_missing path=%s method=%s ip=%s",
                           path, request.method, request.client.host if request.client else "unknown")
            return JSONResponse(
                status_code=400,
                content={"detail": "X-Tenant-ID header is required"},
            )

        if not _TENANT_ID_PATTERN.match(raw_tenant):
            logger.warning("tenant_invalid path=%s tenant=%s", path, raw_tenant[:50])
            return JSONResponse(
                status_code=400,
                content={"detail": "X-Tenant-ID contains invalid characters"},
            )

        # Set tenant context for this request
        token = set_current_tenant_id(raw_tenant)
        request.state.tenant_id = raw_tenant

        try:
            response = await call_next(request)
            return response
        finally:
            reset_current_tenant_id(token)
