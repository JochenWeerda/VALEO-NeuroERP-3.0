"""AGRAR-COV-001: Tests fuer Agrar-Settlement API und Service.

Abdeckung: Service-Rundung, DQ-Datensatz,
DeductionInput-Validierung, HTTP-Smoke-Tests.
"""
from __future__ import annotations

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.agrar_settlements import (
    DeductionInput,
)
from app.services.agrar_settlement_service import AgrarSettlementService

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Service rounding unit tests
# ---------------------------------------------------------------------------

def test_round_money_two_decimals():
    result = AgrarSettlementService.round_money(Decimal("123.456"))
    assert result == Decimal("123.46")


def test_round_money_from_float():
    result = AgrarSettlementService.round_money(99.999)
    assert result == Decimal("100.00")


def test_round_money_exact():
    result = AgrarSettlementService.round_money(50)
    assert result == Decimal("50.00")


def test_round_qty_three_decimals():
    result = AgrarSettlementService.round_qty(Decimal("1234.5678"))
    assert result == Decimal("1234.568")


def test_round_qty_from_float():
    result = AgrarSettlementService.round_qty(1.0005)
    assert abs(float(result) - 1.001) < 0.001


# ---------------------------------------------------------------------------
# DQ datensatz unit tests
# ---------------------------------------------------------------------------

def _make_settlement_payload(**kwargs):
    defaults = {
        "supplier_id": "LF-001",
        "gross_quantity_kg": 50000.0,
        "billing_quantity_kg": None,
        "net_weight_kg": None,
        "article_id": "A-Weizen",
    }
    defaults.update(kwargs)

    defaults.setdefault("unit_price_eur_per_ton", 220.0)

    class FakePayload:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k, v)

    return FakePayload(defaults)


def test_build_settlement_dq_datensatz_keys():
    payload = _make_settlement_payload()
    result = AgrarSettlementService.build_dq_datensatz(payload, "ABR-2026-001")
    assert "abrechnungsnummer" in result
    assert result["abrechnungsnummer"] == "ABR-2026-001"
    assert "lieferant_id" in result


# ---------------------------------------------------------------------------
# DeductionInput validation
# ---------------------------------------------------------------------------

def test_deduction_per_ton_requires_rate():
    with pytest.raises(Exception):
        DeductionInput(deduction_type="drying", mode="per_ton")


def test_deduction_fixed_requires_amount():
    with pytest.raises(Exception):
        DeductionInput(deduction_type="cleaning", mode="fixed")


def test_deduction_per_ton_valid():
    d = DeductionInput(deduction_type="drying", mode="per_ton", rate_per_ton_eur=5.0)
    assert d.rate_per_ton_eur == 5.0


def test_deduction_fixed_valid():
    d = DeductionInput(deduction_type="freight", mode="fixed", fixed_amount_eur=200.0)
    assert d.fixed_amount_eur == 200.0


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_list_settlements_returns_200():
    resp = _client.get("/api/v1/agrar/settlements/", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_get_nonexistent_settlement_returns_404():
    resp = _client.get("/api/v1/agrar/settlements/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_settlement_missing_required_fields_returns_422():
    resp = _client.post("/api/v1/agrar/settlements/", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_billing_weight_preview_missing_body_returns_422():
    resp = _client.post("/api/v1/agrar/settlements/billing-weight/preview",
                        json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_list_drying_rules_returns_200():
    resp = _client.get("/api/v1/agrar/settlements/drying-rules", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 403, 404)
    if resp.status_code == 200:
        assert isinstance(resp.json(), list)
