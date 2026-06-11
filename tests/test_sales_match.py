"""Reine Logik-Tests des Auftrag-↔-Lieferschein-Match (DOM-SALES-004.2)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.procurement_match_service import match_position
from app.services.sales_match_service import match_summary

pytestmark = pytest.mark.unit


def test_match_position_reuse_teilgeliefert():
    r = match_position(Decimal("5"), Decimal("3"))
    assert r["status"] == "teilgeliefert" and r["offen"] == 2.0 and r["abweichung"] is True


def test_match_position_vollstaendig_innerhalb_toleranz():
    assert match_position(Decimal("25"), Decimal("25"))["status"] == "vollstaendig"


def test_match_summary_mischfall():
    zeilen = [
        {"status": "vollstaendig", "abweichung": False},
        {"status": "teilgeliefert", "abweichung": True},
    ]
    s = match_summary(zeilen)
    assert s["positionen"] == 2
    assert s["vollstaendig_geliefert"] is False
    assert s["hat_abweichung"] is True
    assert s["offen_positionen"] == 1


def test_match_summary_alles_geliefert():
    zeilen = [
        {"status": "vollstaendig", "abweichung": False},
        {"status": "ueberliefert", "abweichung": True},
    ]
    s = match_summary(zeilen)
    assert s["vollstaendig_geliefert"] is True
    assert s["offen_positionen"] == 0


def test_match_summary_leer():
    s = match_summary([])
    assert s["positionen"] == 0 and s["vollstaendig_geliefert"] is False
