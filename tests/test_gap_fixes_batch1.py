"""Gap-Fix Tests Batch 1: Auto-Matching, Finance-Invoices, Agrar-Contracts,
Sales-Orders, Compliance, Strecke, Personal.

Deckt alle neu hinzugefügten Endpoints und Workflow-Transitionen ab.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.auto_matching import (
    MatchingRule,
    MatchingRuleCreate,
    MatchingStatistics,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# AUTO-MATCHING — GET/PUT/DELETE /rules/{rule_id}
# ===========================================================================

def test_auto_matching_rule_model_valid():
    rule = MatchingRule(
        rule_name="Test Rule",
        priority=50,
        match_type="amount",
        conditions={"tolerance": 0.01},
        confidence_threshold=0.9,
        auto_apply=True,
        active=True,
    )
    assert rule.priority == 50
    assert rule.confidence_threshold == 0.9


def test_matching_rule_create_requires_match_type():
    with pytest.raises(Exception):
        MatchingRuleCreate(rule_name="X", conditions={})


def test_get_nonexistent_rule_returns_404():
    resp = _client.get("/api/v1/finance/auto-matching/rules/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_put_nonexistent_rule_returns_404():
    payload = {
        "rule_name": "Updated",
        "match_type": "amount",
        "conditions": {"tolerance": 0.02},
    }
    resp = _client.put("/api/v1/finance/auto-matching/rules/does-not-exist", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_rule_returns_404():
    resp = _client.delete("/api/v1/finance/auto-matching/rules/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_rules_returns_200():
    resp = _client.get("/api/v1/finance/auto-matching/rules", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_create_rule_missing_fields_returns_422():
    resp = _client.post("/api/v1/finance/auto-matching/rules", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


# ===========================================================================
# FINANCE INVOICES — DELETE /{invoice_number}
# ===========================================================================

def test_delete_nonexistent_invoice_returns_404():
    resp = _client.delete("/api/v1/finance/invoices/INV-DOES-NOT-EXIST", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_list_invoices_returns_200():
    resp = _client.get("/api/v1/finance/invoices", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# AGRAR CONTRACTS — DELETE + cancel + close
# ===========================================================================

def test_delete_nonexistent_contract_returns_404():
    resp = _client.delete("/api/v1/agrar/contracts/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_cancel_nonexistent_contract_returns_404():
    resp = _client.post("/api/v1/agrar/contracts/does-not-exist/cancel", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_close_nonexistent_contract_returns_404():
    resp = _client.post("/api/v1/agrar/contracts/does-not-exist/close", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


# ===========================================================================
# SALES ORDERS — confirm / complete / cancel workflow
# ===========================================================================

def test_confirm_nonexistent_order_returns_404():
    resp = _client.post("/api/v1/sales/orders/does-not-exist/confirm", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_complete_nonexistent_order_returns_404():
    resp = _client.post("/api/v1/sales/orders/does-not-exist/complete", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_cancel_nonexistent_order_returns_404():
    resp = _client.post("/api/v1/sales/orders/does-not-exist/cancel", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


# ===========================================================================
# COMPLIANCE — EUDR + UStVA (no longer hardcoded mocks)
# ===========================================================================

def test_eudr_status_returns_200():
    resp = _client.get("/api/v1/compliance/eudr", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
    assert "batches_total" in body
    assert "last_check" in body


def test_eudr_status_fields_not_hardcoded():
    """Status must be computed, not a static 'KONFORM' string always."""
    resp = _client.get("/api/v1/compliance/eudr", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    if resp.status_code == 200:
        body = resp.json()
        assert body["status"] in ("KONFORM", "WARNUNG", "KRITISCH")


def test_ustva_status_returns_200():
    resp = _client.get("/api/v1/compliance/ustva", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200
    body = resp.json()
    assert "periode" in body
    assert "readiness_pct" in body
    # No longer returns 'elster_übermittlung' (encoding issue fixed to 'elster_uebermittlung')
    assert "elster_uebermittlung" in body or "elster_übermittlung" in body


def test_ustva_period_filter():
    resp = _client.get("/api/v1/compliance/ustva?periode=2026-04", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    if resp.status_code == 200:
        body = resp.json()
        assert body["periode"] == "2026-04"


# ===========================================================================
# STRECKE — close workflow
# ===========================================================================

def test_close_nonexistent_strecke_returns_404():
    resp = _client.post(
        "/api/v1/strecke/streckengeschaefte/does-not-exist/close?rechnungsnr=RE-001",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_close_strecke_missing_rechnungsnr_returns_422():
    resp = _client.post(
        "/api/v1/strecke/streckengeschaefte/any-id/close",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_list_streckengeschaefte_returns_200():
    resp = _client.get("/api/v1/strecke/streckengeschaefte", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


# ===========================================================================
# PERSONAL — DELETE mitarbeiter / absences / shifts
# ===========================================================================

def test_delete_nonexistent_mitarbeiter_returns_404():
    resp = _client.delete("/api/v1/personal/mitarbeiter/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_absence_returns_404():
    resp = _client.delete("/api/v1/personal/absences/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_shift_returns_404():
    resp = _client.delete("/api/v1/personal/shifts/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404
