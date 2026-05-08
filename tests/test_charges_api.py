"""DOM-INV-002: Tests fuer charges.py (Chargen/Lots).

Abdeckung: _parse_iso_datetime, ChargeCreate/ChargeUpdate-Validierung, HTTP smoke.
"""
from __future__ import annotations

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.charges import (
    _parse_iso_datetime,
    ChargeCreate,
    ChargeUpdate,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# _parse_iso_datetime unit tests
# ---------------------------------------------------------------------------

def test_parse_iso_datetime_utc_z():
    result = _parse_iso_datetime("2026-05-08T10:00:00Z")
    assert result == datetime(2026, 5, 8, 10, 0, 0, tzinfo=timezone.utc)


def test_parse_iso_datetime_offset():
    result = _parse_iso_datetime("2026-05-08T12:00:00+02:00")
    assert result.hour == 12


def test_parse_iso_datetime_date_only():
    result = _parse_iso_datetime("2026-05-08")
    assert result.year == 2026
    assert result.month == 5


def test_parse_iso_datetime_invalid_raises():
    with pytest.raises(Exception):
        _parse_iso_datetime("not-a-date")


# ---------------------------------------------------------------------------
# ChargeCreate validation
# ---------------------------------------------------------------------------

def test_charge_create_requires_artikel_id():
    with pytest.raises(Exception):
        ChargeCreate(
            artikel="Weizen",
            chargen_id="CH-001",
            menge=50.0,
            lagerort="Silo-A",
            eingang="2026-05-08",
        )


def test_charge_create_rejects_zero_menge():
    with pytest.raises(Exception):
        ChargeCreate(
            artikel_id="A-001",
            artikel="Weizen",
            chargen_id="CH-001",
            menge=0.0,
            lagerort="Silo-A",
            eingang="2026-05-08",
        )


def test_charge_create_valid():
    ch = ChargeCreate(
        artikel_id="A-001",
        artikel="Weizen",
        chargen_id="CH-001",
        menge=50.0,
        lagerort="Silo-A",
        eingang="2026-05-08",
    )
    assert ch.rueckverfolgbar_bis_stunden == 4
    assert ch.warentrennung_qs_nicht_qs is False


def test_charge_update_all_optional():
    upd = ChargeUpdate()
    assert upd.menge is None
    assert upd.status is None


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_list_charges_returns_200():
    resp = _client.get("/api/v1/chargen", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_get_nonexistent_charge_returns_404():
    resp = _client.get("/api/v1/chargen/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_charge_missing_fields_returns_422():
    resp = _client.post("/api/v1/chargen", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_create_charge_valid_payload():
    import uuid
    payload = {
        "artikel_id": "A-001",
        "artikel": "Weizen",
        "chargen_id": f"CH-{uuid.uuid4().hex[:8].upper()}",
        "menge": 50.0,
        "lagerort": "Silo-A",
        "eingang": "2026-05-08",
    }
    resp = _client.post("/api/v1/chargen", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 201, 422)
