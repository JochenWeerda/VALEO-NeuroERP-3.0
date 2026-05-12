"""Gap-Fix Tests Batch 4: Warehouses CRUD, BankAccounts DELETE, NumberRanges GET/PUT/DELETE.

Fehlende CRUD-Operationen auf Master-Daten-Endpunkten.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# WAREHOUSES — POST / PUT / DELETE
# ===========================================================================

def test_list_warehouses_returns_200():
    resp = _client.get("/api/v1/warehouses/", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_get_nonexistent_warehouse_returns_404():
    resp = _client.get("/api/v1/warehouses/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_warehouse_missing_fields_returns_422():
    resp = _client.post("/api/v1/warehouses/", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_put_nonexistent_warehouse_returns_404():
    payload = {"name": "Updated", "is_active": False}
    resp = _client.put("/api/v1/warehouses/does-not-exist", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_warehouse_returns_404():
    resp = _client.delete("/api/v1/warehouses/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


# ===========================================================================
# BANK ACCOUNTS — DELETE
# ===========================================================================

def test_list_bank_accounts_returns_200():
    resp = _client.get("/api/v1/finance/bank-accounts", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_delete_nonexistent_bank_account_returns_404():
    resp = _client.delete("/api/v1/finance/bank-accounts/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


# ===========================================================================
# NUMBER RANGES — GET/{type} / PUT / DELETE
# ===========================================================================

def test_list_number_ranges_returns_200():
    resp = _client.get("/api/v1/admin/number-ranges/", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_get_nonexistent_number_range_returns_404():
    resp = _client.get("/api/v1/admin/number-ranges/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_number_range_returns_404():
    resp = _client.delete("/api/v1/admin/number-ranges/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_put_number_range_missing_fields_returns_422():
    resp = _client.put("/api/v1/admin/number-ranges/debtor_account", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    # 422 on missing fields, or 404 if range doesn't exist (depends on validation order)
    assert resp.status_code in (404, 422)
