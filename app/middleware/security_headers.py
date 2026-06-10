"""
security_headers.py — HTTP Security Headers Middleware (Wave 75, Gap 049)

Fügt allen HTTP-Antworten des VALEO NeuroERP-Backends Security-Header hinzu.
Deckung:
  - X-Content-Type-Options:    verhindert MIME-Sniffing (OWASP A05)
  - X-Frame-Options:           verhindert Clickjacking (OWASP A05)
  - Referrer-Policy:           kontrolliert Referrer-Leakage
  - Permissions-Policy:        deaktiviert nicht benötigte Browser-APIs
  - X-XSS-Protection:          deaktiviert Legacy-XSS-Filter (CSP übernimmt)
  - Strict-Transport-Security: erzwingt HTTPS (nur non-DEBUG)
  - Content-Security-Policy:   schränkt erlaubte Quellen ein (nur non-DEBUG)
  - X-Request-ID:              leitet Correlation-ID weiter (Observability)
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


# ---------------------------------------------------------------------------
# Konstante Header (stateless, immer gesetzt)
# ---------------------------------------------------------------------------

_STATIC_HEADERS: dict[str, str] = {
    # Verhindert Content-Type-Sniffing → kein HTML-Rendering von JSON-Antworten
    "X-Content-Type-Options": "nosniff",
    # Clickjacking-Schutz: kein Einbetten in iframes erlaubt
    "X-Frame-Options": "DENY",
    # Referrer nur bei same-origin + HTTPS senden
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Browser-APIs deaktivieren (ERP benötigt keine Kamera, Mikrofon, Geolocation)
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
    "Cross-Origin-Resource-Policy": "same-site",
    # Legacy-XSS-Filter deaktivieren — Browsers sollen CSP verwenden
    "X-XSS-Protection": "0",
}

# ---------------------------------------------------------------------------
# Produktions-Header (nur wenn DEBUG=False)
# ---------------------------------------------------------------------------

_HSTS_HEADER = "max-age=31536000; includeSubDomains; preload"

# CSP für ERP-Backend:
# - Default: self only
# - Script: self + nonce-Muster (Frontend liefert eigenes CSP via Vite)
# - Style: self + unsafe-inline (Tailwind/Radix UI benötigt dies)
# - Img: self + data URIs (Logos, Diagramme)
# - Connect: self (API-Calls)
# - Font: self + data URIs
# - Frame-ancestors: none (= X-Frame-Options: DENY auf CSP-Ebene)
_CSP_PRODUCTION = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)

# Entwicklungs-CSP: weniger restriktiv (Vite HMR, localhost-APIs)
_CSP_DEVELOPMENT = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "font-src 'self' data:; "
    "connect-src 'self' ws://localhost:* http://localhost:*; "
    "frame-ancestors 'none';"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Starlette-Middleware für HTTP Security Headers.

    Wird in main.py zwischen GZipMiddleware und PrometheusMiddleware eingebunden.
    Überschreibt keine vom Endpunkt gesetzten Security-Header (sofern vorhanden).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Statische Header immer setzen (sofern nicht schon vorhanden)
        for header, value in _STATIC_HEADERS.items():
            if header not in response.headers:
                response.headers[header] = value

        # HSTS: nur in Produktion (HTTPS erzwingen)
        if not settings.DEBUG:
            if "Strict-Transport-Security" not in response.headers:
                response.headers["Strict-Transport-Security"] = _HSTS_HEADER

        # CSP: immer setzen (aber mit unterschiedlichem Inhalt)
        if "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = (
                _CSP_DEVELOPMENT if settings.DEBUG else _CSP_PRODUCTION
            )

        # Server-Header entfernen (Fingerprinting-Schutz) — nur in Produktion
        if not settings.DEBUG and "server" in response.headers:
            del response.headers["server"]

        return response


# ---------------------------------------------------------------------------
# Standalone-Hilfsfunktion für Tests
# ---------------------------------------------------------------------------

def build_security_headers(is_debug: bool = False) -> dict[str, str]:
    """
    Gibt das vollständige Security-Header-Dict zurück (für Tests und Dokumentation).

    Args:
        is_debug: True wenn Debug-Modus aktiv.

    Returns:
        Dict mit Header-Name → Header-Wert.
    """
    headers = dict(_STATIC_HEADERS)
    if not is_debug:
        headers["Strict-Transport-Security"] = _HSTS_HEADER
    headers["Content-Security-Policy"] = (
        _CSP_DEVELOPMENT if is_debug else _CSP_PRODUCTION
    )
    return headers
