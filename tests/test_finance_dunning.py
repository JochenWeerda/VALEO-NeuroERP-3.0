"""Reine Logik-Tests des Mahnlaufs (DOM-FIN-004.2)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.finance_dunning_service import (
    _DEFAULT_RULES,
    compute_dunning,
    days_based_level,
    next_dunning_level,
)

pytestmark = pytest.mark.unit


def test_days_based_level():
    assert days_based_level(0) == 0
    assert days_based_level(15) == 1
    assert days_based_level(45) == 2
    assert days_based_level(76) == 3


def test_next_dunning_level_eskaliert():
    # Stufe 1, 15 Tage → 2; Stufe 2, 76 Tage → 3; gedeckelt bei 3.
    assert next_dunning_level(1, 15) == 2
    assert next_dunning_level(2, 76) == 3
    assert next_dunning_level(3, 90) == 3
    assert next_dunning_level(0, 0) == 0


def test_next_dunning_level_springt_nach_ueberfaelligkeit():
    # Noch nicht gemahnt (0), aber 76 Tage überfällig → mind. Stufe 3.
    assert next_dunning_level(0, 76) == 3


def test_compute_dunning_zins_anteilig():
    # 800 € @ Stufe 3 (8 % p.a.), 76 Tage → Zins 800*0.08*76/365 = 13,33.
    r = compute_dunning(Decimal("800"), 3, _DEFAULT_RULES[3], 76)
    assert r["dunning_fee"] == 20.0
    assert r["interest"] == 13.33
    assert r["total_amount"] == 833.33


def test_compute_dunning_stufe1_ohne_zins():
    r = compute_dunning(Decimal("5000"), 1, _DEFAULT_RULES[1], 15)
    assert r["dunning_fee"] == 5.0 and r["interest"] == 0.0 and r["total_amount"] == 5005.0
