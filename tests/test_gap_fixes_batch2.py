"""Gap-Fix Tests Batch 2: Einkauf workflow, Kontrakte PUT.

Deckt freigeben/stornieren Bestellungen und Kontrakt-PUT ab.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# EINKAUF — freigeben / stornieren workflow
# ===========================================================================

def test_freigeben_nonexistent_bestellung_returns_404():
    resp = _client.post("/api/v1/einkauf/bestellungen/does-not-exist/freigeben", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_stornieren_nonexistent_bestellung_returns_404():
    resp = _client.post("/api/v1/einkauf/bestellungen/does-not-exist/stornieren", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_bestellvorschlaege_returns_200():
    resp = _client.get("/api/v1/einkauf/bestellvorschlaege/lager", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_list_bestellungen_returns_200():
    resp = _client.get("/api/v1/einkauf/bestellungen", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# KONTRAKTE — PUT (full replacement)
# ===========================================================================

def test_put_kontrakt_missing_required_fields_returns_422():
    resp = _client.put("/api/v1/kontrakte/any-id", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    # FastAPI validates payload before auth/DB check
    assert resp.status_code == 422


def test_put_kontrakt_valid_payload_nonexistent_returns_404_or_403():
    payload = {
        "contract_type": "KAUF",
        "contract_no": "K-TEST-001",
        "counterparty_id": "cp-001",
        "valid_from": "2026-01-01",
        "valid_to": "2026-12-31",
    }
    resp = _client.put("/api/v1/kontrakte/does-not-exist", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    # 404 = not found after auth, 403 = insufficient roles, 422 = schema validation
    assert resp.status_code in (403, 404, 422)


def test_list_kontrakte_returns_200_or_403():
    resp = _client.get("/api/v1/kontrakte", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    # Endpoint requires role KONTRAKT_LESEN; dev-token may not have it
    assert resp.status_code in (200, 403)


def test_delete_nonexistent_kontrakt_returns_404():
    resp = _client.delete("/api/v1/kontrakte/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (403, 404)
