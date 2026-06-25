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
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

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


class AuditMiddleware:
    """
    Pure ASGI-Middleware die schreibende API-Aufrufe als Audit-Events loggt
    (PERF-MULTIUSER-001 — ersetzt die frühere BaseHTTPMiddleware).

    Schreibt einen strukturierten Log-Eintrag mit:
    - action: HTTP-Methode + Pfad
    - entity_type: zweites Path-Segment (z.B. 'kontrakte', 'zahlungen')
    - user_id: aus request.state.token_claims['sub']
    - tenant_id: aus request.state.tenant_id
    - status_code: der HTTP-Response-Code (aus http.response.start)
    - duration_ms: Verarbeitungszeit
    - correlation_id: aus request.state oder Header

    Kein DB-Write in der Middleware selbst (vermeidet Session-Konflikte).
    Die Audit-API /api/v1/audit/log bleibt für explizite Einträge bestehen.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        # Nur schreibende Methoden auf API-Pfaden auditieren
        if (
            method not in _AUDIT_METHODS
            or not path.startswith(_AUDIT_PREFIX)
            or path in _SKIP_PATHS
        ):
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        # Bei Exception propagiert der Fehler vor dem Logging (wie zuvor).
        await self.app(scope, receive, send_wrapper)

        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        # Metadaten aus Request-State/Scope extrahieren (state von Bearer-Schicht gesetzt)
        request = Request(scope)
        headers = request.headers
        claims = getattr(request.state, "token_claims", {}) or {}
        user_id = claims.get("sub") or headers.get("X-User-ID", "anonymous")
        tenant_id = getattr(request.state, "tenant_id", "unknown")
        correlation_id = (
            getattr(request.state, "correlation_id", None)
            or headers.get("X-Correlation-ID", "")
        )

        # Entity-Type aus Pfad ableiten (z.B. /api/v1/kontrakte/123 → "kontrakte")
        path_parts = path.removeprefix(_AUDIT_PREFIX).split("/")
        entity_type = path_parts[0] if path_parts else "unknown"

        client = scope.get("client")
        logger.info(
            "AUDIT",
            extra={
                "audit": True,
                "action": f"{method} {path}",
                "entity_type": entity_type,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "correlation_id": correlation_id,
                "ip_address": client[0] if client else "unknown",
                "user_agent": headers.get("user-agent", ""),
            },
        )
