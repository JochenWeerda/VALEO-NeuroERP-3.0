"""Reine Logik-Tests des Periodenabschlusses (DOM-FIN-004.4)."""

from __future__ import annotations

from datetime import date

import pytest

from app.services.finance_period_service import close_readiness, period_bounds

pytestmark = pytest.mark.unit


def test_period_bounds_monatsgrenzen():
    assert period_bounds("2026-06") == (date(2026, 6, 1), date(2026, 6, 30))
    assert period_bounds("2026-02") == (date(2026, 2, 1), date(2026, 2, 28))
    assert period_bounds("2026-12") == (date(2026, 12, 1), date(2026, 12, 31))


def test_readiness_clean():
    r = close_readiness(0, 0)
    assert r["ready"] is True and r["blocker"] == []


def test_readiness_offene_posten_blockieren():
    r = close_readiness(2, 0)
    assert r["ready"] is False and "2 offene Posten" in r["blocker"][0]


def test_readiness_storno_inkonsistenz_blockiert():
    r = close_readiness(0, 1)
    assert r["ready"] is False and "Storno-inkonsistente" in r["blocker"][0]


def test_readiness_mehrere_blocker():
    r = close_readiness(3, 2)
    assert r["ready"] is False and len(r["blocker"]) == 2
