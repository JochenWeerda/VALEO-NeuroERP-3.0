"""
Security Middleware
HTTP Security Headers, Correlation-ID, etc.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
import uuid
import time
import logging
import json

logger = logging.getLogger(__name__)


class SecurityHeaders(BaseHTTPMiddleware):
    """
    Security Headers Middleware
    
    Setzt folgende Security-Header:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    - Referrer-Policy
    - Permissions-Policy
    - Cross-Origin-Opener-Policy
    - Cross-Origin-Resource-Policy
    - Content-Security-Policy
    """

    def __init__(self, app: ASGIApp, csp: str) -> None:
        super().__init__(app)
        self.csp = csp

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        ***REMOVED*** HSTS - Force HTTPS
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )

        ***REMOVED*** Prevent MIME-Sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        ***REMOVED*** Prevent Clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        ***REMOVED*** Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        ***REMOVED*** Permissions Policy (Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), camera=(), microphone=()"
        )

        ***REMOVED*** Cross-Origin Policies
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"

        ***REMOVED*** Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp

        return response


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Correlation-ID Middleware
    
    Features:
    - Generiert/übernimmt Correlation-ID
    - Fügt X-Correlation-Id Header hinzu
    - Loggt Request/Response mit Correlation-ID
    - Structured Logging (JSON)
    """

    async def dispatch(self, request: Request, call_next):
        ***REMOVED*** Correlation-ID aus Header oder neu generieren
        cid = request.headers.get("x-correlation-id", str(uuid.uuid4()))

        ***REMOVED*** Start-Zeit für Latency-Messung
        start = time.time()

        ***REMOVED*** Request verarbeiten
        response = await call_next(request)

        ***REMOVED*** Latency berechnen
        latency_ms = int((time.time() - start) * 1000)

        ***REMOVED*** Correlation-ID in Response-Header
        response.headers["X-Correlation-Id"] = cid

        ***REMOVED*** Structured Logging
        log_data = {
            "correlation_id": cid,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "client_host": request.client.host if request.client else "unknown",
        }

        ***REMOVED*** Log-Level basierend auf Status-Code
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

        return response

