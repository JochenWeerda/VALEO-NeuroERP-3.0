"""
Tests for Disposition API — DB-backed CRUD endpoints.

Covers Pydantic schema validation (no DB needed) and endpoint structure tests.
The router prefix is /disposition, mounted at /api/v1.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app
from app.api.v1.endpoints.disposition import (
    DispositionPositionCreate,
    DispositionPositionUpdate,
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


class TestDispositionCreateSchema:
    """Pydantic validation for DispositionPositionCreate."""

    def test_valid_minimal(self):
        d = DispositionPositionCreate(artikel="Weizen", artikel_id="ART-001")
        assert d.artikel == "Weizen"
        assert d.artikel_id == "ART-001"
        assert d.bestand == 0
        assert d.mindestbestand == 0
        assert d.bedarf == 0
        assert d.prioritaet == "mittel"
        assert d.empfehlung is None

    def test_valid_full(self):
        d = DispositionPositionCreate(
            artikel="Raps Premium",
            artikel_id="ART-050",
            bestand=120.5,
            mindestbestand=200.0,
            bedarf=80.0,
            empfehlung="Nachbestellen: 100 t",
            prioritaet="hoch",
        )
        assert d.bestand == 120.5
        assert d.prioritaet == "hoch"
        assert d.empfehlung == "Nachbestellen: 100 t"

    def test_missing_artikel_rejected(self):
        with pytest.raises(ValidationError):
            DispositionPositionCreate(artikel_id="ART-001")

    def test_missing_artikel_id_rejected(self):
        with pytest.raises(ValidationError):
            DispositionPositionCreate(artikel="Weizen")

    def test_missing_both_required_rejected(self):
        with pytest.raises(ValidationError):
            DispositionPositionCreate()

    def test_defaults_bestand_zero(self):
        d = DispositionPositionCreate(artikel="Test", artikel_id="T-1")
        assert d.bestand == 0
        assert d.mindestbestand == 0
        assert d.bedarf == 0

    def test_defaults_prioritaet_mittel(self):
        d = DispositionPositionCreate(artikel="Test", artikel_id="T-1")
        assert d.prioritaet == "mittel"

    def test_custom_prioritaet(self):
        d = DispositionPositionCreate(
            artikel="Test", artikel_id="T-1", prioritaet="hoch"
        )
        assert d.prioritaet == "hoch"


class TestDispositionUpdateSchema:
    """Pydantic validation for DispositionPositionUpdate."""

    def test_all_optional(self):
        u = DispositionPositionUpdate()
        assert u.artikel is None
        assert u.artikel_id is None
        assert u.bestand is None
        assert u.mindestbestand is None
        assert u.bedarf is None
        assert u.empfehlung is None
        assert u.prioritaet is None

    def test_partial_update(self):
        u = DispositionPositionUpdate(bestand=500.0, prioritaet="niedrig")
        assert u.bestand == 500.0
        assert u.prioritaet == "niedrig"
        assert u.artikel is None

    def test_full_update(self):
        u = DispositionPositionUpdate(
            artikel="Neuer Weizen",
            artikel_id="ART-NEW",
            bestand=300,
            mindestbestand=100,
            bedarf=50,
            empfehlung="OK",
            prioritaet="niedrig",
        )
        assert u.artikel == "Neuer Weizen"


# ── Endpoint Tests ────────────────────────────────────────────────


class TestDispositionEndpoints:
    """HTTP endpoint tests for /api/v1/disposition."""

    def test_list_disposition_returns_dict(self):
        resp = client.get("/api/v1/disposition", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert "total" in data
        assert "sum_bedarf" in data
        assert "sum_bestand" in data

    def test_list_disposition_items_is_list(self):
        resp = client.get("/api/v1/disposition", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json()["items"], list)

    def test_list_disposition_filter_by_prioritaet(self):
        resp = client.get("/api/v1/disposition?prioritaet=hoch", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["prioritaet"] == "hoch"

    def test_stats_returns_dict(self):
        resp = client.get("/api/v1/disposition/stats", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "total_positionen" in data
        assert "nachbestellen_anzahl" in data
        assert "nach_kategorie" in data

    def test_stats_nach_kategorie_structure(self):
        resp = client.get("/api/v1/disposition/stats", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        kat = resp.json()["nach_kategorie"]
        assert "hoch" in kat
        assert "mittel" in kat
        assert "niedrig" in kat

    def test_create_position_missing_artikel_422(self):
        payload = {"artikel_id": "ART-999"}
        resp = client.post("/api/v1/disposition", headers=AUTH, json=payload)
        assert resp.status_code == 422

    def test_create_position_empty_body_422(self):
        resp = client.post("/api/v1/disposition", headers=AUTH, json={})
        assert resp.status_code == 422

    def test_create_position_valid(self):
        payload = {
            "artikel": "Testweizen",
            "artikel_id": "ART-TEST-001",
            "bestand": 50,
            "mindestbestand": 100,
            "bedarf": 50,
            "prioritaet": "hoch",
        }
        resp = client.post("/api/v1/disposition", headers=AUTH, json=payload)
        _skip_if_unavailable(resp)
        assert resp.status_code == 201
        data = resp.json()
        assert data["artikel"] == "Testweizen"
        assert data["artikel_id"] == "ART-TEST-001"

    def test_delete_nonexistent_returns_404(self):
        resp = client.delete("/api/v1/disposition/NONEXISTENT-ID-000", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404

    def test_put_nonexistent_returns_404(self):
        payload = {"bestand": 999}
        resp = client.put("/api/v1/disposition/NONEXISTENT-ID-000", headers=AUTH, json=payload)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404
