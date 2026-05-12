"""Gap-Fix Tests Batch 6+7: Förderung, DirectDebits, InventoryOps,
PreparationLists, HarvestAcceptance cancel, DeliveryNotes ship/deliver,
Sustainability DB-backed.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# FÖRDERUNG — GET/{id} + DELETE
# ===========================================================================

def test_get_nonexistent_antrag_returns_404():
    resp = _client.get("/api/v1/foerderung/antraege/999999", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_antrag_returns_404():
    resp = _client.delete("/api/v1/foerderung/antraege/999999", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_antraege_returns_200():
    resp = _client.get("/api/v1/foerderung/antraege", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# DIRECT DEBITS — GET/{run_id} + POST /{run_id}/export
# ===========================================================================

def test_get_nonexistent_direct_debit_run_returns_404():
    resp = _client.get("/api/v1/finance/direct-debits/RUN-DOES-NOT-EXIST", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_export_nonexistent_direct_debit_run_returns_404():
    resp = _client.post("/api/v1/finance/direct-debits/RUN-DOES-NOT-EXIST/export", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_direct_debits_returns_200():
    resp = _client.get("/api/v1/finance/direct-debits", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# INVENTORY OPERATIONS — GET /korrekturen/{id}
# ===========================================================================

def test_get_nonexistent_korrektur_returns_404():
    resp = _client.get("/api/v1/lager/korrekturen/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_korrekturen_returns_200():
    resp = _client.get("/api/v1/lager/korrekturen", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# PREPARATION LISTS — GET/{id}, PUT, DELETE
# ===========================================================================

def test_get_nonexistent_prep_list_returns_404():
    resp = _client.get("/api/v1/preparation-lists/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_put_nonexistent_prep_list_returns_404():
    resp = _client.put("/api/v1/preparation-lists/does-not-exist", json={"notes": "test"}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_prep_list_returns_404():
    resp = _client.delete("/api/v1/preparation-lists/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_prep_lists_returns_200():
    resp = _client.get("/api/v1/preparation-lists/", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# HARVEST ACCEPTANCE — cancel
# ===========================================================================

def test_cancel_nonexistent_acceptance_returns_404():
    resp = _client.post(
        "/api/v1/agrar/annahme/does-not-exist/cancel?reason=Test-Stornierung",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_cancel_acceptance_missing_reason_returns_422_or_404():
    resp = _client.post("/api/v1/agrar/annahme/any-id/cancel", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    # 422 when validation runs before DB; 404 when DB is available but record missing
    assert resp.status_code in (404, 422)


# ===========================================================================
# DELIVERY NOTES — ship / deliver workflow
# ===========================================================================

def test_ship_nonexistent_delivery_note_returns_404():
    resp = _client.post("/api/v1/sales/delivery-notes/does-not-exist/ship", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_deliver_nonexistent_delivery_note_returns_404():
    resp = _client.post("/api/v1/sales/delivery-notes/does-not-exist/deliver", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


# ===========================================================================
# SUSTAINABILITY — catalog/read-model now DB-backed
# ===========================================================================

def test_sustainability_catalog_returns_200():
    resp = _client.get("/api/v1/sustainability/catalog?tenant_id=test-tenant&jahr=2026", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_sustainability_read_model_returns_200():
    resp = _client.get("/api/v1/sustainability/read-model?tenant_id=test-tenant&jahr=2026", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_sustainability_reports_returns_200():
    resp = _client.get("/api/v1/sustainability/reports?tenant_id=test-tenant&jahr=2026", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200
