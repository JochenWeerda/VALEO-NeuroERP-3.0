"""
Tests for Futtermittel-Stammdaten & Rezepte API.

Covers Pydantic schema validation (no DB needed) and endpoint structure tests.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app
from app.api.v1.endpoints.futter_stamm import (
    EinzelfuttermittelIn,
    MischfuttermittelIn,
    RezeptKomponenteIn,
    RezeptIn,
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


# ── Einzelfuttermittel Schema Tests ───────────────────────────────


class TestEinzelfuttermittelSchemas:
    """Pydantic validation for EinzelfuttermittelIn."""

    def test_valid_minimal(self):
        e = EinzelfuttermittelIn(artikel_nummer="EF-001", name="Sojaschrot", art="Protein")
        assert e.artikel_nummer == "EF-001"
        assert e.name == "Sojaschrot"
        assert e.art == "Protein"
        assert e.qs_milch is False
        assert e.bio_zertifiziert is False
        assert e.verfuegbar_t == 0
        assert e.einheit == "t"

    def test_valid_full(self):
        e = EinzelfuttermittelIn(
            artikel_nummer="EF-002",
            name="Maissilage",
            art="Grundfutter",
            herkunft="Bayern",
            lieferant="Agrar GmbH",
            protein=8.5,
            energie=6.2,
            faser=22.0,
            fett=3.1,
            asche=5.0,
            trockensubstanz=35.0,
            gvo_status="GVO-frei",
            qs_milch=True,
            gmp_plus=True,
            bio_zertifiziert=True,
            verfuegbar_t=500.0,
            einheit="t",
            min_bestand_t=100.0,
            preis_pro_t=45.0,
        )
        assert e.protein == 8.5
        assert e.qs_milch is True

    def test_empty_artikel_nummer_rejected(self):
        with pytest.raises(ValidationError):
            EinzelfuttermittelIn(artikel_nummer="", name="Test", art="Test")

    def test_artikel_nummer_too_long_rejected(self):
        with pytest.raises(ValidationError):
            EinzelfuttermittelIn(artikel_nummer="x" * 51, name="Test", art="Test")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            EinzelfuttermittelIn(artikel_nummer="EF-001", name="", art="Test")

    def test_empty_art_rejected(self):
        with pytest.raises(ValidationError):
            EinzelfuttermittelIn(artikel_nummer="EF-001", name="Test", art="")

    def test_art_too_long_rejected(self):
        with pytest.raises(ValidationError):
            EinzelfuttermittelIn(artikel_nummer="EF-001", name="Test", art="a" * 101)

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            EinzelfuttermittelIn()


# ── Mischfuttermittel Schema Tests ────────────────────────────────


class TestMischfuttermittelSchemas:
    """Pydantic validation for MischfuttermittelIn."""

    def test_valid_minimal(self):
        m = MischfuttermittelIn(produkt_code="MF-001", name="Milchvieh Plus", tierart="Rind")
        assert m.produkt_code == "MF-001"
        assert m.tierart == "Rind"
        assert m.leistungsstufe is None

    def test_empty_produkt_code_rejected(self):
        with pytest.raises(ValidationError):
            MischfuttermittelIn(produkt_code="", name="Test", tierart="Rind")

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            MischfuttermittelIn(produkt_code="MF-001", name="", tierart="Rind")

    def test_empty_tierart_rejected(self):
        with pytest.raises(ValidationError):
            MischfuttermittelIn(produkt_code="MF-001", name="Test", tierart="")

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            MischfuttermittelIn()


# ── RezeptKomponente Schema Tests ─────────────────────────────────


class TestRezeptKomponenteSchemas:
    """Pydantic validation for RezeptKomponenteIn."""

    def test_valid(self):
        k = RezeptKomponenteIn(komponente_name="Sojaschrot", anteil=0.3)
        assert k.komponente_name == "Sojaschrot"
        assert k.anteil == 0.3
        assert k.sortierung == 0

    def test_anteil_zero_rejected(self):
        with pytest.raises(ValidationError):
            RezeptKomponenteIn(komponente_name="Test", anteil=0)

    def test_anteil_negative_rejected(self):
        with pytest.raises(ValidationError):
            RezeptKomponenteIn(komponente_name="Test", anteil=-0.1)

    def test_anteil_above_one_rejected(self):
        with pytest.raises(ValidationError):
            RezeptKomponenteIn(komponente_name="Test", anteil=1.1)

    def test_anteil_exactly_one_valid(self):
        k = RezeptKomponenteIn(komponente_name="Alleinfutter", anteil=1.0)
        assert k.anteil == 1.0

    def test_empty_komponente_name_rejected(self):
        with pytest.raises(ValidationError):
            RezeptKomponenteIn(komponente_name="", anteil=0.5)

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RezeptKomponenteIn()


# ── Rezept Schema Tests ───────────────────────────────────────────


class TestRezeptSchemas:
    """Pydantic validation for RezeptIn."""

    def test_valid_minimal(self):
        r = RezeptIn(rezept_code="RZ-001", name="Standardmischung", tierart="Rind")
        assert r.rezept_code == "RZ-001"
        assert r.komponenten == []

    def test_valid_with_komponenten(self):
        r = RezeptIn(
            rezept_code="RZ-002",
            name="Leistungsfutter",
            tierart="Schwein",
            komponenten=[
                RezeptKomponenteIn(komponente_name="Weizen", anteil=0.4),
                RezeptKomponenteIn(komponente_name="Sojaschrot", anteil=0.3),
            ],
        )
        assert len(r.komponenten) == 2

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RezeptIn()


# ── Endpoint Tests ────────────────────────────────────────────────


class TestFutterEndpoints:
    """HTTP endpoint tests for /api/v1/futter/*."""

    def test_list_einzelfuttermittel(self):
        resp = client.get("/api/v1/futter/einzelfuttermittel", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_mischfuttermittel(self):
        resp = client.get("/api/v1/futter/mischfuttermittel", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_rezepte(self):
        resp = client.get("/api/v1/futter/rezepte", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_einzelfuttermittel_missing_name_422(self):
        payload = {"artikel_nummer": "EF-999", "art": "Protein"}
        resp = client.post("/api/v1/futter/einzelfuttermittel", headers=AUTH, json=payload)
        assert resp.status_code == 422

    def test_create_einzelfuttermittel_empty_body_422(self):
        resp = client.post("/api/v1/futter/einzelfuttermittel", headers=AUTH, json={})
        assert resp.status_code == 422

    def test_create_mischfuttermittel_missing_fields_422(self):
        payload = {"name": "Test"}
        resp = client.post("/api/v1/futter/mischfuttermittel", headers=AUTH, json=payload)
        assert resp.status_code == 422

    def test_get_einzelfuttermittel_nonexistent_404(self):
        resp = client.get("/api/v1/futter/einzelfuttermittel/nonexistent-id", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404

    def test_get_mischfuttermittel_nonexistent_404(self):
        resp = client.get("/api/v1/futter/mischfuttermittel/nonexistent-id", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404

    def test_get_rezept_nonexistent_404(self):
        resp = client.get("/api/v1/futter/rezepte/nonexistent-id", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404

    def test_delete_einzelfuttermittel_nonexistent_404(self):
        resp = client.delete("/api/v1/futter/einzelfuttermittel/nonexistent-id", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 404
