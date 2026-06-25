"""
test_middleware_asgi.py — PERF-MULTIUSER-001

Verifiziert, dass die auf reine ASGI umgestellten Middleware
(SecurityHeaders, Correlation, Prometheus, Audit) ihr fachliches Verhalten
behalten: Security-Header werden gesetzt, Correlation-ID wird gespiegelt/
übernommen, Audit loggt nur Mutationen, und der Stack verändert Responses
nicht inhaltlich.
"""
from __future__ import annotations

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.correlation import CORRELATION_ID_HEADER, CorrelationMiddleware
from app.middleware.metrics import PrometheusMiddleware, _simplify_path
from app.middleware.security_headers import SecurityHeadersMiddleware


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()

    @app.get("/api/v1/ping")
    async def ping() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/api/v1/kontrakte")
    async def create_kontrakt() -> dict[str, bool]:
        return {"created": True}

    # Reihenfolge wie main.py (innen → außen)
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(AuditMiddleware)
    return TestClient(app)


def test_security_headers_present(client: TestClient) -> None:
    resp = client.get("/api/v1/ping")
    assert resp.status_code == 200
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in resp.headers
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_correlation_id_generated(client: TestClient) -> None:
    resp = client.get("/api/v1/ping")
    assert resp.headers.get(CORRELATION_ID_HEADER)


def test_correlation_id_roundtrip(client: TestClient) -> None:
    cid = "test-correlation-123"
    resp = client.get("/api/v1/ping", headers={CORRELATION_ID_HEADER: cid})
    assert resp.headers[CORRELATION_ID_HEADER] == cid


def test_audit_logs_only_mutations(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="audit"):
        client.get("/api/v1/ping")
    assert not [r for r in caplog.records if r.name == "audit"]

    caplog.clear()
    with caplog.at_level(logging.INFO, logger="audit"):
        client.post("/api/v1/kontrakte")
    audit_records = [r for r in caplog.records if r.name == "audit"]
    assert len(audit_records) == 1
    rec = audit_records[0]
    assert getattr(rec, "entity_type", None) == "kontrakte"
    assert getattr(rec, "status_code", None) == 200
    assert getattr(rec, "action", None) == "POST /api/v1/kontrakte"


def test_response_body_unchanged(client: TestClient) -> None:
    assert client.get("/api/v1/ping").json() == {"ok": True}
    assert client.post("/api/v1/kontrakte").json() == {"created": True}


def test_simplify_path_replaces_ids() -> None:
    assert _simplify_path("/api/v1/kontrakte/123") == "/api/v1/kontrakte/{id}"
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    assert _simplify_path(f"/api/v1/orders/{uuid}") == "/api/v1/orders/{id}"
