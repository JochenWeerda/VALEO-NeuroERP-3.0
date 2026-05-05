"""Tests fuer den SARA-Safety-Reopt-Loop, pH-Formel und peNDF-Faktoren.

Hintergrund (2026-04-21):
  1. pH-Predictor wurde mit peNDF/Staerke in g/kg TM gespeist, die Formel
     erwartet aber % TM. Folge: alle realistisch optimierten Rationen
     meldeten pH=5.50 (ROT) trotz GRUEN in allen anderen Indikatoren.
  2. ``_feed_pendf_factor`` setzte pauschal 0.90 fuer alle Grobfutter,
     was fachlich unplausible peNDF-Dichten von ~370 g/kg TM lieferte.
     Zebeli 2012 / DLG 01|2023 geben differenzierte Quoten vor
     (Heu 0.95, Grassilage 0.55, Maissilage 0.45 usw.).

DLG2025-PH-FORMEL (2026-04-21): ``_ph_predict`` verwendet jetzt die von
DLG 01|2025 offiziell zitierten Zebeli-2008-Koeffizienten
(6,05 / 0,044 / 0,0006 / 0,017 / 0,016) und die **pansenabbaubare**
Staerke (ST - bST) als Input, nicht mehr die Gesamt-Staerke.

Ergaenzung: Azidose-Safety-Reopt-Loop bei rot-Ampel.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

import pytest

from app.api.v1.endpoints import rations_optimization as ro


# ---------------------------------------------------------------------------
# 1) pH-Formel-Validitaetsbereich und Einheiten-Umrechnung
# ---------------------------------------------------------------------------

class TestPhPredictUnitsAndRange:
    def test_ph_predict_realistic_tmr_is_in_physiological_band(self):
        # peNDF=200 g/kg TM (= 20 %), abbauSt=150 g/kg TM (= 15 %),
        # DMI=22 kg/d -> Zebeli 2008 (DLG 01|2025):
        #   pH = 6,05 + 0,044*20 - 0,0006*400 - 0,017*15 - 0,016*22 ~ 6,08
        ph = ro._ph_predict(200.0, 150.0, 22.0)
        assert 6.00 <= ph <= 6.20, (
            "Realistische TMR-Ration muss pH im physiologischen Zielband "
            f"(DLG 01|2025) liefern, berechnet: {ph}"
        )

    def test_ph_predict_high_pendf_does_not_crash(self):
        # Extrem hohe peNDF (>250) werden auf 250 geclippt, Formel bleibt
        # anwendbar. Mit abbauSt=150 und DMI=22 erwartet Zebeli 2008:
        #   pH = 6,05 + 0,044*25 - 0,0006*625 - 0,017*15 - 0,016*22 ~ 6,17
        ph = ro._ph_predict(370.0, 150.0, 22.0)
        assert 5.8 <= ph <= 7.0, (
            "Extrem strukturierte Ration darf keinen SARA-Pseudowert liefern, "
            f"berechnet: {ph}"
        )

    def test_ph_predict_low_pendf_triggers_low_ph(self):
        # peNDF=60 g/kg TM (6%) und abbauSt=300 g/kg TM (30%) liefert nach
        # Zebeli 2008:
        #   pH = 6,05 + 0,044*6 - 0,0006*36 - 0,017*30 - 0,016*22 ~ 5,43 -> clip 5,5
        ph = ro._ph_predict(60.0, 300.0, 22.0)
        assert ph < 6.0, (
            "Niedrige peNDF + hohe abbaubare Staerke muss pH < 6.0 liefern, "
            f"berechnet: {ph}"
        )

    def test_ph_inputs_in_range_detects_out_of_band(self):
        assert ro._ph_inputs_in_range(200.0, 150.0, 22.0) is True
        assert ro._ph_inputs_in_range(50.0, 150.0, 22.0) is False  # peNDF < 60
        assert ro._ph_inputs_in_range(260.0, 150.0, 22.0) is False  # peNDF > 250
        assert ro._ph_inputs_in_range(200.0, 30.0, 22.0) is False   # abbauSt < 50
        assert ro._ph_inputs_in_range(200.0, 400.0, 22.0) is False  # abbauSt > 350
        assert ro._ph_inputs_in_range(200.0, 150.0, 8.0) is False   # DMI < 10
        assert ro._ph_inputs_in_range(200.0, 150.0, 30.0) is False  # DMI > 25

    def test_ph_predict_uses_dlg2025_zebeli_2008_coeffs(self):
        """Die Koeffizienten muessen den von DLG 01|2025 zitierten Zebeli-2008-
        Wert entsprechen: pH(20%peNDF, 15%abbauSt, 22 kg DMI) ~ 6,08.
        """
        ph = ro._ph_predict(200.0, 150.0, 22.0)
        expected = 6.05 + 0.044 * 20 - 0.0006 * 400 - 0.017 * 15 - 0.016 * 22
        assert abs(ph - round(expected, 2)) < 0.02, (
            f"pH-Formel weicht von DLG 01|2025 / Zebeli 2008 ab: erwartet "
            f"~{expected:.2f}, bekam {ph}"
        )


# ---------------------------------------------------------------------------
# 2) peNDF-Faktoren nach Zebeli 2012 / DLG 01|2023
# ---------------------------------------------------------------------------

class TestFeedPendfFactor:
    @pytest.mark.parametrize(
        "feed,expected",
        [
            ({"group": "Grundfutter/Grobfutter", "name": "Weizenstroh"}, 1.00),
            ({"group": "Grundfutter/Grobfutter", "name": "Heu, 1. Schnitt"}, 0.95),
            ({"group": "Grundfutter/Grobfutter", "name": "Luzernesilage"}, 0.70),
            ({"group": "Grundfutter/Grobfutter", "name": "Grassilage mittel"}, 0.55),
            ({"group": "Grundfutter/Grobfutter", "name": "Maissilage, hoch"}, 0.45),
            ({"group": "Grundfutter/Grobfutter", "name": "Frischgras jung"}, 0.55),
            ({"group": "Grundfutter/Grobfutter", "name": "Ganzpflanzensilage Weizen"}, 0.50),
            ({"group": "Kraftfutter/Trocken", "name": "Gerste, Samen"}, 0.10),
            ({"group": "Kraftfutter/Trocken", "name": "Mais, Korn"}, 0.10),
            ({"group": "Kraftfutter/Trocken", "name": "Rapsextraktionsschrot"}, 0.10),
            ({"group": "Grundfutter/Saftfutter", "name": "Biertreber, nass"}, 0.25),
            ({"group": "Grundfutter/Grobfutter", "name": "Ruebenblattsilage"}, 0.35),
            ({"group": "Zusatzstoffe", "name": "Mineralfutter"}, 0.0),
        ],
    )
    def test_feed_pendf_factor_aligns_with_zebeli_2012(self, feed, expected):
        got = ro._feed_pendf_factor(feed)
        assert got == pytest.approx(expected, abs=0.001), (
            f"Feed={feed['name']} erwartet peNDF-Faktor {expected}, bekam {got}"
        )


# ---------------------------------------------------------------------------
# 3) SARA-Risk-Detection (pre-Reopt)
# ---------------------------------------------------------------------------

class _FakeSolveResult:
    def __init__(self, x, status=0):
        self.x = list(x)
        self.status = status


def _build_fake_lp_out_high_starch() -> Dict[str, Any]:
    """Konstruiere einen lp_out, der SARA-Rot liefert (hoher Staerke, wenig peNDF)."""
    feeds = [
        {
            "id": "mais_sil", "name": "Maissilage", "group": "Grundfutter/Grobfutter",
            "forage": True, "ndf": 400.0, "st": 300.0, "zu": 10.0, "bst": 30.0,
            "me": 11.0, "sidp": 80.0, "cp": 80.0, "ca": 2.0, "p": 2.0, "na": 0.5,
            "mg": 1.5, "k": 12.0, "xl": 28.0, "dm_frac": 0.35, "price": 0.06,
            "min_kg": 0.0, "max_kg": 20.0,
        },
        {
            "id": "weizen", "name": "Weizen", "group": "Kraftfutter/Trocken",
            "forage": False, "ndf": 140.0, "st": 620.0, "zu": 15.0, "bst": 15.0,
            "me": 13.2, "sidp": 72.0, "cp": 110.0, "ca": 0.6, "p": 4.0, "na": 0.1,
            "mg": 1.2, "k": 5.0, "xl": 18.0, "dm_frac": 0.88, "price": 0.24,
            "min_kg": 0.0, "max_kg": 10.0,
        },
    ]
    # 12 kg Maissilage + 10 kg Weizen -> viel Staerke, wenig peNDF.
    amounts = [12.0, 10.0]
    return {
        "scipy_result": _FakeSolveResult(amounts, status=0),
        "feeds": feeds,
    }


def _build_fake_lp_out_healthy() -> Dict[str, Any]:
    """Konstruiere einen lp_out, der fachlich sauber ist (keine SARA-Trigger)."""
    feeds = [
        {
            "id": "grass_sil", "name": "Grassilage", "group": "Grundfutter/Grobfutter",
            "forage": True, "ndf": 450.0, "st": 0.0, "zu": 50.0, "bst": 0.0,
            "me": 11.2, "sidp": 108.0, "cp": 171.0, "ca": 6.0, "p": 4.5, "na": 1.5,
            "mg": 2.5, "k": 28.0, "xl": 35.0, "dm_frac": 0.35, "price": 0.05,
            "min_kg": 0.0, "max_kg": 20.0,
        },
        {
            "id": "mais_sil", "name": "Maissilage", "group": "Grundfutter/Grobfutter",
            "forage": True, "ndf": 400.0, "st": 300.0, "zu": 10.0, "bst": 30.0,
            "me": 11.2, "sidp": 78.0, "cp": 80.0, "ca": 2.0, "p": 2.0, "na": 0.5,
            "mg": 1.5, "k": 12.0, "xl": 28.0, "dm_frac": 0.35, "price": 0.06,
            "min_kg": 0.0, "max_kg": 20.0,
        },
        {
            "id": "soy_meal", "name": "Sojaextraktionsschrot", "group": "Kraftfutter/Trocken",
            "forage": False, "ndf": 154.0, "st": 68.0, "zu": 0.0, "bst": 0.0,
            "me": 13.9, "sidp": 250.0, "cp": 500.0, "ca": 3.0, "p": 7.0, "na": 0.1,
            "mg": 2.8, "k": 20.0, "xl": 15.0, "dm_frac": 0.88, "price": 0.40,
            "min_kg": 0.0, "max_kg": 3.0,
        },
    ]
    amounts = [11.0, 8.0, 2.5]
    return {
        "scipy_result": _FakeSolveResult(amounts, status=0),
        "feeds": feeds,
    }


class TestSaraRiskDetection:
    def test_healthy_ration_has_no_sara_trigger(self):
        lp_out = _build_fake_lp_out_healthy()
        profile = {"feeding_type": "TMR", "milk_kg_day": 30.0, "body_weight_kg": 650.0}
        risk = ro._detect_sara_risk(lp_out, profile)
        assert risk["triggered"] is False, f"Saubere Ration darf keinen SARA-Trigger liefern: {risk}"
        assert risk["metrics"]["ph_predicted"] >= 6.1

    def test_high_starch_low_pendf_triggers_sara(self):
        lp_out = _build_fake_lp_out_high_starch()
        profile = {"feeding_type": "TMR", "milk_kg_day": 42.0, "body_weight_kg": 680.0}
        risk = ro._detect_sara_risk(lp_out, profile)
        assert risk["triggered"] is True, f"SARA-rote Ration muss Trigger ausloesen: {risk}"
        assert risk["reason"] is not None
        assert risk["metrics"]["ph_predicted"] < 6.2 or risk["metrics"]["pendf_kgdm"] < risk["metrics"]["pendf_min_kgdm"]


# ---------------------------------------------------------------------------
# 4) Safety-Reopt end-to-end (mit echtem Solver auf SARA-kritischem Szenario)
# ---------------------------------------------------------------------------

class TestSaraSafetyReoptEndToEnd:
    def test_sara_reopt_flag_present_in_response(self):
        # Normales Szenario: reopt wird nicht getriggert, Key muss aber existieren.
        profile = {
            "breed": "Deutsche Holstein",
            "body_weight_kg": 670.0,
            "milk_kg_day": 30.0,
            "milk_fat_pct": 4.0,
            "milk_protein_pct": 3.4,
            "lactation_stage_days": 100,
            "parity": 2,
            "production_group": "Hochleistung",
            "feeding_type": "TMR",
        }
        result = ro._optimize_internal(profile)
        assert "sara_safety_reopt" in result
        assert result["sara_safety_reopt"]["triggered"] is False

    def test_sara_reopt_triggered_on_synthetic_risk_via_overrides(self):
        # Erzwinge einen Solve, der ph-rot liefert: kuenstliche sara_overrides
        # mit "zu weichen" pabKH/xl-Werten koennen den Testpfad nicht direkt,
        # stattdessen nutzen wir das interne _detect_sara_risk + _maybe_...-Paar
        # mit einem synthetischen lp_out.
        lp_out = _build_fake_lp_out_high_starch()
        profile = {"feeding_type": "TMR", "milk_kg_day": 42.0, "body_weight_kg": 680.0}
        # Fake req-Objekt ausreichend populieren
        req = ro._CowReq(
            me_mj=260.0, sidp_g=2400.0, nel_mj=160.0, nxp_g=2500.0,
            dmi_min_kg=20.0, dmi_max_kg=24.0, dmi_target_kg=22.0,
            ndf_min_g=6000.0, ca_min_g=55.0, p_min_g=40.0, na_min_g=22.0,
            mg_min_g=35.0, k_max_g=550.0,
        )
        runtime_opts = {
            "fan": {"mode": "reference", "reference": 3.0, "tolerance": 0.05,
                    "tolerance_warn": 0.10, "max_iterations": 5},
            "season_profile": None, "policy_profile": "tmr_standard",
            "relaxation_policy": "standard", "objective_strategy": "balance_then_cost",
        }
        new_lp = ro._maybe_run_sara_safety_reopt(
            lp_out=lp_out, req=req, feeds=lp_out["feeds"], profile=profile,
            runtime_options=runtime_opts, fan_mode="reference", fan_reference=3.0,
            fan_tol=0.05, fan_max_iter=3, seasonal={}, buffer_min_kg=0.0,
        )
        payload = new_lp.get("_sara_reopt")
        assert payload is not None, "Reopt-Payload muss gesetzt sein."
        assert payload["triggered"] is True
        assert payload["reason"] is not None
        assert any("peNDF" in a or "NaHCO3" in a or "pabKH" in a for a in payload.get("actions", []))

    def test_sara_reopt_runtime_option_hint_flag_inactive_when_healthy(self):
        profile = {
            "breed": "Deutsche Holstein",
            "body_weight_kg": 670.0,
            "milk_kg_day": 28.0,
            "milk_fat_pct": 4.0,
            "milk_protein_pct": 3.4,
            "lactation_stage_days": 150,
            "parity": 2,
            "production_group": "Hochleistung",
            "feeding_type": "PMR+Weide",
            "season_profile": "summer_mid",
        }
        result = ro._optimize_internal(profile)
        payload = result.get("sara_safety_reopt") or {}
        # Sommer-PMR+Weide ist fachlich sauber, kein SARA-Reopt erwartet.
        assert payload.get("triggered") is False


# ---------------------------------------------------------------------------
# 5) Regression: Warnung nur noch bei Formel-Validitaet
# ---------------------------------------------------------------------------

class TestPhWarningGating:
    def test_no_false_positive_sara_warning_on_well_structured_ration(self):
        profile = {
            "breed": "Deutsche Holstein",
            "body_weight_kg": 670.0,
            "milk_kg_day": 35.0,
            "milk_fat_pct": 4.0,
            "milk_protein_pct": 3.4,
            "lactation_stage_days": 100,
            "parity": 2,
            "production_group": "Hochleistung",
            "feeding_type": "TMR",
        }
        result = ro._optimize_internal(profile)
        warnings = result.get("warnings") or []
        assert not any(
            "SARA" in w and "wahrscheinlich" in w for w in warnings
        ), (
            "Fachlich saubere TMR darf keine SARA-False-Positive-Warnung mehr liefern. "
            f"warnings: {warnings}"
        )
        ind = result.get("dlg_indicators") or {}
        assert ind.get("ph_predicted") is not None and ind["ph_predicted"] >= 6.2
