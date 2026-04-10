"""
Tests for TenantEnforcementMiddleware.

Tests the middleware logic in isolation using a minimal FastAPI app,
independent of the main application's middleware stack.

Validates:
- Requests without X-Tenant-ID are rejected on /api/v1/* paths
- Health/metrics/docs paths are exempt
- Invalid tenant IDs (special chars, too long) are rejected
- Valid tenant IDs pass through and set request.state.tenant_id
- Dev mode falls back to DEFAULT_TENANT_ID when API_DEV_TOKEN is set
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.core.config import settings
from app.middleware.tenant_enforcement import TenantEnforcementMiddleware, _TENANT_ID_PATTERN


# Build a minimal app with only TenantEnforcementMiddleware
def _make_app() -> FastAPI:
    test_app = FastAPI()
    test_app.add_middleware(TenantEnforcementMiddleware)

    @test_app.get("/api/v1/test")
    async def test_endpoint(request: Request):
        return {"tenant_id": getattr(request.state, "tenant_id", None)}

    @test_app.get("/api/v1/health")
    async def health():
        return {"status": "ok"}

    @test_app.get("/api/v1/metrics")
    async def metrics():
        return {"metrics": []}

    @test_app.get("/docs")
    async def docs():
        return {"docs": True}

    @test_app.get("/non-api/path")
    async def non_api():
        return {"ok": True}

    return test_app


@pytest.fixture
def app():
    return _make_app()


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


class TestTenantIdPattern:
    """Unit tests for the regex pattern."""

    def test_valid_simple(self):
        assert _TENANT_ID_PATTERN.match("tenant-001")

    def test_valid_underscores(self):
        assert _TENANT_ID_PATTERN.match("my_tenant_42")

    def test_valid_alphanumeric(self):
        assert _TENANT_ID_PATTERN.match("ABC123")

    def test_invalid_semicolon(self):
        assert not _TENANT_ID_PATTERN.match("tenant;DROP")

    def test_invalid_spaces(self):
        assert not _TENANT_ID_PATTERN.match("tenant 001")

    def test_invalid_empty(self):
        assert not _TENANT_ID_PATTERN.match("")

    def test_invalid_too_long(self):
        assert not _TENANT_ID_PATTERN.match("a" * 101)

    def test_valid_max_length(self):
        assert _TENANT_ID_PATTERN.match("a" * 100)

    def test_invalid_special_chars(self):
        assert not _TENANT_ID_PATTERN.match("tenant@org")
        assert not _TENANT_ID_PATTERN.match("tenant/path")
        assert not _TENANT_ID_PATTERN.match("tenant.name")


class TestExemptPaths:
    """Exempt paths should pass without X-Tenant-ID."""

    def test_health_no_tenant(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_metrics_no_tenant(self, client):
        resp = client.get("/api/v1/metrics")
        assert resp.status_code == 200

    def test_docs_no_tenant(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_non_api_no_tenant(self, client):
        resp = client.get("/non-api/path")
        assert resp.status_code == 200


class TestTenantValidation:
    """API paths should require valid X-Tenant-ID."""

    def test_valid_tenant_passes(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
        resp = client.get("/api/v1/test", headers={"X-Tenant-ID": "tenant-001"})
        assert resp.status_code == 200
        assert resp.json()["tenant_id"] == "tenant-001"

    def test_missing_tenant_rejected(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
        resp = client.get("/api/v1/test")
        assert resp.status_code == 400
        assert "required" in resp.json()["detail"].lower()

    def test_empty_tenant_rejected(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
        resp = client.get("/api/v1/test", headers={"X-Tenant-ID": ""})
        assert resp.status_code == 400

    def test_whitespace_tenant_rejected(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
        resp = client.get("/api/v1/test", headers={"X-Tenant-ID": "   "})
        assert resp.status_code == 400

    def test_invalid_chars_rejected(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
        resp = client.get("/api/v1/test", headers={"X-Tenant-ID": "tenant;DROP TABLE"})
        assert resp.status_code == 400
        assert "invalid characters" in resp.json()["detail"].lower()

    def test_too_long_tenant_rejected(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
        resp = client.get("/api/v1/test", headers={"X-Tenant-ID": "a" * 101})
        assert resp.status_code == 400

    def test_tenant_with_hyphens_underscores(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
        resp = client.get("/api/v1/test", headers={"X-Tenant-ID": "my_tenant-42"})
        assert resp.status_code == 200


class TestDevModeFallback:
    """Dev mode should fall back to DEFAULT_TENANT_ID when no header is sent."""

    def test_dev_mode_uses_default_tenant(self, client, monkeypatch):
        monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
        monkeypatch.setattr(settings, "DEFAULT_TENANT_ID", "dev-tenant")
        resp = client.get("/api/v1/test")
        assert resp.status_code == 200
        assert resp.json()["tenant_id"] == "dev-tenant"

    def test_dev_mode_still_validates_format(self, client, monkeypatch):
        """Even in dev mode, if a tenant ID IS provided, it must be valid."""
        monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
        resp = client.get("/api/v1/test", headers={"X-Tenant-ID": "bad;tenant"})
        assert resp.status_code == 400
