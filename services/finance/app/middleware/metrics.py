"""Prometheus instrumentation middleware."""

from __future__ import annotations

from time import perf_counter

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from services.finance.app.core.config import settings
from services.finance.app.middleware.correlation import get_correlation_id

REQUEST_COUNTER = Counter(
    f"{settings.PROMETHEUS_NAMESPACE}_requests_total",
    "Total number of HTTP requests",
    ("method", "path", "status_code"),
)

REQUEST_LATENCY = Histogram(
    f"{settings.PROMETHEUS_NAMESPACE}_request_duration_seconds",
    "Histogram of request processing time",
    ("method", "path", "status_code"),
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Records metrics for every HTTP request."""

    async def dispatch(self, request: Request, call_next):
        start = perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            status_code = response.status_code if response else 500
            route = request.scope.get("path", request.url.path)
            labels = {
                "method": request.method,
                "path": route,
                "status_code": str(status_code),
            }
            REQUEST_COUNTER.labels(**labels).inc()
            REQUEST_LATENCY.labels(**labels).observe(perf_counter() - start)

            # Attach correlation id for scraping convenience
            correlation_id = get_correlation_id()
            if response is not None and correlation_id:
                response.headers.setdefault("X-Correlation-ID", correlation_id)

