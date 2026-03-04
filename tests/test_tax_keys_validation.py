from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.tax_keys import TaxKeyCreate


def _base_payload():
    return {
        "code": "1",
        "bezeichnung": "USt 19%",
        "steuersatz": Decimal("19"),
        "ustva_position": "66",
        "ustva_bezeichnung": "Steuerpflichtige Umsätze 19%",
        "intracom": False,
        "export": False,
        "reverse_charge": False,
        "gueltig_von": date(2026, 1, 1),
        "gueltig_bis": None,
        "notizen": None,
        "debit_account": "1400",
        "credit_account": "1776",
        "country": "DE",
        "region": None,
        "active": True,
    }


@pytest.mark.unit
def test_tax_key_create_rejects_invalid_country():
    payload = _base_payload()
    payload["country"] = "DEU"
    with pytest.raises(ValidationError):
        TaxKeyCreate(**payload)


@pytest.mark.unit
def test_tax_key_create_rejects_invalid_validity_range():
    payload = _base_payload()
    payload["gueltig_bis"] = date(2025, 12, 31)
    with pytest.raises(ValidationError):
        TaxKeyCreate(**payload)


@pytest.mark.unit
def test_tax_key_create_rejects_reverse_charge_with_nonzero_rate():
    payload = _base_payload()
    payload["reverse_charge"] = True
    payload["steuersatz"] = Decimal("19")
    with pytest.raises(ValidationError):
        TaxKeyCreate(**payload)


@pytest.mark.unit
def test_tax_key_create_allows_reverse_charge_with_zero_rate():
    payload = _base_payload()
    payload["reverse_charge"] = True
    payload["steuersatz"] = Decimal("0")
    obj = TaxKeyCreate(**payload)
    assert obj.reverse_charge is True
    assert obj.steuersatz == Decimal("0")
