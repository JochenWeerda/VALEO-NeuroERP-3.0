from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.finance.tax_resolver import resolve_partner_country, resolve_tax_key_accounts


class _FakeResult:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


class _FakeSession:
    def __init__(self, callback):
        self._callback = callback

    def execute(self, statement, params=None):
        row = self._callback(str(statement), params or {})
        return _FakeResult(row)


@pytest.mark.unit
def test_resolve_partner_country_returns_default_for_missing_partner():
    db = _FakeSession(lambda _sql, _params: None)
    assert resolve_partner_country(db, None, default="DE") == "DE"


@pytest.mark.unit
def test_resolve_partner_country_normalizes_iso_code():
    db = _FakeSession(lambda _sql, _params: ("fr",))
    assert resolve_partner_country(db, "P-1", default="DE") == "FR"


@pytest.mark.unit
def test_resolve_tax_key_accounts_uses_country_then_de_fallback():
    def callback(_sql, params):
        if params.get("country") == "FR":
            return None
        if params.get("country") == "DE":
            return ("01", "1576", "1776", False, False, False, "DE")
        return None

    db = _FakeSession(callback)
    result = resolve_tax_key_accounts(db, tenant_id="system", rate=Decimal("19"), country="FR")

    assert result["country"] == "DE"
    assert result["debit_account"] == "1576"
    assert result["credit_account"] == "1776"
    assert result["reverse_charge"] is False


@pytest.mark.unit
def test_resolve_tax_key_accounts_returns_context_when_no_key_found():
    db = _FakeSession(lambda _sql, _params: None)

    # CH is non-EU -> export=True
    result = resolve_tax_key_accounts(
        db,
        tenant_id="system",
        rate=Decimal("0"),
        country="CH",
        as_of=date(2026, 3, 4),
    )

    assert result["code"] is None
    assert result["debit_account"] is None
    assert result["credit_account"] is None
    assert result["export"] is True
    assert result["intracom"] is False
