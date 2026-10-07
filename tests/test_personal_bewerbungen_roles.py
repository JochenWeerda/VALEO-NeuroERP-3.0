"""Recruiting authorization at the actual API dispatch, before database access."""
from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import personal_bewerbungen as endpoint
from app.auth.deps import get_current_user
from app.core.database import get_db

PREFIX = "/api/v1/personal/applications"
# Role class is a reviewed public contract, including destructive administration.
CASES = [
    ("GET", "", "read"),
    ("POST", "", "write"),
    ("GET", "/aufbewahrung", "read"),
    ("PUT", "/aufbewahrung", "admin"),
    ("GET", "/loeschlauf/faellig", "read"),
    ("GET", "/loeschlaeufe", "read"),
    ("POST", "/loeschlauf", "admin"),
    ("GET", "/einwilligungserklaerungen", "read"),
    ("POST", "/einwilligungserklaerungen", "admin"),
    ("GET", "/einwilligungserklaerungen/1", "read"),
    ("GET", "/candidate", "read"),
    ("PATCH", "/candidate/stage", "write"),
    ("DELETE", "/candidate", "admin"),
    ("GET", "/candidate/einwilligung", "read"),
    ("POST", "/candidate/einwilligung", "write"),
    ("DELETE", "/candidate/einwilligung", "write"),
]
ROLES = [None, "user", "FUTTERMITTEL_ADMIN", "PERSONAL_LESEN", "PERSONAL_BEARBEITEN", "PERSONAL_ADMIN", "admin", "manager"]
ALLOWED = {
    "read": {"PERSONAL_LESEN", "PERSONAL_BEARBEITEN", "PERSONAL_ADMIN", "admin", "manager"},
    "write": {"PERSONAL_BEARBEITEN", "PERSONAL_ADMIN", "admin", "manager"},
    "admin": {"PERSONAL_ADMIN", "admin"},
}

@pytest.fixture
def api():
    app = FastAPI()
    app.include_router(endpoint.router, prefix="/api/v1")
    calls = []
    def database_boundary():
        calls.append("database")
        raise HTTPException(418, "authorized database boundary")
    app.dependency_overrides[get_db] = database_boundary
    with TestClient(app) as client:
        yield app, client, calls

@pytest.mark.parametrize("method,suffix,access", CASES)
@pytest.mark.parametrize("role", ROLES)
def test_role_matrix_before_database(api, method, suffix, access, role):
    app, client, calls = api
    app.dependency_overrides[get_current_user] = lambda: {"sub": "staff", "roles": [] if role is None else [role]}
    response = client.request(method, PREFIX + suffix, json={})
    allowed = role in ALLOWED[access]
    assert response.status_code == (418 if allowed else 403), response.text
    assert calls == (["database"] if allowed else [])

@pytest.mark.parametrize("method,suffix,access", CASES)
@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer invalid-token"}])
def test_real_authentication_required_before_database(api, method, suffix, access, headers):
    _, client, calls = api
    response = client.request(method, PREFIX + suffix, json={}, headers=headers)
    assert response.status_code in (401, 403), response.text
    assert calls == []


def test_all_routes_have_a_reviewed_access_class():
    routes = {(method, route.path.replace("{application_id}", "candidate").replace("{fassung}", "1"))
              for route in endpoint.router.routes for method in route.methods}
    assert routes == {(method, "/personal/applications" + suffix) for method, suffix, _ in CASES}
