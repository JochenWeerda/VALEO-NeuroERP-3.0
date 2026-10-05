"""
F2-Regression: Effizienz-Kennzahlen des Rations-Optimizers gegen DLG 01|2025 (Kap. 10).

Prueft die reine Helper-Funktion `_efficiency_metrics` gegen das im DLG-Merkblatt
angefuehrte Rechenbeispiel (700 kg, 23 kg TM, 32 kg ECM, 237 MJ ME).
"""
from __future__ import annotations

import os
import sys

import pytest

_RATIONS_ROOT = os.path.join(os.path.dirname(__file__), "..", "rationsoptimierung")
if _RATIONS_ROOT not in sys.path:
    sys.path.insert(0, _RATIONS_ROOT)

from app.api.v1.endpoints.rations_optimization import _efficiency_metrics  # noqa: E402


def _dlg_example():
    # DLG 01|2025, Kap. 10: 700 kg, 23 kg TM, 32 kg ECM, ME-Aufnahme 237 MJ (10,3 MJ/kg)
    milk_kg, protein_pct = 32.0, 3.4
    return _efficiency_metrics(
        ecm_kg_day=32.0,
        dmi_kg=23.0,
        me_mj=237.0,
        milk_protein_g=milk_kg * protein_pct / 100.0 * 1000.0,
        cp_intake_g=3800.0,
        body_weight_kg=700.0,
    )


class TestEfficiencyDlg2025Example:
    def test_feed_efficiency(self):
        # kg ECM / kg TM = 32/23 ~ 1,39 (DLG rundet auf 1,4)
        assert _dlg_example()["feed_efficiency_kg_ecm_per_kg_dm"] == pytest.approx(1.391, abs=1e-3)

    def test_energy_efficiency_mj_per_mj(self):
        # ECM*3,15 / ME = 100,8/237 ~ 0,425 (DLG 0,426)
        assert _dlg_example()["energy_efficiency_mj_per_mj"] == pytest.approx(0.425, abs=2e-3)

    def test_energy_efficiency_kg_ecm_per_10mj(self):
        # kg ECM / 10 MJ ME = 32/23,7 = 1,35
        assert _dlg_example()["energy_efficiency_kg_ecm_per_10mj"] == pytest.approx(1.35, abs=1e-3)

    def test_bodymass_efficiency(self):
        assert _dlg_example()["bodymass_efficiency_kg_ecm_per_kg"] == pytest.approx(32.0 / 700.0, abs=1e-4)


class TestEfficiencyEdgeCases:
    def test_zero_inputs_yield_none(self):
        e = _efficiency_metrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        assert e["feed_efficiency_kg_ecm_per_kg_dm"] is None
        assert e["energy_efficiency_mj_per_mj"] is None
        assert e["protein_efficiency_pct"] is None

    def test_protein_efficiency_percentage(self):
        # 1000 g Milchprotein / 3000 g CP = 33,3 %
        e = _efficiency_metrics(30.0, 20.0, 200.0, 1000.0, 3000.0, 650.0)
        assert e["protein_efficiency_pct"] == pytest.approx(33.3, abs=0.1)
