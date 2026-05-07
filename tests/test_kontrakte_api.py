"""
DOMAIN-PARITY-COV-001 / COV-INT-002: Tests fuer Kontrakte-API.

Abdeckung: /api/v1/kontrakte — Kontrakt-Helpers, Serialisierung, Steuerungslogik,
HTTP-Pfade (list, get, status). Unit-Tests ohne DB via Mocks.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.kontrakte import (
    _num,
    _text,
    _bool,
    _string_list,
    _iso,
    _date,
    _line_to_out,
    _contract_reference_price,
)

_TENANT = "test-tenant"
_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": _TENANT}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Unit-Tests: Konverter-Helper
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("val,expected", [
    (None, None),
    ("", None),
    ("3.14", 3.14),
    (42, 42.0),
])
def test_num(val, expected):
    result = _num(val)
    if expected is None:
        assert result is None
    else:
        assert result == pytest.approx(expected)


def test_num_invalid_string_returns_none():
    assert _num("not-a-number") is None


@pytest.mark.parametrize("val,expected", [
    (None, None),
    ("  ", None),
    ("  Weizen  ", "Weizen"),
    ("", None),
])
def test_text(val, expected):
    assert _text(val) == expected


@pytest.mark.parametrize("val,expected", [
    (True, True),
    (False, False),
    ("true", True),
    ("ja", True),
    ("1", True),
    ("false", False),
    ("0", False),
    (0, False),
    (1, True),
])
def test_bool(val, expected):
    assert _bool(val) == expected


def test_string_list_from_list():
    assert _string_list(["a", "b", "", "c"]) == ["a", "b", "c"]


def test_string_list_from_csv():
    assert _string_list("a, b, c") == ["a", "b", "c"]


def test_string_list_empty():
    assert _string_list(None) == []


def test_iso_datetime():
    dt = datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc)
    assert _iso(dt).startswith("2026-05-07")


def test_iso_none():
    assert _iso(None) is None


def test_date_from_isostring():
    dt = _date("2026-05-07")
    assert dt is not None
    assert dt.year == 2026 and dt.month == 5 and dt.day == 7


def test_date_invalid_returns_none():
    assert _date("not-a-date") is None


# ---------------------------------------------------------------------------
# Unit-Tests: Line-Serialisierung
# ---------------------------------------------------------------------------


def _make_line(line_id="L-1", position_no=1, article_id="ART-001") -> MagicMock:
    line = MagicMock()
    line.line_id = line_id
    line.position_no = position_no
    line.article_id = article_id
    line.description1 = "Weizen"
    line.description2 = None
    line.qty_contract = Decimal("100.0")
    line.price_unit = "EUR/t"
    line.unit_price = Decimal("220.00")
    line.discount_pct = None
    line.surcharge = None
    line.rebate_type = None
    line.is_bio = False
    line.is_matif = False
    return line


def test_line_to_out_basic():
    line = _make_line()
    out = _line_to_out(line)
    assert out["article_id"] == "ART-001"
    assert out["qty_contract"] == pytest.approx(100.0)
    assert out["unit_price"] == pytest.approx(220.0)
    assert out["qty_remaining"] is None


def test_line_to_out_with_rest():
    line = _make_line()
    out = _line_to_out(line, rest=Decimal("40.0"))
    assert out["qty_remaining"] == pytest.approx(40.0)


# ---------------------------------------------------------------------------
# Unit-Tests: Referenzpreis
# ---------------------------------------------------------------------------


def test_contract_reference_price_uses_line_price():
    contract = MagicMock()
    contract.min_price = Decimal("180.0")
    assert _contract_reference_price(contract, 200.0) == pytest.approx(200.0)


def test_contract_reference_price_falls_back_to_min_price():
    contract = MagicMock()
    contract.min_price = Decimal("180.0")
    assert _contract_reference_price(contract, None) == pytest.approx(180.0)


def test_contract_reference_price_none_when_no_price():
    contract = MagicMock()
    contract.min_price = None
    assert _contract_reference_price(contract, None) is None


# ---------------------------------------------------------------------------
# HTTP Endpoint-Tests
# ---------------------------------------------------------------------------


def test_list_kontrakte_route_exists():
    # GET /kontrakte ist rollengeschuetzt (KONTRAKT_BEARBEITEN); dev-token hat keine Rollen.
    # 403 bestaetigt: Route vorhanden + Sicherheits-Gate aktiv.
    resp = _client.get("/api/v1/kontrakte", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 403)


def test_get_kontrakt_route_exists():
    # Einzelaufruf: 403 oder 404 bestaetigen beide, dass die Route registriert ist.
    resp = _client.get("/api/v1/kontrakte/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (403, 404)
