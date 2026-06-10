"""Reine Logik-Tests des Beschaffungs-Abgleichs (DOM-PROC-004) — ohne DB.

Deckt den Mengen-Abgleich je Position ab: offen/teil/voll/überliefert + Abweichung.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.procurement_match_service import match_position

pytestmark = pytest.mark.unit


def test_offen_wenn_nichts_geliefert():
    m = match_position(Decimal("100"), Decimal("0"))
    assert m["status"] == "offen"
    assert m["offen"] == 100.0
    assert m["abweichung"] is False  # offen ist Lücke, aber keine Mengen-Abweichung


def test_vollstaendig_innerhalb_toleranz():
    m = match_position(Decimal("100"), Decimal("100"))
    assert m["status"] == "vollstaendig"
    assert m["abweichung"] is False
    assert m["offen"] == 0.0


def test_teilgeliefert():
    m = match_position(Decimal("100"), Decimal("60"))
    assert m["status"] == "teilgeliefert"
    assert m["abweichung"] is True
    assert m["offen"] == 40.0


def test_ueberliefert():
    m = match_position(Decimal("100"), Decimal("110"))
    assert m["status"] == "ueberliefert"
    assert m["abweichung"] is True
    assert m["abweichung_pct"] == 10.0
    assert m["offen"] == -10.0


def test_toleranz_grenze_zaehlt_als_vollstaendig():
    # 1 % Toleranz: 99–101 gilt als vollständig.
    assert match_position(Decimal("100"), Decimal("100.5"))["status"] == "vollstaendig"
    assert match_position(Decimal("100"), Decimal("99.5"))["status"] == "vollstaendig"


def test_ohne_menge():
    m = match_position(Decimal("0"), Decimal("0"))
    assert m["status"] == "ohne_menge"
    assert m["abweichung"] is False
