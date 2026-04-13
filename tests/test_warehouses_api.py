"""
COV-INV-002: Tests for Warehouses API endpoints.

Covers /api/v1/warehouses — list, get, 404, Superglue carrier rollout.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


class TestWarehousesList:
    """GET /warehouses/"""

    def test_list_returns_paginated(self):
        r = client.get("/api/v1/warehouses/", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data

    def test_list_with_pagination(self):
        r = client.get("/api/v1/warehouses/?skip=0&limit=5", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_with_search(self):
        r = client.get("/api/v1/warehouses/?search=Haupt", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_with_tenant_filter(self):
        r = client.get("/api/v1/warehouses/?tenant_id=test-tenant", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


class TestWarehouseDetail:
    """GET /warehouses/{warehouse_id}"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/warehouses/NONEXISTENT-WH-ID", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestSuperglueCarrierRollout:
    """GET /warehouses/integrations/superglue/carrier-rollout"""

    def test_returns_rollout_structure(self):
        r = client.get(
            "/api/v1/warehouses/integrations/superglue/carrier-rollout",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert data["provider_key"] == "superglue"
        assert data["domain_key"] == "logistics"
        assert "rollout" in data

    def test_with_tenant_param(self):
        r = client.get(
            "/api/v1/warehouses/integrations/superglue/carrier-rollout?tenant_id=test-tenant",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert data["tenant_id"] == "test-tenant"
