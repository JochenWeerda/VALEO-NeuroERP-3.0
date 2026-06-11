"""Reine Logik-Tests des Lieferungs-Storno-Guards (DOM-SALES-004.4)."""

from __future__ import annotations

import pytest

from app.services.sales_storno_service import can_storno

pytestmark = pytest.mark.unit


def test_storno_erlaubt_bei_offen():
    ok, msg = can_storno("geliefert", None)
    assert ok is True and msg == ""


def test_storno_blockiert_wenn_berechnet():
    ok, msg = can_storno("geliefert", "RE-001")
    assert ok is False and "Gutschrift" in msg


def test_storno_blockiert_wenn_bereits_storniert():
    ok, msg = can_storno("storniert", None)
    assert ok is False and "bereits storniert" in msg


def test_storno_status_case_insensitive():
    assert can_storno("STORNIERT", None)[0] is False
