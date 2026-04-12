"""
Tests for Agrar Sorten/Varieties API.

Covers Pydantic schema validation (no DB needed) and endpoint structure tests.
The endpoint is mounted at /api/v1/agrar/varieties.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app
from app.api.v1.endpoints.agrar_varieties import (
    VarietyIn,
    VarietyOut,
    _STANDARD_SEED,
)

client = TestClient(app, raise_server_exceptions=False)
AUTH = {
    "Authorization": f"Bearer {settings.API_DEV_TOKEN or 'dev-token'}",
    "X-Tenant-ID": "test-tenant",
}


def _skip_if_unavailable(resp):
    if resp.status_code in (500, 503):
        body = resp.text
        if any(k in body for k in ("OperationalError", "Connection refused", "UndefinedTable", "does not exist")):
            pytest.skip("DB or tables not available")


# ── Schema Tests ──────────────────────────────────────────────────


class TestVarietySchemas:
    """Pydantic validation for VarietyIn / VarietyOut."""

    def test_valid_minimal(self):
        v = VarietyIn(variety_number="100", name="Mais")
        assert v.variety_number == "100"
        assert v.name == "Mais"
        assert v.description is None
        assert v.crop_type is None
        assert v.zuechter is None

    def test_valid_full(self):
        v = VarietyIn(
            variety_number="245",
            name="Weizen Elite",
            description="Hochleistungsweizen",
            crop_type="WHEAT",
            zuechter="Saatzucht GmbH",
            zulassungsjahr=2024,
            reifezahl="S240",
            qualitaetsgruppe="E",
        )
        assert v.zuechter == "Saatzucht GmbH"
        assert v.zulassungsjahr == 2024
        assert v.qualitaetsgruppe == "E"

    def test_empty_variety_number_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="", name="Test")

    def test_variety_number_too_long_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="x" * 21, name="Test")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="100", name="")

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="100", name="n" * 256)

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            VarietyIn()

    def test_missing_variety_number(self):
        with pytest.raises(ValidationError):
            VarietyIn(name="Weizen")

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            VarietyIn(variety_number="100")

    def test_variety_out_requires_id(self):
        with pytest.raises(ValidationError):
            VarietyOut(variety_number="100", name="Mais")

    def test_variety_out_valid(self):
        v = VarietyOut(id="abc-123", variety_number="100", name="Mais")
        assert v.id == "abc-123"
        assert v.aktiv is True


# ── Seed Data Tests ───────────────────────────────────────────────


class TestSeedData:
    """Verify the standard seed data structure."""

    def test_seed_has_five_entries(self):
        assert len(_STANDARD_SEED) == 5

    def test_seed_entries_have_required_keys(self):
        for seed in _STANDARD_SEED:
            assert "variety_number" in seed
            assert "name" in seed
            assert "crop_type" in seed

    def test_seed_variety_numbers_unique(self):
        numbers = [s["variety_number"] for s in _STANDARD_SEED]
        assert len(numbers) == len(set(numbers))

    def test_seed_crop_types_valid(self):
        valid_types = {"WHEAT", "MAIZE", "BARLEY", "OATS", "RAPESEED"}
        for seed in _STANDARD_SEED:
            assert seed["crop_type"] in valid_types


# ── Endpoint Tests ────────────────────────────────────────────────


class TestVarietyEndpoints:
    """HTTP endpoint tests for /api/v1/agrar/varieties."""

    def test_list_varieties_returns_list(self):
        resp = client.get("/api/v1/agrar/varieties/", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_varieties_auto_seed(self):
        """First call should auto-seed standard varieties."""
        resp = client.get("/api/v1/agrar/varieties/", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        # Should have at least the 5 seeded varieties
        assert len(data) >= 5

    def test_list_varieties_filter_by_crop_type(self):
        resp = client.get("/api/v1/agrar/varieties/?crop_type=WHEAT", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        for item in data:
            assert item.get("crop_type") == "WHEAT"

    def test_post_variety_empty_body_422(self):
        resp = client.post("/api/v1/agrar/varieties/", headers=AUTH, json={})
        assert resp.status_code == 422

    def test_post_variety_missing_name_422(self):
        resp = client.post(
            "/api/v1/agrar/varieties/",
            headers=AUTH,
            json={"variety_number": "999"},
        )
        assert resp.status_code == 422

    def test_get_variety_nonexistent_404(self):
        resp = client.get("/api/v1/agrar/varieties/nonexistent-id", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404

    def test_delete_variety_nonexistent_404(self):
        resp = client.delete("/api/v1/agrar/varieties/nonexistent-id", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404
