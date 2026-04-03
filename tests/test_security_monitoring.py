from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.security_monitoring import router
from app.core.outbound_security import OutboundTargetPolicyError, validate_outbound_http_target
from app.core.tenant_isolation_guard import IsolationDecision, TenantIsolationGuard
from app.services.security_observability import security_observer


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


def test_security_monitoring_metrics_include_outbound_blocks():
    security_observer.reset()

    try:
        validate_outbound_http_target("http://127.0.0.1/internal")
    except OutboundTargetPolicyError:
        pass

    response = _client().get("/api/v1/security/monitoring/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["event_count"] == 1
    assert body["by_category"]["outbound_http"] == 1
    assert body["by_outcome"]["blocked"] == 1


def test_security_monitoring_health_reflects_denied_tenant_events():
    security_observer.reset()
    guard = TenantIsolationGuard()

    decision = guard.check(
        requesting_tenant="tenant-a",
        resource_tenant="tenant-b",
        resource_type="journal_entry",
    )

    response = _client().get("/api/v1/security/monitoring/health")

    assert decision == IsolationDecision.DENIED
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "warning"
    assert body["denied_count"] == 1


def test_security_monitoring_events_endpoint_supports_filters():
    security_observer.reset()
    try:
        validate_outbound_http_target("http://10.0.0.5/hook")
    except OutboundTargetPolicyError:
        pass

    TenantIsolationGuard().check(
        requesting_tenant="tenant-a",
        resource_tenant="tenant-b",
        resource_type="payment_run",
    )

    response = _client().get("/api/v1/security/monitoring/events?category=tenant_isolation&limit=5")

    assert response.status_code == 200
    body = response.json()
    assert body["event_count"] == 1
    assert body["events"][0]["category"] == "tenant_isolation"
    assert body["events"][0]["outcome"] == "denied"
