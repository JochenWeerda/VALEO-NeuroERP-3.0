"""
Tests for inventory operations — Bestandskorrektur, Schwund, MHD-Abschreibung.

Covers:
- REASON_CODES and DEFAULT_ACCOUNTS constants
- Pydantic schema validation (BestandskorrekturIn, SchwundBuchungIn, MhdAbschreibungIn)
- Endpoint structure (GET reason-codes, POST bestandskorrektur/schwund/mhd-abschreibung, GET korrekturen)
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from main import app
from app.api.v1.endpoints.inventory_operations import (
    REASON_CODES,
    DEFAULT_ACCOUNTS,
    BestandskorrekturIn,
    BestandskorrekturOut,
    SchwundBuchungIn,
    MhdAbschreibungIn,
)

client = TestClient(app, raise_server_exceptions=False)
AUTH = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "test-tenant",
}


def _skip_if_unavailable(resp):
    if resp.status_code in (500, 503):
        body = resp.text
        if any(k in body for k in ("OperationalError", "Connection refused", "UndefinedTable", "does not exist")):
            pytest.skip("DB or tables not available")


# ── Constants ────────────────────────────────────────────────────


class TestReasonCodes:
    """Verify the REASON_CODES dictionary."""

    def test_reason_codes_has_all_required_keys(self):
        expected = {"schwund", "bruch", "mhd_verfall", "diebstahl", "messdifferenz", "qualitaetsmangel", "sonstige"}
        assert expected == set(REASON_CODES.keys())

    def test_reason_codes_values_are_strings(self):
        for code, label in REASON_CODES.items():
            assert isinstance(label, str), f"REASON_CODES[{code!r}] should be str"
            assert len(label) > 0

    def test_reason_codes_count(self):
        assert len(REASON_CODES) == 7


class TestDefaultAccounts:
    """Verify SKR03 default account mappings."""

    def test_bestandskonto(self):
        assert DEFAULT_ACCOUNTS["bestandskonto"] == "1500"

    def test_gegenkonto_zugang(self):
        assert DEFAULT_ACCOUNTS["gegenkonto_zugang"] == "3200"

    def test_gegenkonto_abgang(self):
        assert DEFAULT_ACCOUNTS["gegenkonto_abgang"] == "3800"

    def test_schwund_konto(self):
        assert DEFAULT_ACCOUNTS["schwund_konto"] == "5810"

    def test_bestandsveraenderung_present(self):
        assert DEFAULT_ACCOUNTS["bestandsveraenderung"] == "5800"


# ── Schema validation ───────────────────────────────────────────


class TestBestandskorrekturInSchema:
    """Pydantic validation for BestandskorrekturIn."""

    def test_valid_minimal(self):
        obj = BestandskorrekturIn(
            article_id="ART-001",
            warehouse_id="WH-001",
            menge=-5.0,
            grund="schwund",
        )
        assert obj.article_id == "ART-001"
        assert obj.menge == -5.0
        assert obj.bemerkung is None
        assert obj.buchungsdatum is None

    def test_valid_full(self):
        obj = BestandskorrekturIn(
            article_id="ART-002",
            warehouse_id="WH-002",
            menge=10.0,
            grund="bruch",
            bemerkung="Palette umgefallen",
            charge="CH-2026-01",
            buchungsdatum=date(2026, 4, 1),
        )
        assert obj.bemerkung == "Palette umgefallen"
        assert obj.buchungsdatum == date(2026, 4, 1)

    def test_missing_article_id(self):
        with pytest.raises(ValidationError):
            BestandskorrekturIn(warehouse_id="WH-001", menge=1.0, grund="sonstige")

    def test_missing_warehouse_id(self):
        with pytest.raises(ValidationError):
            BestandskorrekturIn(article_id="ART-001", menge=1.0, grund="sonstige")

    def test_missing_menge(self):
        with pytest.raises(ValidationError):
            BestandskorrekturIn(article_id="ART-001", warehouse_id="WH-001", grund="sonstige")

    def test_missing_grund(self):
        with pytest.raises(ValidationError):
            BestandskorrekturIn(article_id="ART-001", warehouse_id="WH-001", menge=1.0)


class TestSchwundBuchungInSchema:
    """Pydantic validation for SchwundBuchungIn."""

    def test_valid(self):
        obj = SchwundBuchungIn(article_id="ART-001", warehouse_id="WH-001", menge=3.5)
        assert obj.menge == 3.5

    def test_menge_must_be_positive(self):
        with pytest.raises(ValidationError, match="greater than"):
            SchwundBuchungIn(article_id="ART-001", warehouse_id="WH-001", menge=0)

    def test_negative_menge_rejected(self):
        with pytest.raises(ValidationError):
            SchwundBuchungIn(article_id="ART-001", warehouse_id="WH-001", menge=-1.0)

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            SchwundBuchungIn(menge=5.0)


class TestMhdAbschreibungInSchema:
    """Pydantic validation for MhdAbschreibungIn."""

    def test_valid(self):
        obj = MhdAbschreibungIn(
            article_id="ART-001",
            warehouse_id="WH-001",
            menge=10.0,
            charge="CH-001",
            mhd=date(2026, 3, 31),
        )
        assert obj.charge == "CH-001"
        assert obj.mhd == date(2026, 3, 31)

    def test_menge_must_be_positive(self):
        with pytest.raises(ValidationError, match="greater than"):
            MhdAbschreibungIn(
                article_id="ART-001", warehouse_id="WH-001",
                menge=0, charge="CH-001", mhd=date(2026, 1, 1),
            )

    def test_missing_charge(self):
        with pytest.raises(ValidationError):
            MhdAbschreibungIn(
                article_id="ART-001", warehouse_id="WH-001",
                menge=5.0, mhd=date(2026, 1, 1),
            )

    def test_missing_mhd(self):
        with pytest.raises(ValidationError):
            MhdAbschreibungIn(
                article_id="ART-001", warehouse_id="WH-001",
                menge=5.0, charge="CH-001",
            )


# ── Endpoint tests ──────────────────────────────────────────────


class TestReasonCodesEndpoint:
    """GET /api/v1/lager/reason-codes."""

    def test_returns_list(self):
        resp = client.get("/api/v1/lager/reason-codes", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        codes = {item["code"] for item in body}
        assert "schwund" in codes
        assert "mhd_verfall" in codes
        assert len(body) == 7


class TestBestandskorrekturEndpoint:
    """POST /api/v1/lager/bestandskorrektur."""

    def test_422_on_missing_fields(self):
        resp = client.post(
            "/api/v1/lager/bestandskorrektur",
            json={},
            headers=AUTH,
        )
        assert resp.status_code == 422

    def test_422_on_partial_payload(self):
        resp = client.post(
            "/api/v1/lager/bestandskorrektur",
            json={"article_id": "ART-001"},
            headers=AUTH,
        )
        assert resp.status_code == 422


class TestSchwundEndpoint:
    """POST /api/v1/lager/schwund."""

    def test_422_on_empty_body(self):
        resp = client.post(
            "/api/v1/lager/schwund",
            json={},
            headers=AUTH,
        )
        assert resp.status_code == 422

    def test_422_on_zero_menge(self):
        resp = client.post(
            "/api/v1/lager/schwund",
            json={"article_id": "ART-001", "warehouse_id": "WH-001", "menge": 0},
            headers=AUTH,
        )
        assert resp.status_code == 422


class TestMhdAbschreibungEndpoint:
    """POST /api/v1/lager/mhd-abschreibung."""

    def test_422_on_empty_body(self):
        resp = client.post(
            "/api/v1/lager/mhd-abschreibung",
            json={},
            headers=AUTH,
        )
        assert resp.status_code == 422


class TestKorrekturenEndpoint:
    """GET /api/v1/lager/korrekturen."""

    def test_returns_paginated(self):
        resp = client.get("/api/v1/lager/korrekturen", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert isinstance(body["items"], list)
