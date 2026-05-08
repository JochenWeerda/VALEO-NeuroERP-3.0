"""DOM-INV-002: Tests fuer silo_operations_api.py.

Abdeckung: SiloZelleCreateRequest/EinlagerungRequest/AuslagerungRequest, HTTP smoke.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.silo_operations_api import (
    SiloZelleCreateRequest,
    EinlagerungRequest,
    AuslagerungRequest,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------

def test_silo_zelle_create_requires_bezeichnung():
    with pytest.raises(Exception):
        SiloZelleCreateRequest(tenant_id="t1", kapazitaet_t=100.0)


def test_silo_zelle_create_valid():
    req = SiloZelleCreateRequest(tenant_id="t1", bezeichnung="Silo-A1", kapazitaet_t=500.0)
    assert req.bezeichnung == "Silo-A1"
    assert req.kapazitaet_t == 500.0


def test_einlagerung_requires_menge():
    with pytest.raises(Exception):
        EinlagerungRequest(tenant_id="t1", silo_id="s1", sorte="Weizen")


def test_einlagerung_valid():
    req = EinlagerungRequest(tenant_id="t1", silo_id="s1", menge_t=50.0, sorte="Weizen")
    assert req.menge_t == 50.0


def test_auslagerung_requires_menge():
    with pytest.raises(Exception):
        AuslagerungRequest(tenant_id="t1", silo_id="s1")


def test_auslagerung_valid():
    req = AuslagerungRequest(tenant_id="t1", silo_id="s1", menge_t=20.0)
    assert req.menge_t == 20.0


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_create_silo_zelle_missing_fields_smoke():
    # Duplicate guard: POST /silo/zellen with missing fields always returns 422
    resp = _client.post("/api/v1/silo/zellen", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_get_nonexistent_silo_zelle_returns_404():
    resp = _client.get("/api/v1/silo/zellen/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_silo_zelle_missing_fields_returns_422():
    resp = _client.post("/api/v1/silo/zellen", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_einlagerung_missing_fields_returns_422():
    resp = _client.post("/api/v1/silo/zellen/z-001/einlagerung", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 422)


def test_auslagerung_missing_fields_returns_422():
    resp = _client.post("/api/v1/silo/zellen/z-001/auslagerung", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 422)
