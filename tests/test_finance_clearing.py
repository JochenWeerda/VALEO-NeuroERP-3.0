"""Reine Logik-Tests der OP-Auszifferung (DOM-FIN-004.3)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.finance_clearing_service import clearing_result

pytestmark = pytest.mark.unit


def test_teilausgleich():
    r = clearing_result(Decimal("5000"), 2000)
    assert r["neu_offen"] == 3000.0 and r["voll_ausgeziffert"] is False and r["ueberzahlt"] is False


def test_vollausgleich_mit_skonto():
    r = clearing_result(Decimal("3000"), 2900, skonto_betrag=100)
    assert r["ausgleich"] == 3000.0 and r["neu_offen"] == 0.0 and r["voll_ausgeziffert"] is True


def test_exakter_ausgleich():
    r = clearing_result(Decimal("800"), 800)
    assert r["voll_ausgeziffert"] is True and r["neu_offen"] == 0.0


def test_ueberzahlung_erkannt():
    r = clearing_result(Decimal("100"), 150)
    assert r["ueberzahlt"] is True


def test_neu_offen_nie_negativ():
    r = clearing_result(Decimal("100"), 100)
    assert r["neu_offen"] == 0.0
