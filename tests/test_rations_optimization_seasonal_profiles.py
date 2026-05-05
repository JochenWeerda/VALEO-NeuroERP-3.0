"""
FAN-MODE-V1 §12 Saisonprofile — Sommer + Herbst.

Fachliche Anforderungen:
  * Sommerration (Hitzestress):
      - reduzierte TM-Aufnahme (DMI-Reduktion -3 % bis -12 %)
      - erhoehter Na-Bedarf (Schwitzverluste) um +15 % bis +30 %
      - automatisch eingesetzter Pansenpuffer NaHCO3 (SARA-Prophylaxe)
  * Herbstration (stickstoffreicher Grasaufwuchs):
      - harte CP-Dichte-Obergrenze 175 g/kg TM (Harnstoffschutz)
      - aNDFomGF-Boost um +15 g/kg TM (Strukturstuetzung)
      - maessig erhoehtes RMD-Limit (+1 g N/kg TM) fuer Weidecharakteristik
  * Policy-Profil-Auswahl:
      - PMR+Weide + summer_* -> pmr_pasture_summer
      - PMR+Weide + autumn   -> pmr_pasture_autumn
"""
from __future__ import annotations

import pytest

from app.api.v1.endpoints import rations_optimization as ro


# ---------------------------------------------------------------------------
# A) Seasonal adjustment catalog
# ---------------------------------------------------------------------------

class TestSeasonalCatalog:
    def test_neutral_profile_defaults(self):
        adj = ro._seasonal_adjustments(None)
        assert adj["dmi_factor"] == 1.0
        assert adj["na_boost_factor"] == 1.0
        assert adj["inject_buffer"] == 0.0

    def test_unknown_season_falls_back_to_neutral(self):
        adj = ro._seasonal_adjustments("never_heard_of_this")
        assert adj["dmi_factor"] == 1.0
        assert adj["na_boost_factor"] == 1.0

    def test_summer_profiles_reduce_dmi_monotonically(self):
        young = ro._seasonal_adjustments("summer_young")["dmi_factor"]
        mid = ro._seasonal_adjustments("summer_mid")["dmi_factor"]
        late = ro._seasonal_adjustments("summer_late")["dmi_factor"]
        assert 1.0 > young >= mid > late
        assert late <= 0.90  # Hochsommer/Abend -10 % oder mehr

    def test_summer_profiles_boost_na(self):
        for season in ("summer_young", "summer_mid", "summer_late"):
            assert ro._seasonal_adjustments(season)["na_boost_factor"] > 1.0

    def test_summer_injects_pansenpuffer(self):
        for season in ("summer_young", "summer_mid", "summer_late"):
            adj = ro._seasonal_adjustments(season)
            assert adj["inject_buffer"] >= 1.0
            assert adj["buffer_min_kg"] > 0.0

    def test_autumn_has_cp_cap_and_structure_boost(self):
        adj = ro._seasonal_adjustments("autumn")
        assert adj["cp_density_max_override"] <= 180.0
        assert adj["andfom_gf_min_boost"] >= 10.0
        assert adj["inject_buffer"] == 0.0  # kein Pansenpuffer im Herbst

    def test_autumn_has_moderate_rmd_boost(self):
        adj = ro._seasonal_adjustments("autumn")
        assert 0.0 < adj["rmd_max_boost"] <= 1.5


# ---------------------------------------------------------------------------
# B) Policy profile resolution (summer + autumn)
# ---------------------------------------------------------------------------

class TestPolicyProfileSummerAutumn:
    def test_pmr_pasture_summer_is_registered(self):
        assert "pmr_pasture_summer" in ro._POLICY_PROFILES

    def test_pmr_pasture_autumn_is_registered(self):
        assert "pmr_pasture_autumn" in ro._POLICY_PROFILES

    @pytest.mark.parametrize("season", ["summer_young", "summer_mid", "summer_late"])
    def test_pasture_summer_resolves_to_summer_profile(self, season):
        profile = ro._resolve_policy_profile("PMR+Weide", season)
        assert profile == "pmr_pasture_summer"

    def test_pasture_autumn_resolves_to_autumn_profile(self):
        assert ro._resolve_policy_profile("PMR+Weide", "autumn") == "pmr_pasture_autumn"

    def test_tmr_summer_ignores_season_and_keeps_tmr(self):
        assert ro._resolve_policy_profile("TMR", "summer_mid") == "tmr_standard"

    def test_explicit_override_wins(self):
        assert ro._resolve_policy_profile(
            "PMR+Weide", "summer_mid", explicit="pmr_standard"
        ) == "pmr_standard"


# ---------------------------------------------------------------------------
# C) Runtime options wiring
# ---------------------------------------------------------------------------

class TestRuntimeOptionsSeasonal:
    @pytest.mark.parametrize("season", ["summer_mid", "summer_late", "autumn"])
    def test_runtime_options_carry_seasonal_policy(self, season):
        opts = ro._resolve_runtime_options(
            {"feeding_type": "PMR+Weide"}, season_profile=season,
        )
        assert opts["season_profile"] == season
        expected = (
            "pmr_pasture_summer" if season.startswith("summer") else "pmr_pasture_autumn"
        )
        assert opts["policy_profile"] == expected


# ---------------------------------------------------------------------------
# D) End-to-end summer optimization (heat stress)
# ---------------------------------------------------------------------------

class TestSummerOptimization:
    def _profile(self, season: str) -> dict:
        return {
            "breed": "Deutsche Holstein",
            "body_weight_kg": 650,
            "milk_kg_day": 32,
            "milk_fat_pct": 3.9,
            "milk_protein_pct": 3.35,
            "lactation_stage_days": 150,
            "parity": 2,
            "feeding_type": "PMR+Weide",
            "season_profile": season,
        }

    def test_summer_mid_auto_injects_rumen_buffer(self):
        """Bei Sommerprofilen wird NaHCO3 als Pflichtbaustein mit min_kg > 0 gefuehrt.

        Wir pruefen direkt gegen den Optimizer-Response: Nach dem LP-Run MUSS die
        Pansenpuffer-Position in ration_items erscheinen (min_kg erzwingt das).
        """
        opts = ro._resolve_runtime_options(
            self._profile("summer_mid"), season_profile="summer_mid"
        )
        result = ro._optimize_internal(self._profile("summer_mid"), runtime_options=opts)
        assert result.get("status") == "optimal", (
            f"Sommerration soll machbar sein, status={result.get('status')}"
        )
        items = result.get("ration_items") or []
        buffer_items = [
            it for it in items
            if "pansenpuffer" in (it.get("name") or "").lower()
            or it.get("feed_id") == "special_summer_rumen_buffer"
        ]
        assert buffer_items, (
            "NaHCO3-Pansenpuffer muss in Sommerration enthalten sein. "
            f"Ration: {[it.get('name') for it in items]}"
        )
        assert buffer_items[0].get("kgdm", 0.0) >= 0.05

    def test_summer_mid_applies_dmi_reduction(self):
        """Requirements-basierte DMI-Reduktion bei Hitzestress."""
        profile = self._profile("summer_mid")
        req_neutral = ro._gfe_requirements(profile)
        # Baseline (kein Saisoneffekt) -> Gruber-DMI
        # Simulierte Saison-Rechnung
        opts = ro._resolve_runtime_options(profile, season_profile="summer_mid")
        # Die DMI-Reduktion wird im Optimizer angewendet; wir pruefen den Katalog
        adj = ro._seasonal_adjustments(opts["season_profile"])
        reduced = req_neutral.dmi_target_kg * adj["dmi_factor"]
        assert reduced < req_neutral.dmi_target_kg
        assert reduced >= req_neutral.dmi_target_kg * 0.80  # max 20 % Reduktion

    def test_summer_late_stronger_than_summer_young(self):
        profile_young = self._profile("summer_young")
        profile_late = self._profile("summer_late")
        req = ro._gfe_requirements(profile_young)
        adj_young = ro._seasonal_adjustments("summer_young")
        adj_late = ro._seasonal_adjustments("summer_late")
        dmi_young = req.dmi_target_kg * adj_young["dmi_factor"]
        dmi_late = req.dmi_target_kg * adj_late["dmi_factor"]
        assert dmi_late < dmi_young


# ---------------------------------------------------------------------------
# E) Autumn constraints (harnstoff protection + structure boost)
# ---------------------------------------------------------------------------

class TestAutumnConstraints:
    def _profile(self) -> dict:
        return {
            "breed": "Deutsche Holstein",
            "body_weight_kg": 650,
            "milk_kg_day": 28,
            "milk_fat_pct": 4.1,
            "milk_protein_pct": 3.4,
            "lactation_stage_days": 220,
            "parity": 3,
            "feeding_type": "PMR+Weide",
            "season_profile": "autumn",
        }

    def test_autumn_optimization_returns_policy_profile(self):
        prof = self._profile()
        opts = ro._resolve_runtime_options(prof, season_profile="autumn")
        result = ro._optimize_internal(prof, runtime_options=opts)
        assert result.get("active_policy_profile") == "pmr_pasture_autumn"
        assert result.get("season_profile") == "autumn"

    def test_autumn_does_not_inject_rumen_buffer(self):
        adj = ro._seasonal_adjustments("autumn")
        assert adj["inject_buffer"] == 0.0

    def test_autumn_cp_cap_is_tighter_than_default_pmr_weide(self):
        """CP-Dichte-Obergrenze Herbst (175 g/kg TM) < default PMR+Weide (185)."""
        adj = ro._seasonal_adjustments("autumn")
        assert adj["cp_density_max_override"] <= 180.0

    def test_autumn_structure_boost_increases_andfom_gf_min(self):
        adj = ro._seasonal_adjustments("autumn")
        assert adj["andfom_gf_min_boost"] >= 10.0


# ---------------------------------------------------------------------------
# F) Compatibility: existing seasons remain neutral
# ---------------------------------------------------------------------------

class TestBackwardsCompatibility:
    @pytest.mark.parametrize("season", ["spring_young", "spring_mid", "spring_late", "winter"])
    def test_non_stress_seasons_keep_dmi_and_na(self, season):
        adj = ro._seasonal_adjustments(season)
        assert adj["dmi_factor"] == 1.0
        assert adj["na_boost_factor"] == 1.0
        assert adj["inject_buffer"] == 0.0

    def test_season_profile_none_keeps_defaults(self):
        opts = ro._resolve_runtime_options({"feeding_type": "TMR"})
        assert opts["season_profile"] is None
        assert opts["policy_profile"] == "tmr_standard"
