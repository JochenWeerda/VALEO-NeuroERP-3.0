"""Reine Logik-Tests der Kontrakt-Fixierung & MATIF-Bewertung (DOM-CON-004.2)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.contract_fixing_service import (
    effektiv_preis,
    marktwert_offen,
    mtm_fixiert,
    restmenge,
)

pytestmark = pytest.mark.unit


def test_effektiv_preis_matif_plus_praemie():
    assert effektiv_preis(210, 12) == Decimal("222")
    assert effektiv_preis("205.5", "-3.5") == Decimal("202.0")


def test_restmenge_nie_negativ():
    assert restmenge(500, 300) == Decimal("200")
    assert restmenge(300, 300) == Decimal("0")
    assert restmenge(100, 140) == Decimal("0")  # Überfixierung wird auf 0 gekappt


def test_mtm_verkauf_ueber_markt_fixiert_ist_vorteil():
    # Verkauf: Ø-Fix effektiv 220,3333, Markt effektiv 220 → leicht über Markt → +Vorteil.
    r = mtm_fixiert(Decimal("220.3333"), Decimal("220"), Decimal("300"), einkauf=False)
    assert r == Decimal("99.99")


def test_mtm_einkauf_unter_markt_fixiert_ist_vorteil():
    # Einkauf: unter Markt fixiert (Fix 200, Markt 210) → Vorteil = (210-200)*100 = 1000.
    r = mtm_fixiert(Decimal("200"), Decimal("210"), Decimal("100"), einkauf=True)
    assert r == Decimal("1000.00")


def test_mtm_einkauf_ueber_markt_fixiert_ist_nachteil():
    # Einkauf: über Markt fixiert (Fix 215, Markt 210) → Nachteil = (210-215)*100 = -500.
    r = mtm_fixiert(Decimal("215"), Decimal("210"), Decimal("100"), einkauf=True)
    assert r == Decimal("-500.00")


def test_marktwert_offen():
    assert marktwert_offen(Decimal("200"), Decimal("220")) == Decimal("44000.00")
    assert marktwert_offen(0, Decimal("220")) == Decimal("0.00")
