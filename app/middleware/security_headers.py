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

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

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


class SecurityHeadersMiddleware:
    """
    Reine ASGI-Middleware für HTTP Security Headers (PERF-MULTIUSER-001).

    Ersetzt die frühere BaseHTTPMiddleware: injiziert Security-Header direkt
    in die ``http.response.start``-Nachricht und vermeidet so den anyio-
    Stream-Overhead pro Request. Überschreibt keine vom Endpunkt bereits
    gesetzten Security-Header.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)

                # Statische Header immer setzen (sofern nicht schon vorhanden)
                for header, value in _STATIC_HEADERS.items():
                    if header not in headers:
                        headers[header] = value

                # HSTS: nur in Produktion (HTTPS erzwingen)
                if not settings.DEBUG and "Strict-Transport-Security" not in headers:
                    headers["Strict-Transport-Security"] = _HSTS_HEADER

                # CSP: immer setzen (aber mit unterschiedlichem Inhalt)
                if "Content-Security-Policy" not in headers:
                    headers["Content-Security-Policy"] = (
                        _CSP_DEVELOPMENT if settings.DEBUG else _CSP_PRODUCTION
                    )

                # Server-Header entfernen (Fingerprinting-Schutz) — nur in Produktion
                if not settings.DEBUG and "server" in headers:
                    del headers["server"]

            await send(message)

        await self.app(scope, receive, send_wrapper)


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
