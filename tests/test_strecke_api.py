"""
DOMAIN-PARITY-COV-001 / COV-INT-002: Tests fuer Strecke-API.

Abdeckung: /api/v1/strecke/streckengeschaefte — CRUD, Validierung, Nummernvergabe,
semantische Status-Pfade. Unit-Tests ohne DB via SQLAlchemy-Session-Mock.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.strecke import (
    _parse_datum,
    _next_strecke_nr,
    _to_out,
    _numeric_advisory_key,
    StreckengeschaeftCreate,
)

_TENANT = "test-tenant"
_NOW = datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc)
_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": _TENANT}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helper-Unit-Tests (kein HTTP, kein DB)
# ---------------------------------------------------------------------------


def test_parse_datum_valid():
    d = _parse_datum("2026-05-07")
    assert d == date(2026, 5, 7)


def test_parse_datum_truncates_to_date():
    d = _parse_datum("2026-05-07T10:00:00")
    assert d == date(2026, 5, 7)


def test_parse_datum_invalid_raises_http_400():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        _parse_datum("not-a-date")
    assert exc.value.status_code == 400


def test_numeric_advisory_key_stable():
    k1 = _numeric_advisory_key("tenant-a", 2026)
    k2 = _numeric_advisory_key("tenant-a", 2026)
    assert k1 == k2


def test_numeric_advisory_key_different_tenants():
    k1 = _numeric_advisory_key("tenant-a", 2026)
    k2 = _numeric_advisory_key("tenant-b", 2026)
    assert k1 != k2


def test_numeric_advisory_key_range():
    k = _numeric_advisory_key("any-tenant", 2026)
    assert 1 <= k <= 0x7FFF_FFFF


def _make_row(
    sid: str = "sg-001",
    strecke_nr: str = "STR-2026-0001",
    erledigt: bool = False,
) -> MagicMock:
    row = MagicMock()
    row.id = sid
    row.strecke_nr = strecke_nr
    row.datum = date(2026, 5, 7)
    row.niederlassung = "Hamburg"
    row.partie_nr = "P-001"
    row.kostenstelle = "K-01"
    row.lagerhalle = "LH-A"
    row.nls_nr = ""
    row.erledigt = erledigt
    row.lieferant_name = "Maier GmbH"
    row.lieferant_nr = "L-100"
    row.kontrakt_nr = "KON-001"
    row.artikel = "Weizen"
    row.netto = Decimal("1000.00")
    row.mwst = Decimal("70.00")
    row.brutto = Decimal("1070.00")
    row.rechnungsnr = "RE-001"
    row.bediener = "Tester"
    row.notiz = ""
    row.erstellt = _NOW
    return row


def test_to_out_serializes_correctly():
    row = _make_row()
    out = _to_out(row)
    assert out.id == "sg-001"
    assert out.strecke_nr == "STR-2026-0001"
    assert out.netto == pytest.approx(1000.0)
    assert out.erledigt is False


def test_next_strecke_nr_first_of_year():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    nr = _next_strecke_nr(db, _TENANT, fiscal_year=2026)
    assert nr == "STR-2026-0001"


def test_next_strecke_nr_increments():
    db = MagicMock()
    # _next_strecke_nr tut: for (nr,) in rows -> rows muessen Einzel-Tupel sein
    db.query.return_value.filter.return_value.all.return_value = [("STR-2026-0005",)]
    nr = _next_strecke_nr(db, _TENANT, fiscal_year=2026)
    assert nr == "STR-2026-0006"


# ---------------------------------------------------------------------------
# HTTP Endpoint-Tests (TestClient, DB via Mock/Skip)
# ---------------------------------------------------------------------------


def test_list_returns_200():
    resp = _client.get("/api/v1/strecke/streckengeschaefte", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_nonexistent_returns_404():
    resp = _client.get("/api/v1/strecke/streckengeschaefte/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_with_invalid_date_returns_400():
    payload = {
        "datum": "not-a-date",
        "niederlassung": "Hamburg",
        "artikel": "Weizen",
        "netto": 1000.0,
    }
    resp = _client.post("/api/v1/strecke/streckengeschaefte", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (400, 422)
