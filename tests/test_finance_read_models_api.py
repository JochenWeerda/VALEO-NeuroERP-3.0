"""
COV-FIN-002: Tests for Finance Read Models API endpoints.

Covers /api/v1/finance/read-models — cockpits, cash closings,
settlement, projections status and rebuild.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


class TestAPInvoiceCockpit:
    """GET /finance/read-models/ap-invoice-cockpit"""

    def test_returns_structured_cockpit(self):
        r = client.get("/api/v1/finance/read-models/ap-invoice-cockpit", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "buckets" in data
        assert "total_count" in data


class TestPaymentRunCockpit:
    """GET /finance/read-models/payment-run-cockpit"""

    def test_returns_structured_cockpit(self):
        r = client.get("/api/v1/finance/read-models/payment-run-cockpit", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "draft_count" in data
        assert "total_pending_amount" in data


class TestCashClosings:
    """GET /finance/read-models/cash-closings*"""

    def test_list_cash_closings(self):
        r = client.get("/api/v1/finance/read-models/cash-closings", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total_count" in data

    def test_cash_closings_analysis(self):
        r = client.get("/api/v1/finance/read-models/cash-closings/analysis", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "total_count" in data
        assert "exception_count" in data

    def test_cash_closings_reporting(self):
        r = client.get("/api/v1/finance/read-models/cash-closings/reporting", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "periods" in data
        assert "total_count" in data

    def test_get_closing_nonexistent_404(self):
        r = client.get("/api/v1/finance/read-models/cash-closings/NONEXISTENT", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestProcessObservation:
    """GET /finance/read-models/process-observation"""

    def test_returns_structured_observation(self):
        r = client.get("/api/v1/finance/read-models/process-observation", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data


class TestSettlementCockpit:
    """GET /finance/read-models/settlement-cockpit"""

    def test_returns_dict(self):
        r = client.get("/api/v1/finance/read-models/settlement-cockpit", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), dict)


class TestProjectionManagement:
    """POST/GET /finance/read-models/_rebuild, _status"""

    def test_status_returns_projection_state(self):
        r = client.get("/api/v1/finance/read-models/_status", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "projection_count" in data

    def test_rebuild_triggers_projection_refresh(self):
        r = client.post("/api/v1/finance/read-models/_rebuild", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "rebuilt_at" in data
        assert "projections" in data
