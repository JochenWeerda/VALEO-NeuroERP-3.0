"""
Prometheus Metrics
"""

from prometheus_client import Counter, Histogram, Gauge

# Workflow-Metriken
workflow_transitions_total = Counter(
    'workflow_transitions_total',
    'Total workflow transitions',
    ['domain', 'action', 'status']
)

# Document-Metriken
document_print_duration_seconds = Histogram(
    'document_print_duration_seconds',
    'PDF generation duration',
    ['domain']
)

# SSE-Metriken
sse_connections_active = Gauge(
    'sse_connections_active',
    'Active SSE connections',
    ['channel']
)

# API-Metriken
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

