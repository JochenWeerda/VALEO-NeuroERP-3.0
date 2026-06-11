"""Unit-Tests Rechnungsstufe des 3-Wege-Match (DOM-PROC-004.2)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.procurement_match_service import match_three_way_value

pytestmark = pytest.mark.unit


def test_three_way_abgeglichen_innerhalb_toleranz():
    m = match_three_way_value(Decimal("10000"), Decimal("10100"), Decimal("2"))
    assert m["status"] == "abgeglichen"
    assert m["abweichung"] is False


def test_three_way_wertabweichung():
    m = match_three_way_value(Decimal("10000"), Decimal("11000"), Decimal("2"))
    assert m["status"] == "wertabweichung"
    assert m["abweichung"] is True
    assert m["differenz"] == 1000.0


def test_three_way_rechnung_ohne_bezug():
    m = match_three_way_value(Decimal("0"), Decimal("500"))
    assert m["status"] == "rechnung_ohne_bezug"
    assert m["abweichung"] is True


def test_three_way_ohne_bezug_und_rechnung():
    m = match_three_way_value(Decimal("0"), Decimal("0"))
    assert m["status"] == "ohne_bezug"
    assert m["abweichung"] is False
