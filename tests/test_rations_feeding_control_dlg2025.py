"""
F1-Regression: Fuetterungscontrolling-Kennzahlen gegen DLG 01|2025 (Kap. 11 + 12).

Prueft TM-Verzehr/Kuh, Mischgenauigkeit (Toleranz < 5 %) und IOFC.
"""
from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.agrar.rations.control.feeding_control import (  # noqa: E402
    LoadedComponent,
    compute_feeding_control,
    tm_verzehr_je_kuh,
)


class TestTmVerzehr:
    def test_dlg_formula(self):
        # (vorgelegt 1200 - Restfutter 60) * 40% / 58 Kuehe
        v = tm_verzehr_je_kuh(1200.0, 60.0, 40.0, 58)
        assert v == pytest.approx((1200 - 60) * 0.40 / 58, abs=1e-2)

    def test_zero_animals_none(self):
        assert tm_verzehr_je_kuh(1000.0, 50.0, 38.0, 0) is None

    def test_rest_exceeds_vorlage(self):
        # Restfutter > Vorlage -> aufgenommen 0
        assert tm_verzehr_je_kuh(100.0, 150.0, 40.0, 10) == 0.0


class TestMixingAccuracy:
    def test_within_tolerance(self):
        comps = [
            LoadedComponent("maissilage", "Maissilage", soll_kg=600.0, ist_kg=615.0),
            LoadedComponent("grassilage", "Grassilage", soll_kg=300.0, ist_kg=295.0),
        ]
        r = compute_feeding_control(comps, restfutter_kg=40.0, tierzahl=58, tm_pct=40.0)
        # Abweichung gesamt = (15 + 5) / 900 * 100 = 2,22 % < 5 %
        assert r.mischgenauigkeit_pct == pytest.approx(2.2, abs=0.1)
        assert r.mischgenauigkeit_ok is True
        assert r.warnungen == []

    def test_over_tolerance_warns(self):
        comps = [
            LoadedComponent("maissilage", "Maissilage", soll_kg=600.0, ist_kg=700.0),
            LoadedComponent("grassilage", "Grassilage", soll_kg=300.0, ist_kg=300.0),
        ]
        r = compute_feeding_control(comps, restfutter_kg=0.0, tierzahl=50, tm_pct=42.0)
        # (100 + 0) / 900 * 100 = 11,1 % > 5 %
        assert r.mischgenauigkeit_pct == pytest.approx(11.1, abs=0.1)
        assert r.mischgenauigkeit_ok is False
        assert any("Mischgenauigkeit" in w for w in r.warnungen)

    def test_component_deviation_flagged(self):
        comps = [LoadedComponent("kf", "Kraftfutter", soll_kg=100.0, ist_kg=120.0)]
        r = compute_feeding_control(comps, restfutter_kg=0.0, tierzahl=10, tm_pct=88.0)
        assert r.komponenten[0].abweichung_pct == pytest.approx(20.0, abs=0.1)
        assert r.komponenten[0].innerhalb_toleranz is False


class TestIofc:
    def test_iofc_dlg_formula(self):
        comps = [LoadedComponent("tmr", "TMR", soll_kg=1000.0, ist_kg=1000.0)]
        r = compute_feeding_control(
            comps, restfutter_kg=0.0, tierzahl=50, tm_pct=40.0,
            milch_kg_kuh=32.0, milchpreis_eur_kg=0.45, futterkosten_eur_kuh=6.20,
        )
        # IOFC = 32 * 0,45 - 6,20 = 14,40 - 6,20 = 8,20
        assert r.iofc_eur_kuh == pytest.approx(8.20, abs=1e-2)

    def test_iofc_none_without_inputs(self):
        comps = [LoadedComponent("tmr", "TMR", soll_kg=1000.0, ist_kg=1000.0)]
        r = compute_feeding_control(comps, restfutter_kg=0.0, tierzahl=50, tm_pct=40.0)
        assert r.iofc_eur_kuh is None

class TestShakerBox:
    def test_pendf_actual_and_green_status(self):
        from app.agrar.rations.control.feeding_control import evaluate_shaker_box
        value = evaluate_shaker_box(oben_pct=8, mitte_pct=42, unten_pct=50, ndf_g_kgdm=360, pendf_soll_g_kgdm=175)
        assert value["struktur_gt_8mm_pct"] == 50
        assert value["pendf_ist_g_kgdm"] == 180
        assert value["status"] == "gruen"

    def test_invalid_sum_rejected(self):
        from app.agrar.rations.control.feeding_control import evaluate_shaker_box
        with pytest.raises(ValueError, match="100"):
            evaluate_shaker_box(oben_pct=8, mitte_pct=40, unten_pct=40)

    def test_selection_and_temperature_generate_actions(self):
        from app.agrar.rations.control.feeding_control import evaluate_shaker_box
        box = evaluate_shaker_box(oben_pct=20, mitte_pct=25, unten_pct=55, ndf_g_kgdm=340, pendf_soll_g_kgdm=180)
        r = compute_feeding_control([LoadedComponent("tmr", "TMR", 1000, 1100)], 50, 50, 40,
            schuettelbox=box, futtertisch_temp_c=27, umgebung_temp_c=18)
        assert any("Selektionsrisiko" in warning for warning in r.warnungen)
        assert any("Nacherwaermung" in warning for warning in r.warnungen)
        assert len(r.anpassungsvorschlaege) >= 3
def test_endpoint_exposes_full_control_loop():
    import asyncio
    from app.api.v1.endpoints.rations_optimization import _FeedingControlIn, evaluate_feeding_control
    payload = _FeedingControlIn.model_validate({
        "komponenten": [{"feed_id": "tmr", "name": "TMR", "soll_kg": 1000, "ist_kg": 1060}],
        "restfutter_kg": 50, "tierzahl": 50, "tm_pct": 40,
        "milch_kg_kuh": 32, "milchpreis_eur_kg": 0.45, "futterkosten_eur_kuh": 6.2,
        "schuettelbox": {"oben_pct": 8, "mitte_pct": 42, "unten_pct": 50,
                           "ndf_g_kgdm": 360, "pendf_soll_g_kgdm": 175},
        "futtertisch_temp_c": 27, "umgebung_temp_c": 18,
    })
    response = asyncio.run(evaluate_feeding_control(payload))
    import json
    data = json.loads(response.body)
    assert data["mischgenauigkeit_pct"] == 6.0
    assert data["tm_verzehr_kg_kuh"] == 8.08
    assert data["iofc_eur_kuh"] == 8.2
    assert data["schuettelbox"]["pendf_ist_g_kgdm"] == 180.0
    assert data["anpassungsvorschlaege"]