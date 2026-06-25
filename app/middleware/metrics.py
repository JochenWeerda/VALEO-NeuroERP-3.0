"""
Prometheus Metrics Middleware
Tracks HTTP requests, latency, and errors
"""

import re
import time
import logging
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Precompiled once at import (was compiled per-request in the old implementation)
_UUID_RE = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    flags=re.IGNORECASE,
)
_NUMERIC_ID_RE = re.compile(r'/\d+(/|$)')


def _simplify_path(path: str) -> str:
    """Replace UUIDs and numeric IDs with placeholders for metric aggregation."""
    path = _UUID_RE.sub('{id}', path)
    path = _NUMERIC_ID_RE.sub('/{id}\\1', path)
    return path

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# SLO target: P99 < 500ms  →  buckets tuned around the 500ms threshold
_SLO_LATENCY_BUCKETS = (0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=_SLO_LATENCY_BUCKETS,
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method', 'endpoint']
)

# SLO breach counters — alert when these increase
http_slo_latency_violations_total = Counter(
    'http_slo_latency_violations_total',
    'HTTP requests that exceeded the P99 SLO threshold (500ms)',
    ['method', 'endpoint'],
)

http_slo_error_violations_total = Counter(
    'http_slo_error_violations_total',
    'HTTP 5xx responses (SLO: error rate < 0.1%)',
    ['method', 'endpoint'],
)


class PrometheusMiddleware:
    """Pure ASGI middleware to track Prometheus metrics (PERF-MULTIUSER-001).

    Ersetzt die frühere BaseHTTPMiddleware: liest Methode/Pfad aus dem Scope,
    erfasst den Status-Code aus der ``http.response.start``-Nachricht und
    vermeidet den anyio-Stream-Overhead pro Request.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] == "/metrics":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        endpoint = _simplify_path(scope["path"])

        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        start_time = time.time()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            http_requests_total.labels(method=method, endpoint=endpoint, status=500).inc()
            raise
        else:
            http_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
        finally:
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

            # SLO breach tracking
            if duration > 0.5:
                http_slo_latency_violations_total.labels(
                    method=method, endpoint=endpoint
                ).inc()
            if status_code >= 500:
                http_slo_error_violations_total.labels(
                    method=method, endpoint=endpoint
                ).inc()

