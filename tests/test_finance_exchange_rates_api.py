"""
COV-FIN-002: Tests for Exchange Rates API endpoints.

Covers /api/v1/finance/exchange-rates — CRUD, convert, latest.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


class TestExchangeRatesList:
    """GET /finance/exchange-rates"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/finance/exchange-rates", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestExchangeRateCRUD:
    """POST/GET/PUT /finance/exchange-rates"""

    def test_create_rate(self):
        payload = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.92,
            "rate_date": "2026-04-13",
            "rate_type": "spot",
            "source": "test",
            "active": True,
        }
        r = client.post("/api/v1/finance/exchange-rates", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code == 400:
            # Duplicate pair+date — acceptable on repeat
            return
        assert r.status_code == 201
        data = r.json()
        assert data["from_currency"] == "USD"
        assert data["rate"] == 0.92

    def test_create_missing_fields_422(self):
        r = client.post("/api/v1/finance/exchange-rates", headers=AUTH, json={})
        assert r.status_code == 422

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/finance/exchange-rates/NONEXISTENT-ID", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestExchangeRateConversion:
    """POST /finance/exchange-rates/convert"""

    def test_convert_returns_result(self):
        payload = {
            "amount": 100.0,
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate_type": "spot",
        }
        r = client.post("/api/v1/finance/exchange-rates/convert", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        # Either 200 with conversion or 404 if no rate exists
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            data = r.json()
            assert "converted_amount" in data
            assert "exchange_rate" in data

    def test_convert_missing_fields_422(self):
        r = client.post("/api/v1/finance/exchange-rates/convert", headers=AUTH, json={})
        assert r.status_code == 422


class TestExchangeRateLatest:
    """GET /finance/exchange-rates/latest/{from}/{to}"""

    def test_latest_nonexistent_pair_404(self):
        r = client.get("/api/v1/finance/exchange-rates/latest/XYZ/ABC", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404
