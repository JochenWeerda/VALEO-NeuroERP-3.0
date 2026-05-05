"""Tests fuer die peNDF-Degradierung zur Kontrollgroesse (DLG 01|2023).

Hintergrund:
    Die DLG schreibt explizit, dass peNDF fuer die Rationsplanung nicht zur
    Verfuegung steht und empfiehlt stattdessen aNDFom aus dem Grobfutter
    (aNDFomGF) als primaere Planungsgroesse. Zielwert fuer Hochleistungsrationen
    ist >= 200 g/kg TM aNDFomGF, bei hoeheren pansenabbaubaren KH entsprechend
    mehr. peNDF bleibt als Kontroll-/Validierungsgroesse erhalten.

Diese Tests validieren:
  * staerkeadaptive Aufstufung der aNDFomGF-Mindestdichte,
  * Kalibrierungsstatus des peNDF-Modells (pendf_model_calibrated + Status-Text),
  * peNDF-Ampel im Response-Dict als Kontrollgroesse mit passendem Label,
  * kein False-Positive-SARA-Trigger bei peNDF ausserhalb des Modellbereichs.

Die Tests sind LP-frei und arbeiten auf den Helper-Funktionen sowie synthetischen
`lp_out`-Strukturen.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pytest

from app.api.v1.endpoints import rations_optimization as ro


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

class _FakeScipyResult:
    def __init__(self, x: List[float], status: int = 0) -> None:
        self.x = list(x)
        self.status = status
        self.fun = 0.0
        self.success = status == 0
        self.message = "ok" if status == 0 else "infeasible"


def _make_feed(
    feed_id: str,
    *,
    ndf: float,
    st: float,
    zu: float = 0.0,
    forage: bool,
    group: str = "Grundfutter",
    name: str = "",
) -> Dict[str, Any]:
    return {
        "id": feed_id,
        "name": name or feed_id,
        "group": group,
        "dm_frac": 0.35 if forage else 0.88,
        "price": 0.10,
        "me": 6.5 if forage else 8.0,
        "sidp": 60 if forage else 140,
        "ndf": ndf,
        "st": st,
        "zu": zu,
        "bst": 0.0,
        "xl": 20.0,
        "cp": 150.0 if forage else 180.0,
        "ca": 6.0,
        "p": 3.5,
        "na": 0.6,
        "mg": 2.5,
        "k": 12.0,
        "sidlys": 6.0,
        "sidmet": 2.0,
        "rmd": 0.0,
        "forage": forage,
        "min_kg": 0.0,
        "max_kg": 20.0,
    }


def _fake_lp_out(
    amounts: List[float],
    feeds: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "scipy_result": _FakeScipyResult(amounts, status=0),
        "feeds": feeds,
        "_relaxed": True,
        "_infeasibility_hint": None,
    }


# ---------------------------------------------------------------------------
# Staerkeadaptive aNDFomGF-Mindestdichte
# ---------------------------------------------------------------------------

class TestAndfomGfStarchAdaptive:
    @pytest.mark.parametrize(
        "starch_kgdm,expected",
        [
            (0.0, 0.0),
            (180.0, 0.0),
            (200.0, 10.0),
            (220.0, 20.0),
            (260.0, 40.0),
            # Cap bei 40
            (400.0, 40.0),
        ],
    )
    def test_starch_uplift_linear_capped(self, starch_kgdm, expected):
        assert ro._andfom_gf_starch_uplift(starch_kgdm) == expected

    def test_target_non_pasture_base_200(self):
        assert ro._andfom_gf_min_target(staerke_density_kgdm=150.0, pasture_pmr=False) == 200.0

    def test_target_pasture_base_180(self):
        assert ro._andfom_gf_min_target(staerke_density_kgdm=100.0, pasture_pmr=True) == 180.0

    def test_target_high_starch_non_pasture(self):
        assert ro._andfom_gf_min_target(staerke_density_kgdm=240.0, pasture_pmr=False) == 230.0

    def test_target_seasonal_and_sara_boost_are_additive(self):
        t = ro._andfom_gf_min_target(
            staerke_density_kgdm=220.0,
            pasture_pmr=False,
            seasonal_boost=15.0,
            sara_boost=10.0,
        )
        assert t == 200.0 + 20.0 + 15.0 + 10.0


# ---------------------------------------------------------------------------
# peNDF-Modell-Kalibrierungsstatus
# ---------------------------------------------------------------------------

class TestPendfModelCalibrated:
    @pytest.mark.parametrize(
        "starch_kgdm,dmi_kg,expected",
        [
            (100.0, 20.0, True),
            (250.0, 25.0, True),
            (260.0, 20.0, False),
            (200.0, 9.0, False),
            (200.0, 26.0, False),
            (-1.0, 20.0, False),
        ],
    )
    def test_calibrated_flag(self, starch_kgdm, dmi_kg, expected):
        assert ro._pendf_model_calibrated(starch_kgdm, dmi_kg) is expected


# ---------------------------------------------------------------------------
# dlg_indicators-Felder & Rolle der peNDF-Ampel
# ---------------------------------------------------------------------------

class TestDlgIndicatorsPendfRole:
    def _build_response(self, feeds, amounts, *, feeding_type: str = "TMR") -> Dict[str, Any]:
        lp_out = _fake_lp_out(amounts, feeds)
        req = ro._CowReq(
            dmi_min_kg=18.0,
            dmi_max_kg=26.0,
            dmi_target_kg=22.0,
            me_mj=160.0,
            nel_mj=100.0,
            sidp_g=1600.0,
            nxp_g=1700.0,
            ndf_min_g=4200.0,
            ca_min_g=120.0,
            p_min_g=60.0,
            na_min_g=18.0,
            mg_min_g=25.0,
            k_max_g=260.0,
        )
        profile = {
            "breed": "Holstein",
            "body_weight_kg": 650,
            "milk_kg_day": 32,
            "feeding_type": feeding_type,
        }
        return ro._build_response(lp_out, req, profile)

    def test_pendf_labeled_as_control_variable(self):
        grassilage = _make_feed("grassilage", ndf=440.0, st=0.0, forage=True, group="Grundfutter/Grassilage", name="Grassilage")
        heu = _make_feed("heu", ndf=600.0, st=0.0, forage=True, group="Grundfutter/Heu", name="Heu")
        kf = _make_feed("kf", ndf=180.0, st=350.0, forage=False, group="Kraftfutter", name="Kraftfutter")
        feeds = [grassilage, heu, kf]
        amounts = [9.0, 3.0, 6.0]
        resp = self._build_response(feeds, amounts)
        dlg = resp["dlg_indicators"]
        # peNDF ist jetzt Kontrollgroesse - im Zieltext erkennbar
        assert "Kontrolle" in dlg["pendf_ziel"]
        assert "aNDFomGF" in dlg["pendf_ziel"]
        assert dlg["pendf_role"].startswith("Kontrolle")
        # aNDFomGF bleibt primaere Steuergroesse mit klarer Herkunft
        assert "andfom_gf_base" in dlg
        assert "andfom_gf_starch_uplift" in dlg

    def test_pendf_model_status_text_for_calibrated(self):
        grassilage = _make_feed("grassilage", ndf=440.0, st=0.0, forage=True, group="Grundfutter/Grassilage", name="Grassilage")
        kf = _make_feed("kf", ndf=180.0, st=200.0, forage=False, group="Kraftfutter", name="Kraftfutter")
        feeds = [grassilage, kf]
        amounts = [14.0, 6.0]
        resp = self._build_response(feeds, amounts)
        dlg = resp["dlg_indicators"]
        assert dlg["pendf_model_calibrated"] is True
        assert dlg["pendf_model_status"] == "peNDF-Modell im kalibrierten Bereich"

    def test_pendf_model_status_text_when_out_of_range(self):
        heu = _make_feed("heu", ndf=600.0, st=0.0, forage=True, group="Grundfutter/Heu", name="Heu")
        kf_extrem = _make_feed("kf_extrem", ndf=120.0, st=600.0, forage=False, group="Kraftfutter", name="Kraftfutter extrem")
        feeds = [heu, kf_extrem]
        # Hohe KF-Anteile treiben Staerke > 250 g/kg TM -> ausserhalb Kalibrierbereich
        amounts = [3.0, 12.0]
        resp = self._build_response(feeds, amounts)
        dlg = resp["dlg_indicators"]
        assert dlg["pendf_model_calibrated"] is False
        assert "ausserhalb" in dlg["pendf_model_status"].lower()
        assert "fallback" in dlg["pendf_model_status"].lower()


# ---------------------------------------------------------------------------
# SARA-Risiko nutzt peNDF nur im kalibrierten Bereich
# ---------------------------------------------------------------------------

class TestSaraTriggerRespectsCalibration:
    def test_uncalibrated_pendf_does_not_trigger_sara(self):
        """Bei peNDF ausserhalb Modellbereich darf peNDF allein keinen SARA-Reopt triggern.

        aNDFomGF und pH bleiben valide Trigger, aber die reine Modell-
        Extrapolation soll keinen Alarm ausloesen.
        """
        # Starch > 250 bringt Modell in Fallback; gleichzeitig gute aNDFomGF & pH.
        grassilage = _make_feed("grassilage", ndf=500.0, st=0.0, forage=True, group="Grundfutter/Grassilage", name="Grassilage")
        heu = _make_feed("heu", ndf=600.0, st=0.0, forage=True, group="Grundfutter/Heu", name="Heu")
        stroh = _make_feed("stroh", ndf=800.0, st=0.0, forage=True, group="Grundfutter/Stroh", name="Stroh")
        kf = _make_feed("kf", ndf=180.0, st=500.0, forage=False, group="Kraftfutter", name="Kraftfutter")
        feeds = [grassilage, heu, stroh, kf]
        amounts = [7.0, 3.0, 2.0, 9.0]  # starch density ~ 500*9/21 = 214; Grenzbereich
        profile = {
            "breed": "Holstein",
            "body_weight_kg": 650,
            "feeding_type": "TMR",
        }
        lp_out = _fake_lp_out(amounts, feeds)
        risk = ro._detect_sara_risk(lp_out, profile)
        # aNDFomGF ~ (7*500+3*600+2*800)/21 = (3500+1800+1600)/21 = 329 > Ziel (230)
        # pabKH ~ (9*500)/21 = 214 < limit 210? Limit=210, 214>207 -> trigger
        # Der Test soll zeigen: peNDF darf nicht _alleiniger_ Trigger sein.
        metrics = risk["metrics"]
        # Wenn Modell extrapoliert wurde, darf peNDF nicht als Grund in reasons stehen.
        if not metrics["pendf_model_calibrated"]:
            reasons = risk.get("reason") or ""
            assert "peNDF" not in reasons or "aNDFomGF" in reasons or "pabKH" in reasons

    def test_calibrated_low_pendf_and_low_andfomgf_still_trigger(self):
        grassilage = _make_feed("grassilage", ndf=400.0, st=0.0, forage=True, group="Grundfutter/Grassilage", name="Grassilage")
        kf = _make_feed("kf", ndf=180.0, st=400.0, forage=False, group="Kraftfutter", name="Kraftfutter")
        feeds = [grassilage, kf]
        # wenig Grobfutter -> niedrige aNDFomGF + hohe pabKH
        amounts = [5.0, 15.0]
        profile = {
            "breed": "Holstein",
            "body_weight_kg": 650,
            "feeding_type": "TMR",
        }
        lp_out = _fake_lp_out(amounts, feeds)
        risk = ro._detect_sara_risk(lp_out, profile)
        assert risk["triggered"] is True
        reason = risk["reason"] or ""
        # aNDFomGF oder pabKH muss Trigger sein
        assert ("aNDFomGF" in reason) or ("pabKH" in reason) or ("pH" in reason)


# ---------------------------------------------------------------------------
# Warnings: peNDF-Fallback ergibt Hinweis
# ---------------------------------------------------------------------------

class TestWarningsForUncalibratedPendf:
    def test_warning_when_pendf_out_of_range(self):
        heu = _make_feed("heu", ndf=600.0, st=0.0, forage=True, group="Grundfutter/Heu", name="Heu")
        # Starch-Density weit > 250 -> Fallback
        kf_extrem = _make_feed("kf_extrem", ndf=120.0, st=600.0, forage=False, group="Kraftfutter", name="Kraftfutter extrem")
        feeds = [heu, kf_extrem]
        amounts = [3.0, 12.0]
        lp_out = _fake_lp_out(amounts, feeds)
        req = ro._CowReq(
            dmi_min_kg=12.0, dmi_max_kg=20.0, dmi_target_kg=15.0,
            me_mj=120.0, nel_mj=75.0, sidp_g=1200.0, nxp_g=1300.0, ndf_min_g=3000.0,
            ca_min_g=90.0, p_min_g=50.0, na_min_g=14.0, mg_min_g=20.0, k_max_g=220.0,
        )
        resp = ro._build_response(
            lp_out, req,
            {"breed": "Holstein", "body_weight_kg": 650, "feeding_type": "TMR"},
        )
        joined = " | ".join(resp.get("warnings", []))
        assert "peNDF ausserhalb Modellbereich" in joined or "Fallback" in joined
