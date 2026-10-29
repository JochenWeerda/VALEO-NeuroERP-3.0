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

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id

AUTH = {}  # Unit identity is supplied explicitly by the miniature-app fixture.


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
    # This miniature app tests response/SQL-error handling; signed identities
    # and actual SQL authorization are covered by test_gdpr_subject_boundary.
    unit.dependency_overrides[get_current_user] = lambda: {"sub": "synthetic-privacy-admin", "roles": ["admin"]}
    return unit


# ---------------------------------------------------------------------------
# Missing subjects fail with an exact status; real integration is separate.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('operation,method', [('data-export','GET'),('export-portable','GET'),('delete-user','DELETE')])
def test_missing_subject_is_404_not_a_server_error(operation, method):
    client = TestClient(_unit_app(_FakeDb(user=None)), raise_server_exceptions=False)
    assert client.request(method, f'/gdpr/{operation}/NONEXISTENT', headers=AUTH).status_code == 404


@pytest.mark.parametrize('operation,method', [('data-export','GET'),('export-portable','GET'),('delete-user','DELETE')])
def test_storage_errors_do_not_disclose_personal_values(operation, method, caplog):
    class BrokenDb(_FakeDb):
        def query(self, _model):
            raise RuntimeError('SYNTHETIC-PRIVATE-INPUT')
    response = TestClient(_unit_app(BrokenDb()), raise_server_exceptions=False).request(method, f'/gdpr/{operation}/USER-1',headers=AUTH)
    assert response.status_code == 500
    assert 'SYNTHETIC-PRIVATE-INPUT' not in response.text + caplog.text


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
