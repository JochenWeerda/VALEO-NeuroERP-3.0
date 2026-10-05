"""
AS-W3-Regression: Naehrstoffvergleich / Stoffstrombilanz (DueV/StoffBilV).
Zufuhr (Duengung) vs. Abfuhr (Erntegut) -> N/P2O5-Saldo.
"""
from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.agrar.feldbuch.stoffstrombilanz import (  # noqa: E402
    SchlagStrom,
    naehrstoffabfuhr_kg,
    stoffstrombilanz,
)


class TestAbfuhr:
    def test_winterweizen(self):
        # 80 dt/ha * 10 ha = 800 dt; N 1,9 kg/dt -> 1520 kg N
        ab = naehrstoffabfuhr_kg("Winterweizen", 80.0, 10.0)
        assert ab["n"] == pytest.approx(1520.0, abs=0.1)
        assert ab["p2o5"] == pytest.approx(640.0, abs=0.1)

    def test_unknown_uses_default(self):
        ab = naehrstoffabfuhr_kg("Exotenkultur", 50.0, 1.0)
        assert ab["n"] == pytest.approx(50.0 * 1.7, abs=0.1)

    def test_zero_yield(self):
        assert naehrstoffabfuhr_kg("Winterweizen", 0.0, 10.0)["n"] == 0.0


class TestBilanz:
    def test_saldo(self):
        stroeme = [
            SchlagStrom(n_zufuhr_kg=1600.0, p2o5_zufuhr_kg=600.0,
                        kultur="Winterweizen", ertrag_dt_ha=80.0, flaeche_ha=10.0),
        ]
        b = stoffstrombilanz(stroeme)
        # N: 1600 - 1520 = +80; P2O5: 600 - 640 = -40
        assert b["n"]["saldo_kg"] == pytest.approx(80.0, abs=0.1)
        assert b["p2o5"]["saldo_kg"] == pytest.approx(-40.0, abs=0.1)

    def test_empty(self):
        b = stoffstrombilanz([])
        assert b["n"]["zufuhr_kg"] == 0.0
        assert b["n"]["abfuhr_kg"] == 0.0
