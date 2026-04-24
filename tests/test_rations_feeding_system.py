"""Tests fuer das gestaffelte Fuetterungsmodell (Slice 1a/1b).

Abgedeckt:
  - FeedingSystemConfig / ConcentrateRecipeProfile Pydantic-Validierung
  - Default-Konzentratgrenzen je Distribution (Transponder/AMS/Melkstand)
  - Praxis-Regeln: Faersen 4 kg, Holstein Mehrlakt 4.5 kg, Premium 5 kg
  - Abwaertskompatibilitaet: ohne FeedingSystemConfig -> Fallback aus feeding_type
  - Automatische Block-Zuordnung nach TM, Feed-Gruppe und Feeding-System
  - Override-Logik (manuelle Block-Zuweisung)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints import rations_optimization as ro
from app.api.v1.endpoints.rations_optimization import (
    ConcentrateRecipeProfile,
    FeedingSystemConfig,
)


# ---------------------------------------------------------------------------
# Pydantic-Modelle
# ---------------------------------------------------------------------------

class TestConcentrateRecipeProfile:
    def test_defaults(self) -> None:
        p = ConcentrateRecipeProfile()
        assert p.starch_breakdown_class == "mixed"
        assert p.rumen_buffer_present is False
        assert p.source == "default"
        assert p.mill_byproduct_share is None
        assert p.slow_starch_share is None

    def test_slow_starch_profile(self) -> None:
        p = ConcentrateRecipeProfile(
            starch_breakdown_class="slow",
            slow_starch_share=0.65,
            rumen_buffer_present=True,
            source="declared",
        )
        assert p.starch_breakdown_class == "slow"
        assert p.slow_starch_share == 0.65
        assert p.rumen_buffer_present is True
        assert p.source == "declared"

    def test_invalid_starch_class(self) -> None:
        with pytest.raises(ValidationError):
            ConcentrateRecipeProfile(starch_breakdown_class="super-slow")

    def test_invalid_source(self) -> None:
        with pytest.raises(ValidationError):
            ConcentrateRecipeProfile(source="guessed")


class TestFeedingSystemConfig:
    def test_defaults_tmr(self) -> None:
        c = FeedingSystemConfig()
        assert c.system == "TMR"
        assert c.concentrate_distribution == "included_in_tmr"
        assert c.treat_as_primiparous is False

    def test_pmr_pasture_milkparlor(self) -> None:
        c = FeedingSystemConfig(
            system="PMR_pasture",
            concentrate_distribution="milkparlor",
            treat_as_primiparous=True,
        )
        assert c.system == "PMR_pasture"
        assert c.concentrate_distribution == "milkparlor"
        assert c.treat_as_primiparous is True

    def test_invalid_system(self) -> None:
        with pytest.raises(ValidationError):
            FeedingSystemConfig(system="invalid")

    def test_invalid_distribution(self) -> None:
        with pytest.raises(ValidationError):
            FeedingSystemConfig(concentrate_distribution="bucket")


# ---------------------------------------------------------------------------
# _feeding_system_defaults: Konzentratgrenzen je Verteilungssystem
# ---------------------------------------------------------------------------

class TestConcentrateLimitsTransponder:
    def test_transponder_default(self) -> None:
        d = ro._feeding_system_defaults("PMR_stall", "transponder")
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(2.5)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(8.0)

    def test_transponder_ignores_parity(self) -> None:
        # Transponder-Limit ist nicht parity-abhaengig in V1
        d_primi = ro._feeding_system_defaults("PMR_stall", "transponder", treat_as_primiparous=True)
        d_multi = ro._feeding_system_defaults("PMR_stall", "transponder", treat_as_primiparous=False)
        assert d_primi["concentrate_max_per_day_kg"] == d_multi["concentrate_max_per_day_kg"]


class TestConcentrateLimitsAms:
    def test_ams_default(self) -> None:
        d = ro._feeding_system_defaults("PMR_stall", "ams")
        # 2.0 kg/Melkung * 3 Melkungen = 6 kg/Tag als konservativer Praxisrichtwert
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(2.0)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(6.0)
        assert d["concentrate_servings_per_day"] == pytest.approx(3.0)


class TestConcentrateLimitsMilkparlor:
    """DLG-Praxis-Regeln User-Abstimmung 2026-04-21."""

    def test_holstein_multiparous_default(self) -> None:
        d = ro._feeding_system_defaults("PMR_stall", "milkparlor", treat_as_primiparous=False)
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(4.5)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(9.0)
        assert d["concentrate_servings_per_day"] == pytest.approx(2.0)

    def test_primiparous_reduced(self) -> None:
        d = ro._feeding_system_defaults("PMR_stall", "milkparlor", treat_as_primiparous=True)
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(4.0)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(8.0)

    def test_premium_concentrate_raises_limit(self) -> None:
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="slow", rumen_buffer_present=True
        )
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=False, recipe=recipe
        )
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(5.0)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(10.0)

    def test_slow_starch_without_buffer_not_premium(self) -> None:
        # Slow starch ALLEIN reicht nicht - beide Bedingungen noetig
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="slow", rumen_buffer_present=False
        )
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=False, recipe=recipe
        )
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(4.5)  # Standard-Limit

    def test_buffer_without_slow_starch_not_premium(self) -> None:
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="mixed", rumen_buffer_present=True
        )
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=False, recipe=recipe
        )
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(4.5)

    def test_primiparous_with_premium_still_standard(self) -> None:
        # Premium-Limit auch bei 1. Laktation verfuegbar
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="slow", rumen_buffer_present=True
        )
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=True, recipe=recipe
        )
        # Premium ueberschreibt Primi-Limit (fachlich: slow starch schuetzt Pansen)
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(5.0)


class TestConcentrateLimitsIncludedInTmr:
    def test_tmr_included_has_no_staged_limit(self) -> None:
        d = ro._feeding_system_defaults("TMR", "included_in_tmr")
        assert d["concentrate_max_per_serving_kg"] == 0.0
        assert d["concentrate_max_per_day_kg"] == 0.0
        assert d["concentrate_servings_per_day"] == 0.0


class TestConcentrateClassAdjustmentRapid:
    """User-Review 2026-04-23, §5: rapid-Klasse REDUZIERT Limits (SARA-Schutz)."""

    def test_milkparlor_rapid_reduces_serving_and_day(self) -> None:
        recipe = ConcentrateRecipeProfile(starch_breakdown_class="rapid")
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=False, recipe=recipe
        )
        # Standard Melkstand Holstein: 4,5 / 9,0 -> rapid: -0,5 / -1,5
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(4.0)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(7.5)

    def test_transponder_rapid_reduces_limits(self) -> None:
        recipe = ConcentrateRecipeProfile(starch_breakdown_class="rapid")
        d = ro._feeding_system_defaults("PMR_stall", "transponder", recipe=recipe)
        # Transponder-Standard 2,5 / 8,0 -> rapid: 2,0 / 6,5
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(2.0)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(6.5)

    def test_ams_rapid_reduces_limits(self) -> None:
        recipe = ConcentrateRecipeProfile(starch_breakdown_class="rapid")
        d = ro._feeding_system_defaults("PMR_stall", "ams", recipe=recipe)
        # AMS-Standard 2,0 / 6,0 -> rapid: 1,5 / 4,5
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(1.5)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(4.5)

    def test_rapid_primiparous_milkparlor(self) -> None:
        """Primipara + rapid: beide Reduktionen kombiniert (pansenfreundlich)."""
        recipe = ConcentrateRecipeProfile(starch_breakdown_class="rapid")
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=True, recipe=recipe
        )
        # Primi-Basis 4,0 / 8,0 -> rapid: 3,5 / 6,5
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(3.5)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(6.5)


class TestConcentrateClassAdjustmentSlow:
    """slow-ohne-Puffer: leicht erhoeht; slow+Puffer: Premium."""

    def test_milkparlor_slow_without_buffer_plus_half(self) -> None:
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="slow", rumen_buffer_present=False
        )
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=False, recipe=recipe
        )
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(4.5)
        # slow ohne Puffer: Tagesmax leicht angehoben (+0,5)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(9.5)

    def test_transponder_slow_without_buffer(self) -> None:
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="slow", rumen_buffer_present=False
        )
        d = ro._feeding_system_defaults("PMR_stall", "transponder", recipe=recipe)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(8.5)

    def test_transponder_premium(self) -> None:
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="slow", rumen_buffer_present=True
        )
        d = ro._feeding_system_defaults("PMR_stall", "transponder", recipe=recipe)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(9.0)

    def test_ams_premium_raises(self) -> None:
        recipe = ConcentrateRecipeProfile(
            starch_breakdown_class="slow", rumen_buffer_present=True
        )
        d = ro._feeding_system_defaults("PMR_stall", "ams", recipe=recipe)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(7.0)


class TestConcentrateClassMixed:
    """mixed-Klasse: Default-Verhalten (keine Adjustierung)."""

    def test_mixed_milkparlor_keeps_standard(self) -> None:
        recipe = ConcentrateRecipeProfile(starch_breakdown_class="mixed")
        d = ro._feeding_system_defaults(
            "PMR_stall", "milkparlor", treat_as_primiparous=False, recipe=recipe
        )
        assert d["concentrate_max_per_serving_kg"] == pytest.approx(4.5)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(9.0)

    def test_mixed_transponder_keeps_standard(self) -> None:
        recipe = ConcentrateRecipeProfile(starch_breakdown_class="mixed")
        d = ro._feeding_system_defaults("PMR_stall", "transponder", recipe=recipe)
        assert d["concentrate_max_per_day_kg"] == pytest.approx(8.0)


# ---------------------------------------------------------------------------
# _resolve_feeding_system_config: Fallback-Logik
# ---------------------------------------------------------------------------

class TestResolveFeedingSystemConfigFallback:
    def test_no_config_no_profile_defaults_to_tmr(self) -> None:
        r = ro._resolve_feeding_system_config(None, None)
        assert r["system"] == "TMR"
        assert r["concentrate_distribution"] == "included_in_tmr"

    def test_fallback_from_profile_pmr_weide(self) -> None:
        r = ro._resolve_feeding_system_config(None, {"feeding_type": "PMR+Weide"})
        assert r["system"] == "PMR_pasture"
        assert r["concentrate_distribution"] == "milkparlor"

    def test_fallback_from_profile_pmr(self) -> None:
        r = ro._resolve_feeding_system_config(None, {"feeding_type": "PMR"})
        assert r["system"] == "PMR_stall"
        assert r["concentrate_distribution"] == "transponder"

    def test_fallback_from_profile_tmr(self) -> None:
        r = ro._resolve_feeding_system_config(None, {"feeding_type": "TMR"})
        assert r["system"] == "TMR"

    def test_tmr_with_pasture_feed_auto_promotes_to_pmr_pasture(self) -> None:
        feeds = [
            {
                "id": "weide_fruehjahr",
                "name": "Weide, Fruehjahr jung",
                "dm_frac": 0.18,
                "forage": True,
                "max_kg": 12.0,
            },
            {
                "id": "grassilage",
                "name": "Grassilage",
                "dm_frac": 0.35,
                "forage": True,
                "max_kg": 15.0,
            },
        ]
        r = ro._resolve_feeding_system_config(
            {"system": "TMR", "concentrate_distribution": "included_in_tmr"},
            {"feeding_type": "TMR"},
            feeds=feeds,
        )
        assert r["system"] == "PMR_pasture"
        assert r["concentrate_distribution"] == "milkparlor"
        assert r["auto_promoted_from_tmr"] is True

    def test_tmr_with_unavailable_pasture_feed_stays_tmr(self) -> None:
        feeds = [
            {
                "id": "weide_fruehjahr",
                "name": "Weide, Fruehjahr jung",
                "dm_frac": 0.18,
                "forage": True,
                "max_kg": 0.0,
            }
        ]
        r = ro._resolve_feeding_system_config(
            {"system": "TMR", "concentrate_distribution": "included_in_tmr"},
            None,
            feeds=feeds,
        )
        assert r["system"] == "TMR"
        assert r["auto_promoted_from_tmr"] is False

    def test_explicit_config_wins_over_profile(self) -> None:
        cfg = {"system": "PMR_stall", "concentrate_distribution": "ams"}
        r = ro._resolve_feeding_system_config(cfg, {"feeding_type": "PMR+Weide"})
        assert r["system"] == "PMR_stall"
        assert r["concentrate_distribution"] == "ams"

    def test_accepts_pydantic_model_directly(self) -> None:
        cfg = FeedingSystemConfig(system="PMR_pasture", concentrate_distribution="milkparlor")
        r = ro._resolve_feeding_system_config(cfg, None)
        assert r["system"] == "PMR_pasture"
        assert r["concentrate_max_per_serving_kg"] == pytest.approx(4.5)  # Default Holstein Mehrlakt

    def test_primiparous_from_profile_parity(self) -> None:
        cfg = {"system": "PMR_stall", "concentrate_distribution": "milkparlor"}
        r = ro._resolve_feeding_system_config(cfg, {"parity": 1})
        assert r["treat_as_primiparous"] is True
        assert r["concentrate_max_per_serving_kg"] == pytest.approx(4.0)

    def test_primiparous_from_is_primiparous_flag(self) -> None:
        cfg = {"system": "PMR_stall", "concentrate_distribution": "milkparlor"}
        r = ro._resolve_feeding_system_config(cfg, {"is_primiparous": True})
        assert r["treat_as_primiparous"] is True

    def test_invalid_system_defaults_to_tmr(self) -> None:
        r = ro._resolve_feeding_system_config({"system": "WhatsThis"}, None)
        assert r["system"] == "TMR"

    def test_invalid_distribution_defaults(self) -> None:
        r = ro._resolve_feeding_system_config(
            {"system": "PMR_stall", "concentrate_distribution": "bucket"}, None
        )
        assert r["concentrate_distribution"] == "included_in_tmr"


# ---------------------------------------------------------------------------
# _auto_assign_block: Feed -> Block-Zuordnung
# ---------------------------------------------------------------------------

class TestAutoAssignBlockPasture:
    def test_weide_assigned_to_pasture_block_in_pmr_pasture(self) -> None:
        feed = {"name": "Weide Fruehjahr jung", "dm_frac": 0.18, "forage": True}
        assert ro._auto_assign_block(feed, "PMR_pasture") == "pasture_block"

    def test_weide_in_tmr_system_still_goes_to_pasture_block(self) -> None:
        # Weide wird fachlich gegrast und darf nie in den Mischwagen-Block.
        # Der Runtime-Pfad eskaliert TMR+Weide zusaetzlich auf PMR_pasture.
        feed = {"name": "Weide Fruehjahr jung", "dm_frac": 0.18, "forage": True}
        assert ro._auto_assign_block(feed, "TMR") == "pasture_block"

    def test_grass_silage_is_tmr_not_pasture(self) -> None:
        # 35 % TM = Grassilage -> TMR (nicht pasture)
        feed = {"name": "Grassilage 2. Schnitt", "dm_frac": 0.35, "forage": True}
        assert ro._auto_assign_block(feed, "PMR_pasture") == "tmr_block"


class TestAutoAssignBlockConcentrate:
    def test_concentrate_in_pmr_goes_to_staged(self) -> None:
        feed = {
            "name": "MLF 18/4",
            "group": "Kraftfutter",
            "futterart": "Milchleistungsfutter",
            "forage": False,
        }
        assert ro._auto_assign_block(feed, "PMR_stall") == "concentrate_staged_block"

    def test_concentrate_in_tmr_stays_in_tmr(self) -> None:
        feed = {
            "name": "MLF 18/4",
            "group": "Kraftfutter",
            "futterart": "Milchleistungsfutter",
            "forage": False,
        }
        assert ro._auto_assign_block(feed, "TMR") == "tmr_block"

    def test_sojaextr_is_concentrate(self) -> None:
        feed = {
            "name": "Sojaextraktionsschrot",
            "group": "Konzentratfutter",
            "forage": False,
        }
        assert ro._auto_assign_block(feed, "PMR_stall") == "concentrate_staged_block"


class TestAutoAssignBlockMineral:
    def test_mineral_always_in_tmr_block(self) -> None:
        feed = {
            "name": "Weidemineral Mg/Na",
            "group": "Mineral",
            "forage": False,
        }
        for system in ("TMR", "PMR_stall", "PMR_pasture"):
            assert ro._auto_assign_block(feed, system) == "tmr_block"


class TestAutoAssignBlockForage:
    def test_maize_silage_is_tmr(self) -> None:
        feed = {"name": "Maissilage hohe OMD", "dm_frac": 0.35, "forage": True}
        assert ro._auto_assign_block(feed, "PMR_pasture") == "tmr_block"

    def test_grass_hay_is_tmr(self) -> None:
        feed = {"name": "Heu", "dm_frac": 0.87, "forage": True}
        assert ro._auto_assign_block(feed, "PMR_stall") == "tmr_block"


# ---------------------------------------------------------------------------
# _split_feeds_by_block: Volle Ration mit Overrides
# ---------------------------------------------------------------------------

class TestSplitFeedsByBlock:
    def _pmr_weide_feeds(self) -> list[dict]:
        return [
            {"id": "weide_fruehjahr", "name": "Weide Fruehjahr jung",
             "dm_frac": 0.18, "forage": True},
            {"id": "grassilage_2s", "name": "Grassilage 2. Schnitt",
             "dm_frac": 0.35, "forage": True},
            {"id": "maissilage", "name": "Maissilage",
             "dm_frac": 0.33, "forage": True},
            {"id": "weidemineral", "name": "Weidemineral Mg/Na",
             "group": "Mineral", "forage": False},
            {"id": "mlf_184", "name": "MLF 18/4",
             "group": "Kraftfutter", "futterart": "Milchleistungsfutter",
             "forage": False},
        ]

    def test_pmr_pasture_standard_split(self) -> None:
        cfg = {"system": "PMR_pasture", "concentrate_distribution": "milkparlor"}
        buckets = ro._split_feeds_by_block(self._pmr_weide_feeds(), cfg)
        assert len(buckets["pasture_block"]) == 1
        assert buckets["pasture_block"][0]["id"] == "weide_fruehjahr"
        assert {f["id"] for f in buckets["tmr_block"]} == {
            "grassilage_2s", "maissilage", "weidemineral"
        }
        assert len(buckets["concentrate_staged_block"]) == 1
        assert buckets["concentrate_staged_block"][0]["id"] == "mlf_184"

    def test_tmr_system_keeps_pasture_out_of_tmr(self) -> None:
        cfg = {"system": "TMR", "concentrate_distribution": "included_in_tmr"}
        buckets = ro._split_feeds_by_block(self._pmr_weide_feeds(), cfg)
        assert len(buckets["pasture_block"]) == 1
        assert buckets["pasture_block"][0]["id"] == "weide_fruehjahr"
        assert len(buckets["concentrate_staged_block"]) == 0
        assert len(buckets["tmr_block"]) == 4

    def test_manual_override_wins(self) -> None:
        cfg = {"system": "PMR_pasture", "concentrate_distribution": "milkparlor"}
        overrides = [{"feed_id": "mlf_184", "block": "tmr"}]
        buckets = ro._split_feeds_by_block(self._pmr_weide_feeds(), cfg, overrides)
        assert len(buckets["concentrate_staged_block"]) == 0
        assert any(f["id"] == "mlf_184" for f in buckets["tmr_block"])

    def test_override_force_weide_to_tmr(self) -> None:
        # Bsp: Weide wird abends zusaetzlich in Raufe vorgelegt
        cfg = {"system": "PMR_pasture", "concentrate_distribution": "milkparlor"}
        overrides = [{"feed_id": "weide_fruehjahr", "block": "tmr"}]
        buckets = ro._split_feeds_by_block(self._pmr_weide_feeds(), cfg, overrides)
        assert len(buckets["pasture_block"]) == 0
        assert any(f["id"] == "weide_fruehjahr" for f in buckets["tmr_block"])

    def test_invalid_override_ignored(self) -> None:
        cfg = {"system": "PMR_pasture", "concentrate_distribution": "milkparlor"}
        overrides = [{"feed_id": "weide_fruehjahr", "block": "does_not_exist"}]
        buckets = ro._split_feeds_by_block(self._pmr_weide_feeds(), cfg, overrides)
        # Fallback: automatisch -> pasture
        assert any(f["id"] == "weide_fruehjahr" for f in buckets["pasture_block"])

    def test_empty_feeds(self) -> None:
        buckets = ro._split_feeds_by_block(
            [], {"system": "PMR_pasture", "concentrate_distribution": "milkparlor"}
        )
        assert buckets == {
            "pasture_block": [],
            "tmr_block": [],
            "concentrate_staged_block": [],
        }


# ---------------------------------------------------------------------------
# Slice 1d: k_l-Logik systembewusst
# ---------------------------------------------------------------------------

class TestKlForcedAtPasture:
    """PMR+Weide: k_l fix 0,60, auch bei hoher ME-Dichte.

    Begruendung: Weide wird nicht als Mischration gefressen, sondern in
    gestaffelten Fressphasen. Eine "Gesamtrations-ME-Dichte" existiert
    physiologisch nicht; die dichteabhaengige Formel (0,463 + 0,24*q)
    darf nicht angewendet werden.
    """

    def test_high_density_is_ignored_for_pasture(self) -> None:
        # Weide 11,8 MJ ME/kg TM wuerde per Formel k_l~0,617 ergeben -
        # muss aber auf 0,60 geclippt werden bei PMR_pasture
        kl = ro._kl_milk_from_me_density(11.8, feeding_system="PMR_pasture")
        assert kl == pytest.approx(0.60)

    def test_medium_density_also_clipped_for_pasture(self) -> None:
        kl = ro._kl_milk_from_me_density(10.5, feeding_system="PMR_pasture")
        assert kl == pytest.approx(0.60)

    def test_low_density_stays_at_060(self) -> None:
        # Niedrige Dichte (<10 MJ) wuerde ohnehin 0,60 ergeben
        kl = ro._kl_milk_from_me_density(9.5, feeding_system="PMR_pasture")
        assert kl == pytest.approx(0.60)

    def test_alias_pmr_weide_also_clips(self) -> None:
        # alte Bezeichnung PMR+Weide wird auch erkannt
        kl = ro._kl_milk_from_me_density(11.5, feeding_system="PMR+Weide")
        assert kl == pytest.approx(0.60)

    def test_tmr_system_uses_density_formula(self) -> None:
        # TMR: Formel greift weiterhin
        kl_low = ro._kl_milk_from_me_density(9.0, feeding_system="TMR")
        kl_high = ro._kl_milk_from_me_density(12.0, feeding_system="TMR")
        assert kl_high > kl_low   # hoehere Dichte -> hoehere Verwertung
        assert 0.58 <= kl_low <= 0.64
        assert 0.58 <= kl_high <= 0.64

    def test_pmr_stall_uses_density_formula(self) -> None:
        kl = ro._kl_milk_from_me_density(11.0, feeding_system="PMR_stall")
        # bei 11 MJ/kg TM: q=0,598, k_l = 0,463+0,24*0,598 = 0,6063
        assert 0.58 < kl < 0.64

    def test_no_system_no_density_defaults_060(self) -> None:
        assert ro._kl_milk_from_me_density(None) == pytest.approx(0.60)


class TestMilkRequirementFactorsWithFeedingSystem:
    """Integration: _milk_requirement_factors reicht feeding_system weiter."""

    def _profile(self, feeding_type: str = "PMR+Weide") -> Dict[str, Any]:
        return {
            "body_weight_kg": 650,
            "milk_fat_pct": 4.0,
            "milk_protein_pct": 3.4,
            "feeding_type": feeding_type,
        }

    def test_pmr_weide_clips_kl_via_profile(self) -> None:
        # Hohe Dichte im Input, aber feeding_type=PMR+Weide im Profil
        # -> k_l muss auf 0,60 geclippt sein.
        me_maint, me_per_milk, _, _ = ro._milk_requirement_factors(
            self._profile("PMR+Weide"),
            me_density_mj_per_kg_tm=11.8,
        )
        # nel_per_kg_milk = 0.38*4 + 0.21*3.4 + 0.95 = 3.184
        # me_per_kg_milk = 3.184 / 0.60 = 5.307
        assert me_per_milk == pytest.approx(3.184 / 0.60, rel=1e-3)

    def test_tmr_uses_density_dependent_kl(self) -> None:
        me_maint, me_per_milk_low, _, _ = ro._milk_requirement_factors(
            self._profile("TMR"),
            me_density_mj_per_kg_tm=9.0,
        )
        me_maint, me_per_milk_high, _, _ = ro._milk_requirement_factors(
            self._profile("TMR"),
            me_density_mj_per_kg_tm=12.0,
        )
        # Hoehere Dichte -> hoehere k_l -> niedrigerer ME/kg Milch
        assert me_per_milk_high < me_per_milk_low

    def test_pasture_surcharge_still_applies(self) -> None:
        # +15 % Erhaltung bei PMR+Weide bleibt unveraendert
        me_maint_tmr, _, _, _ = ro._milk_requirement_factors(
            self._profile("TMR"), me_density_mj_per_kg_tm=11.0
        )
        me_maint_weide, _, _, _ = ro._milk_requirement_factors(
            self._profile("PMR+Weide"), me_density_mj_per_kg_tm=11.0
        )
        assert me_maint_weide == pytest.approx(me_maint_tmr * 1.15, rel=1e-3)


class TestMilkFromSupplyPastureClipping:
    """Regression: die Milch-Anzeige bei PMR+Weide wird durch k_l=0,60
    konservativer - sie darf bei hoher Rations-ME-Dichte NICHT mehr
    Milch errechnen als bei mittlerer Dichte."""

    def _profile(self) -> Dict[str, Any]:
        return {
            "body_weight_kg": 670,
            "milk_fat_pct": 4.0,
            "milk_protein_pct": 3.4,
            "feeding_type": "PMR+Weide",
        }

    def test_pasture_milk_does_not_benefit_from_density(self) -> None:
        me_sup = 254.0
        sidp_sup = 2450.0

        m_mid = ro._milk_from_supply(
            me_sup, sidp_sup, self._profile(),
            me_density_mj_per_kg_tm=10.5,
            feeding_system="PMR_pasture",
        )
        m_high = ro._milk_from_supply(
            me_sup, sidp_sup, self._profile(),
            me_density_mj_per_kg_tm=11.8,
            feeding_system="PMR_pasture",
        )
        # k_l clipped -> Milch identisch (oder minimal wegen Rundung)
        assert abs(m_mid["milk_from_energy_kg"] - m_high["milk_from_energy_kg"]) < 0.2

    def test_tmr_milk_scales_with_density(self) -> None:
        # Bei TMR ist die Dichte-Wirkung weiter aktiv
        me_sup = 254.0
        sidp_sup = 2450.0
        profile = {**self._profile(), "feeding_type": "TMR"}

        m_low = ro._milk_from_supply(
            me_sup, sidp_sup, profile,
            me_density_mj_per_kg_tm=9.5,
            feeding_system="TMR",
        )
        m_high = ro._milk_from_supply(
            me_sup, sidp_sup, profile,
            me_density_mj_per_kg_tm=11.8,
            feeding_system="TMR",
        )
        # Hoehere Dichte -> mehr Milch aus gleicher ME-Summe
        assert m_high["milk_from_energy_kg"] > m_low["milk_from_energy_kg"]
