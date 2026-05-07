"""
Tests for GDPR API endpoints.

Covers /api/v1/gdpr — GET /data-export/{user_id},
DELETE /delete-user/{user_id}, GET /export-portable/{user_id}
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.core.database import get_db
from app.core.tenant import get_tenant_id

AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
BASE = "/api/v1/gdpr"


# ---------------------------------------------------------------------------
# Fake helpers
# ---------------------------------------------------------------------------

def _make_user(uid: str = "USER-1"):
    u = MagicMock()
    u.id = uid
    u.username = "testuser"
    u.email = "test@example.com"
    u.first_name = "Test"
    u.last_name = "User"
    u.roles = ["user"]
    u.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    u.tenant_id = "test-tenant"
    return u


class _FakeQuery:
    def __init__(self, first_result=None, all_results=None):
        self._first = first_result
        self._all = list(all_results or [])

    def filter(self, *_a):
        return self

    def limit(self, _n):
        return self

    def all(self):
        return self._all

    def first(self):
        return self._first

    def update(self, _data):
        return 0


class _FakeDb:
    def __init__(self, user=None, audit_logs=None):
        self._user = user
        self._audit_logs = list(audit_logs or [])
        self._committed = False

    def query(self, model):
        # Distinguish User vs AuditLog by model name
        name = getattr(model, "__name__", "") or getattr(model, "__tablename__", "")
        if "User" in str(name):
            return _FakeQuery(first_result=self._user)
        # AuditLog queries
        return _FakeQuery(first_result=None, all_results=self._audit_logs)

    def commit(self):
        self._committed = True

    def rollback(self):
        pass


def _unit_app(db):
    from app.api.v1.endpoints.gdpr import router as gdpr_router
    unit = FastAPI()
    unit.include_router(gdpr_router, prefix="/gdpr")
    unit.dependency_overrides[get_db] = lambda: db
    unit.dependency_overrides[get_tenant_id] = lambda: "test-tenant"
    return unit


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestGdprIntegration:
    def setup_method(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_data_export_nonexistent_user_integration(self):
        r = self.client.get(f"{BASE}/data-export/NONEXISTENT-USER", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code in (404, 500)

    def test_delete_user_nonexistent_integration(self):
        r = self.client.delete(f"{BASE}/delete-user/NONEXISTENT-USER", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code in (404, 500)

    def test_export_portable_nonexistent_integration(self):
        r = self.client.get(f"{BASE}/export-portable/NONEXISTENT-USER", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code in (404, 500)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestGdprDataExportUnit:
    def test_data_export_user_not_found_returns_404(self):
        db = _FakeDb(user=None)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.get("/gdpr/data-export/NONEXISTENT", headers=AUTH)
        assert r.status_code == 404

    def test_data_export_existing_user_returns_200(self):
        user = _make_user("USER-1")
        db = _FakeDb(user=user)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.get("/gdpr/data-export/USER-1", headers=AUTH)
        assert r.status_code == 200
        data = r.json()
        assert "personal_data" in data
        assert "audit_logs" in data
        assert "export_metadata" in data

    def test_data_export_personal_data_fields(self):
        user = _make_user("USER-1")
        db = _FakeDb(user=user)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.get("/gdpr/data-export/USER-1", headers=AUTH)
        pd = r.json()["personal_data"]
        assert pd["id"] == "USER-1"
        assert pd["email"] == "test@example.com"

    def test_data_export_audit_logs_empty(self):
        user = _make_user("USER-1")
        db = _FakeDb(user=user, audit_logs=[])
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.get("/gdpr/data-export/USER-1", headers=AUTH)
        assert r.json()["audit_logs"] == []


class TestGdprDeleteUserUnit:
    def test_delete_user_not_found_returns_404(self):
        db = _FakeDb(user=None)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.delete("/gdpr/delete-user/NONEXISTENT", headers=AUTH)
        assert r.status_code == 404

    def test_delete_existing_user_returns_204(self):
        user = _make_user("USER-1")
        db = _FakeDb(user=user)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.delete("/gdpr/delete-user/USER-1", headers=AUTH)
        assert r.status_code == 204

    def test_delete_commits_to_db(self):
        user = _make_user("USER-1")
        db = _FakeDb(user=user)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        client.delete("/gdpr/delete-user/USER-1", headers=AUTH)
        assert db._committed


class TestGdprExportPortableUnit:
    def test_export_portable_user_not_found_returns_404(self):
        db = _FakeDb(user=None)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.get("/gdpr/export-portable/NONEXISTENT", headers=AUTH)
        assert r.status_code == 404

    def test_export_portable_returns_portability_metadata(self):
        user = _make_user("USER-1")
        db = _FakeDb(user=user)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.get("/gdpr/export-portable/USER-1", headers=AUTH)
        assert r.status_code == 200
        data = r.json()
        assert "portability_metadata" in data
        assert "personal_data" in data

    def test_export_portable_has_gdpr_standard(self):
        user = _make_user("USER-1")
        db = _FakeDb(user=user)
        client = TestClient(_unit_app(db), raise_server_exceptions=False)
        r = client.get("/gdpr/export-portable/USER-1", headers=AUTH)
        meta = r.json()["portability_metadata"]
        assert "GDPR Article 20" in meta["standards"]
