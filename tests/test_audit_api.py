"""
Tests for Audit API endpoints.

Covers /api/v1/audit — POST /log, GET /logs, GET /stats
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.core.database import get_db

AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
BASE = "/api/v1/audit"


# ---------------------------------------------------------------------------
# Fake DB helpers
# ---------------------------------------------------------------------------

def _make_log(lid: str = "LOG-1"):
    log = MagicMock()
    log.id = lid
    log.timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    log.user_id = "USER-1"
    log.user_email = "user@example.com"
    log.tenant_id = "test-tenant"
    log.action = "CREATE"
    log.entity_type = "invoice"
    log.entity_id = "INV-1"
    log.changes = {}
    log.ip_address = "127.0.0.1"
    log.user_agent = "test-agent"
    log.correlation_id = "corr-1"
    return log


class _FakeQuery:
    def __init__(self, items=None):
        self._items = list(items or [])

    def filter(self, *_a):
        return self

    def order_by(self, *_a):
        return self

    def offset(self, n):
        self._items = self._items[n:]
        return self

    def limit(self, n):
        self._items = self._items[:n]
        return self

    def all(self):
        return list(self._items)

    def count(self):
        return len(self._items)

    def group_by(self, *_a):
        return self


class _FakeDb:
    def __init__(self, items=None):
        self._items = list(items or [])

    def query(self, _m):
        return _FakeQuery(self._items)


class _ErrorDb:
    """DB that raises on every query call."""

    def query(self, _m):
        raise RuntimeError("DB unavailable")


def _unit_app(db):
    from app.api.v1.endpoints.audit import router as audit_router
    unit = FastAPI()
    unit.include_router(audit_router, prefix="/audit")
    unit.dependency_overrides[get_db] = lambda: db
    return unit


# ---------------------------------------------------------------------------
# Integration tests (main app — DB may not be available)
# ---------------------------------------------------------------------------

class TestAuditIntegration:
    def setup_method(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_get_logs_integration(self):
        r = self.client.get(f"{BASE}/logs", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_stats_integration(self):
        r = self.client.get(f"{BASE}/stats", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "total_entries" in data

    def test_get_logs_with_filters_integration(self):
        r = self.client.get(
            f"{BASE}/logs?tenant_id=test-tenant&action=CREATE",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_get_stats_with_tenant_integration(self):
        r = self.client.get(f"{BASE}/stats?tenant_id=test-tenant", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Unit tests (isolated FastAPI app with fake DB)
# ---------------------------------------------------------------------------

class TestAuditLogsUnit:
    def setup_method(self):
        self.log = _make_log()
        self.db = _FakeDb([self.log])
        self.client = TestClient(_unit_app(self.db), raise_server_exceptions=False)

    def test_get_logs_returns_200(self):
        r = self.client.get("/audit/logs", headers=AUTH)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "LOG-1"

    def test_get_logs_returns_list_with_expected_fields(self):
        r = self.client.get("/audit/logs", headers=AUTH)
        assert r.status_code == 200
        item = r.json()[0]
        for key in ("id", "user_id", "user_email", "tenant_id", "action", "entity_type", "entity_id", "changes"):
            assert key in item

    def test_get_logs_filter_params_accepted(self):
        r = self.client.get(
            "/audit/logs?tenant_id=test-tenant&entity_type=invoice&action=CREATE",
            headers=AUTH,
        )
        assert r.status_code == 200

    def test_get_logs_empty_db(self):
        empty_client = TestClient(_unit_app(_FakeDb([])), raise_server_exceptions=False)
        r = empty_client.get("/audit/logs", headers=AUTH)
        assert r.status_code == 200
        assert r.json() == []

    def test_get_logs_db_error_returns_empty_list(self):
        err_client = TestClient(_unit_app(_ErrorDb()), raise_server_exceptions=False)
        r = err_client.get("/audit/logs", headers=AUTH)
        assert r.status_code == 200
        assert r.json() == []

    def test_get_logs_pagination_params_accepted(self):
        r = self.client.get("/audit/logs?skip=0&limit=10", headers=AUTH)
        assert r.status_code == 200


class TestAuditStatsUnit:
    def setup_method(self):
        self.db = _FakeDb([])
        self.client = TestClient(_unit_app(self.db), raise_server_exceptions=False)

    def test_get_stats_returns_200(self):
        r = self.client.get("/audit/stats", headers=AUTH)
        assert r.status_code == 200

    def test_get_stats_has_required_keys(self):
        r = self.client.get("/audit/stats", headers=AUTH)
        data = r.json()
        for key in ("total_entries", "actions", "entity_types", "top_users", "timestamp"):
            assert key in data

    def test_get_stats_with_tenant_id_filter(self):
        r = self.client.get("/audit/stats?tenant_id=test-tenant", headers=AUTH)
        assert r.status_code == 200

    def test_get_stats_db_error_returns_default(self):
        err_client = TestClient(_unit_app(_ErrorDb()), raise_server_exceptions=False)
        r = err_client.get("/audit/stats", headers=AUTH)
        assert r.status_code == 200
        data = r.json()
        assert data["total_entries"] == 0
        assert data["actions"] == []
        assert data["entity_types"] == []
        assert data["top_users"] == []
        assert "timestamp" in data

    def test_get_stats_zero_total_with_empty_db(self):
        r = self.client.get("/audit/stats", headers=AUTH)
        data = r.json()
        assert data["total_entries"] == 0
