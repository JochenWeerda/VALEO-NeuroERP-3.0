"""Gap-Fix Tests Batch 3: Silo PUT/DELETE, Charges PUT, CreditNotes DELETE, Settlements reject.

Alle neuen Endpoints aus dem dritten Gap-Fix-Durchlauf.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# SILO — PUT/DELETE silos and lots
# ===========================================================================

def test_put_nonexistent_silo_returns_404():
    payload = {"silo_number": "S-99", "name": "Test", "capacity_tons": 100}
    resp = _client.put("/api/v1/silo/silos/does-not-exist", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_silo_returns_404():
    resp = _client.delete("/api/v1/silo/silos/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_put_nonexistent_silo_lot_returns_404():
    payload = {"virtual_lot_number": "L-001", "quantity_tons": 10}
    resp = _client.put("/api/v1/silo/silos/no-silo/lots/no-lot", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_silo_lot_returns_404():
    resp = _client.delete("/api/v1/silo/silos/no-silo/lots/no-lot", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_silos_returns_200():
    resp = _client.get("/api/v1/silo/silos", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# CHARGES — PUT (full replacement)
# ===========================================================================

def test_put_nonexistent_charge_returns_404():
    payload = {"charge_number": "C-001", "article_id": "art-001", "quantity": 100}
    resp = _client.put("/api/v1/chargen/C-DOES-NOT-EXIST", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_charges_returns_200():
    resp = _client.get("/api/v1/chargen", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# SALES CREDIT NOTES — DELETE
# ===========================================================================

def test_delete_nonexistent_credit_note_returns_404():
    resp = _client.delete("/api/v1/sales/credit-notes/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_return_returns_404():
    resp = _client.delete("/api/v1/sales/returns/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_credit_notes_returns_200():
    resp = _client.get("/api/v1/sales/credit-notes", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_list_returns_returns_200():
    resp = _client.get("/api/v1/sales/returns", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# AGRAR SETTLEMENTS — reject
# ===========================================================================

def test_reject_nonexistent_settlement_returns_404():
    resp = _client.post(
        "/api/v1/agrar/settlements/does-not-exist/reject"
        "?actor_id=user-1&reason=Fehler+in+Berechnung",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_reject_settlement_missing_required_params_returns_422():
    resp = _client.post(
        "/api/v1/agrar/settlements/any-id/reject",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422
