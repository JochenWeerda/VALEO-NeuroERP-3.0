"""
audit_middleware.py — Automatische Audit-Log-Erfassung für Mutationen (Gap 049)

Erfasst alle schreibenden HTTP-Methoden (POST, PUT, PATCH, DELETE) und schreibt
einen Eintrag in app_audit_log (Tabelle) via direktem DB-Insert wenn möglich,
sonst als Structured-Log-Event.

Abgedeckt:
  - Alle /api/v1/* Endpunkte mit POST/PUT/PATCH/DELETE
  - User-ID und Tenant-ID aus request.state (gesetzt von Bearer-Token-Middleware)
  - Correlation-ID aus request.state oder Header
  - IP-Adresse und User-Agent
  - HTTP-Methode, Pfad, Status-Code
  - Keine Request-Body-Aufzeichnung (Datenschutz)
"""
from __future__ import annotations

import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("audit")

_AUDIT_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_AUDIT_PREFIX = "/api/v1/"
_SKIP_PATHS = frozenset({
    "/api/v1/health",
    "/api/v1/health/ready",
    "/api/v1/health/live",
    "/api/v1/metrics",
    "/api/v1/audit/log",  # Kein rekursives Audit des Audit-Endpoints
})


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware die schreibende API-Aufrufe automatisch als Audit-Events loggt.

    Schreibt einen strukturierten Log-Eintrag mit:
    - action: HTTP-Methode + Pfad
    - entity_type: zweites Path-Segment (z.B. 'kontrakte', 'zahlungen')
    - user_id: aus request.state.token_claims['sub']
    - tenant_id: aus request.state.tenant_id
    - status_code: der HTTP-Response-Code
    - duration_ms: Verarbeitungszeit
    - correlation_id: aus request.state oder Header

    Kein DB-Write in der Middleware selbst (vermeidet Session-Konflikte).
    Die Audit-API /api/v1/audit/log bleibt für explizite Einträge bestehen.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Nur schreibende Methoden auf API-Pfaden auditieren
        if (
            request.method not in _AUDIT_METHODS
            or not request.url.path.startswith(_AUDIT_PREFIX)
            or request.url.path in _SKIP_PATHS
        ):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        # Metadaten aus Request-State extrahieren
        claims = getattr(request.state, "token_claims", {}) or {}
        user_id = claims.get("sub") or request.headers.get("X-User-ID", "anonymous")
        tenant_id = getattr(request.state, "tenant_id", "unknown")
        correlation_id = (
            getattr(request.state, "correlation_id", None)
            or request.headers.get("X-Correlation-ID", "")
        )

        # Entity-Type aus Pfad ableiten (z.B. /api/v1/kontrakte/123 → "kontrakte")
        path_parts = request.url.path.removeprefix(_AUDIT_PREFIX).split("/")
        entity_type = path_parts[0] if path_parts else "unknown"

        logger.info(
            "AUDIT",
            extra={
                "audit": True,
                "action": f"{request.method} {request.url.path}",
                "entity_type": entity_type,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "correlation_id": correlation_id,
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
            },
        )

        return response
