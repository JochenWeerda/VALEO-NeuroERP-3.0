"""
Tests for Liquidity Planning API.

Validates:
- /finance/liquidity/overview returns correct structure
- Pydantic schema enforces types
- _safe_float helper handles None/Decimal/float
- Forecast bucket generation logic
- Query parameter validation (tage_voraus bounds)
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from app.core.config import settings
from conftest import skip_if_db_unavailable


def _skip_if_table_missing(resp):
    skip_if_db_unavailable(resp)
    if resp.status_code == 500:
        body = resp.text
        if "UndefinedTable" in body or "does not exist" in body:
            pytest.skip("Required tables not yet migrated — run alembic upgrade head")


@pytest.fixture
def client():
    from main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def auth_header():
    token = settings.API_DEV_TOKEN or "dev-token"
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": "test-tenant"}


class TestSafeFloat:
    """Unit tests for _safe_float helper."""

    def test_none_returns_zero(self):
        from app.api.v1.endpoints.liquidity import _safe_float
        assert _safe_float(None) == 0.0

    def test_decimal_converts(self):
        from app.api.v1.endpoints.liquidity import _safe_float
        assert _safe_float(Decimal("123.45")) == 123.45

    def test_int_converts(self):
        from app.api.v1.endpoints.liquidity import _safe_float
        assert _safe_float(42) == 42.0

    def test_float_passthrough(self):
        from app.api.v1.endpoints.liquidity import _safe_float
        assert _safe_float(99.9) == 99.9

    def test_negative_decimal(self):
        from app.api.v1.endpoints.liquidity import _safe_float
        assert _safe_float(Decimal("-500.00")) == -500.0


class TestLiquiditySchemas:
    """Validate Pydantic schemas."""

    def test_liquidity_bucket_schema(self):
        from app.api.v1.endpoints.liquidity import LiquidityBucket
        b = LiquidityBucket(
            zeitraum="2026-04-01 – 2026-04-30",
            erwartete_eingaenge=10000.0,
            erwartete_ausgaenge=5000.0,
            netto=5000.0,
        )
        assert b.netto == 5000.0
        assert b.zeitraum == "2026-04-01 – 2026-04-30"

    def test_liquidity_overview_schema(self):
        from app.api.v1.endpoints.liquidity import LiquidityOverview
        o = LiquidityOverview(
            aktuell=100000.0,
            ziel=250000.0,
            forderungen_offen=50000.0,
            verbindlichkeiten_offen=30000.0,
            netto_working_capital=20000.0,
            prognose=[],
            stichtag="2026-04-10",
        )
        assert o.waehrung == "EUR"
        assert o.netto_working_capital == 20000.0

    def test_overview_nwc_calculation(self):
        from app.api.v1.endpoints.liquidity import LiquidityOverview
        o = LiquidityOverview(
            aktuell=0,
            ziel=0,
            forderungen_offen=75000.0,
            verbindlichkeiten_offen=50000.0,
            netto_working_capital=25000.0,
            prognose=[],
            stichtag="2026-04-10",
        )
        assert o.forderungen_offen - o.verbindlichkeiten_offen == o.netto_working_capital


class TestLiquidityEndpoint:
    """Integration test for the overview endpoint."""

    def test_overview_returns_structure(self, client, auth_header):
        resp = client.get("/api/v1/finance/liquidity/overview", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert "aktuell" in data
        assert "forderungen_offen" in data
        assert "verbindlichkeiten_offen" in data
        assert "netto_working_capital" in data
        assert "prognose" in data
        assert isinstance(data["prognose"], list)
        assert data["waehrung"] == "EUR"

    def test_overview_default_90_days(self, client, auth_header):
        resp = client.get("/api/v1/finance/liquidity/overview", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200
        buckets = resp.json()["prognose"]
        assert len(buckets) == 3  # 90 / 30 = 3

    def test_overview_custom_horizon(self, client, auth_header):
        resp = client.get("/api/v1/finance/liquidity/overview?tage_voraus=30", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200
        buckets = resp.json()["prognose"]
        assert len(buckets) == 1

    def test_overview_180_days(self, client, auth_header):
        resp = client.get("/api/v1/finance/liquidity/overview?tage_voraus=180", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200
        buckets = resp.json()["prognose"]
        assert len(buckets) == 6  # 180 / 30 = 6

    def test_overview_validation_min_days(self, client, auth_header):
        resp = client.get("/api/v1/finance/liquidity/overview?tage_voraus=3", headers=auth_header)
        assert resp.status_code == 422  # ge=7

    def test_overview_validation_max_days(self, client, auth_header):
        resp = client.get("/api/v1/finance/liquidity/overview?tage_voraus=500", headers=auth_header)
        assert resp.status_code == 422  # le=365
