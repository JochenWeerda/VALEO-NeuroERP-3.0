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

# Kernel / Neuro: Audit-Inserts (ohne Tenant-Label — Cardinality)
neuro_kernel_audit_inserts_total = Counter(
    'neuro_kernel_audit_inserts_total',
    'Successful audit rows written to neuro_step_audit_trace (kernel execute + broker)',
)

# NATS / Event-Bus (EventBusObserver) — Scraping: GET /metrics (root main.py)
valeo_event_bus_events_received_total = Counter(
    'valeo_event_bus_events_received_total',
    'Events received by in-process event bus observer',
)
valeo_event_bus_events_processed_total = Counter(
    'valeo_event_bus_events_processed_total',
    'Events processed successfully',
)
valeo_event_bus_events_failed_total = Counter(
    'valeo_event_bus_events_failed_total',
    'Events failed during processing',
)
valeo_event_bus_dlq_entries_total = Counter(
    'valeo_event_bus_dlq_entries_total',
    'Events sent to DLQ',
)

# Strecke / Streckengeschäfte (M-11 Betrieb)
strecke_operations_total = Counter(
    'strecke_operations_total',
    'Streckengeschaefte Erstell-/Mutationsbewegungen',
    ['operation'],
)

# Tenant-Authentifizierung/-Autorisierung (Phase 4 — Observability)
tenant_auth_errors_total = Counter(
    'tenant_auth_errors_total',
    'Tenant authentication and authorization errors by route and error type',
    ['route', 'error_type'],  # error_type: missing_tenant | forbidden_tenant | unauthorized
)
