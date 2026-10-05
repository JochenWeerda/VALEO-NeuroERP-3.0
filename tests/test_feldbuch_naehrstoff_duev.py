"""
AS-W1-Regression: Reinnaehrstoff- und Duengebilanz-Berechnung gegen DueV.

Prueft Reinnaehrstoffe (N/P2O5/K2O/MgO/S), org./mineralische Trennung, die
170-kg-N-Obergrenze fuer organische Duengung und die vereinfachte
N-Duengebedarfsermittlung.
"""
from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.agrar.feldbuch.naehrstoff import (  # noqa: E402
    Duengemassnahme,
    NaehrstoffGehalt,
    duengebedarf_n,
    duengebilanz,
    duev_n_org_check,
    reinnaehrstoffe_kg,
)


class TestReinnaehrstoffe:
    def test_kas_nitrogen(self):
        # Kalkammonsalpeter 27 % N, 350 kg/ha auf 10 ha -> 3500 kg Produkt -> 945 kg N
        rn = reinnaehrstoffe_kg(350.0, 10.0, NaehrstoffGehalt(n=27.0))
        assert rn["n"] == pytest.approx(945.0, abs=0.01)
        assert rn["p2o5"] == 0.0

    def test_npk_all_nutrients(self):
        # NPK 15-15-15, 300 kg/ha auf 5 ha -> 1500 kg Produkt -> je 225 kg N/P2O5/K2O
        rn = reinnaehrstoffe_kg(300.0, 5.0, NaehrstoffGehalt(n=15.0, p2o5=15.0, k2o=15.0))
        assert rn["n"] == pytest.approx(225.0, abs=0.01)
        assert rn["p2o5"] == pytest.approx(225.0, abs=0.01)
        assert rn["k2o"] == pytest.approx(225.0, abs=0.01)

    def test_zero_area_zero_nutrients(self):
        rn = reinnaehrstoffe_kg(300.0, 0.0, NaehrstoffGehalt(n=15.0))
        assert rn["n"] == 0.0


class TestDuengebilanz:
    def test_org_min_split_and_effective_n(self):
        massnahmen = [
            # Guelle (organisch): ~0,4 % N, 25 m3~=25000 kg/ha? Hier vereinfacht kg/ha.
            Duengemassnahme(menge_pro_ha=25000.0, flaeche_ha=1.0, gehalt=NaehrstoffGehalt(n=0.4, organisch=True), n_wirksamkeit=0.6),
            # KAS (mineralisch)
            Duengemassnahme(menge_pro_ha=200.0, flaeche_ha=1.0, gehalt=NaehrstoffGehalt(n=27.0)),
        ]
        b = duengebilanz(massnahmen)
        # org N = 25000*0,4/100 = 100; min N = 200*27/100 = 54
        assert b["n_organisch_kg"] == pytest.approx(100.0, abs=0.01)
        assert b["n_mineralisch_kg"] == pytest.approx(54.0, abs=0.01)
        # wirksam = 100*0,6 + 54*1,0 = 114
        assert b["n_wirksam_kg"] == pytest.approx(114.0, abs=0.01)
        assert b["reinnaehrstoffe_kg"]["n"] == pytest.approx(154.0, abs=0.01)


class TestDuevOrgLimit:
    def test_within_limit(self):
        r = duev_n_org_check(160.0, 1.0)
        assert r["ueberschritten"] is False
        assert r["grenzwert_kg_ha"] == 170.0

    def test_over_limit(self):
        r = duev_n_org_check(185.0, 1.0)
        assert r["ueberschritten"] is True
        assert r["auslastung_pct"] == pytest.approx(108.8, abs=0.1)

    def test_red_area_stricter_limit(self):
        # Rote Gebiete: strengerer Parameter (z. B. 130 kg/ha auf Betriebsebene)
        r = duev_n_org_check(150.0, 1.0, grenzwert_kg_ha=130.0)
        assert r["ueberschritten"] is True


class TestDuengebedarf:
    def test_basic_formula(self):
        # Sollwert 210, Nmin 45, +10 Zuschlag, -20 Abschlag -> 155
        assert duengebedarf_n(210.0, 45.0, zuschlaege_kg_ha=10.0, abschlaege_kg_ha=20.0) == pytest.approx(155.0)

    def test_not_negative(self):
        assert duengebedarf_n(100.0, 200.0) == 0.0
