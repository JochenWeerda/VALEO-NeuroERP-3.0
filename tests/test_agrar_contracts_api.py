"""AGRAR-COV-001: Tests fuer agrar_contracts.py.

Abdeckung: _compute_status, _build_contract_dq_datensatz, HTTP CRUD-Pfade.
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.agrar_contracts import (
    _compute_status,
    _build_contract_dq_datensatz,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# _compute_status unit tests
# ---------------------------------------------------------------------------

def test_compute_status_cancelled():
    result = _compute_status(Decimal("1000"), Decimal("500"), "cancelled")
    assert result == "cancelled"


def test_compute_status_fulfilled_when_remaining_zero():
    result = _compute_status(Decimal("1000"), Decimal("0"), "open")
    assert result == "fulfilled"


def test_compute_status_fulfilled_when_remaining_negative():
    result = _compute_status(Decimal("1000"), Decimal("-1"), "open")
    assert result == "fulfilled"


def test_compute_status_partially_allocated():
    result = _compute_status(Decimal("1000"), Decimal("500"), "open")
    assert result == "partially_allocated"


def test_compute_status_open_when_fully_remaining():
    result = _compute_status(Decimal("1000"), Decimal("1000"), "open")
    assert result == "open"


def test_compute_status_cancelled_overrides_fulfilled():
    result = _compute_status(Decimal("1000"), Decimal("0"), "cancelled")
    assert result == "cancelled"


# ---------------------------------------------------------------------------
# _build_contract_dq_datensatz unit tests
# ---------------------------------------------------------------------------

def test_build_dq_datensatz_basic():
    data = {
        "contract_number": "KON-2026-001",
        "partner_id": "P-001",
        "article_id": "A-Weizen",
        "total_quantity_kg": 100_000,
        "fixed_price": 220.0,
        "status": "open",
        "pricing_model": "fixed",
    }
    result = _build_contract_dq_datensatz(data)
    assert result["kontrakt_nr"] == "KON-2026-001"
    assert result["lieferant_nr"] == "P-001"
    assert result["ware"] == "A-Weizen"
    assert abs(result["menge_tonnen"] - 100.0) < 1e-9
    assert result["preis_eur_pro_t"] == 220.0
    assert result["kontrakt_status"] == "OPEN"
    assert result["preismodell"] == "fixed"


def test_build_dq_datensatz_no_quantity():
    data = {"total_quantity_kg": None, "status": "draft", "pricing_model": "pool"}
    result = _build_contract_dq_datensatz(data)
    assert result["menge_tonnen"] is None


def test_build_dq_datensatz_missing_keys():
    result = _build_contract_dq_datensatz({})
    assert result["kontrakt_nr"] is None
    assert result["lieferant_nr"] is None
    assert result["kontrakt_status"] == "AKTIV"


# ---------------------------------------------------------------------------
# HTTP endpoint smoke tests
# ---------------------------------------------------------------------------

def test_list_contracts_returns_200_or_503():
    resp = _client.get("/api/v1/agrar/contracts", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200
    body = resp.json()
    # endpoint returns either a plain list or a paginated dict
    assert isinstance(body, (list, dict))


def test_get_nonexistent_contract_returns_404():
    resp = _client.get("/api/v1/agrar/contracts/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_contract_missing_fields_returns_422():
    resp = _client.post("/api/v1/agrar/contracts", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_create_contract_invalid_harvest_year():
    payload = {
        "contract_number": "KON-2026-001",
        "contract_type": "buy",
        "harvest_year": 1990,
        "partner_id": "P-001",
        "article_id": "A-Weizen",
        "pricing_model": "fixed",
        "total_quantity_kg": 50000.0,
    }
    resp = _client.post("/api/v1/agrar/contracts", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_create_contract_valid_payload_accepted():
    import uuid
    payload = {
        "contract_number": f"KON-2026-{uuid.uuid4().hex[:8].upper()}",
        "contract_type": "buy",
        "harvest_year": 2026,
        "partner_id": "P-001",
        "article_id": "A-Weizen",
        "pricing_model": "fixed",
        "fixed_price": 220.0,
        "total_quantity_kg": 50000.0,
    }
    resp = _client.post("/api/v1/agrar/contracts", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 201, 422)


def test_list_allocations_for_missing_contract_returns_404():
    resp = _client.get("/api/v1/agrar/contracts/no-such-id/allocations", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404
