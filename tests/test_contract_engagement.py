"""Reine Logik-Tests der Kontrakt-Engagement-Aggregation (DOM-CON-004.3)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.contract_engagement_service import (
    naechste_mahnstufe,
    netto_position,
    offen_menge,
)

pytestmark = pytest.mark.unit


def test_offen_menge_nie_negativ():
    assert offen_menge(200, 120) == Decimal("80")
    assert offen_menge(50, 50) == Decimal("0")
    assert offen_menge(50, 70) == Decimal("0")  # Übererfüllung kappt auf 0


def test_netto_position_einkauf_minus_verkauf():
    assert netto_position(80, 0) == Decimal("80")
    assert netto_position(0, 500) == Decimal("-500")
    assert netto_position(120, 60) == Decimal("60")


def test_naechste_mahnstufe_eskaliert():
    assert naechste_mahnstufe(None) == 1
    assert naechste_mahnstufe(0) == 1
    assert naechste_mahnstufe(1) == 2
    assert naechste_mahnstufe(3) == 4
