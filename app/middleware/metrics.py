"""
Prometheus Metrics Middleware
Tracks HTTP requests, latency, and errors
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

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


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track Prometheus metrics for all HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        path = request.url.path
        
        # Simplify path (remove IDs for better aggregation)
        endpoint = self._simplify_path(path)
        
        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = response.status_code
            
            # Track request
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            return response
            
        except Exception:
            # Track errors
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()
            raise
            
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
            if "status" in locals() and status >= 500:
                http_slo_error_violations_total.labels(
                    method=method, endpoint=endpoint
                ).inc()
    
    def _simplify_path(self, path: str) -> str:
        """Simplify path by replacing UUIDs and IDs with placeholders."""
        import re
        
        # Replace UUIDs
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}',
            path,
            flags=re.IGNORECASE
        )
        
        # Replace numeric IDs
        path = re.sub(r'/\d+(/|$)', '/{id}\\1', path)
        
        return path

