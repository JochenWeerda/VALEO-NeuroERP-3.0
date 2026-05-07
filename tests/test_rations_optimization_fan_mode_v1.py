"""FAN-MODE-V1 Gate-Tests fuer den additiven Daten-/Response-Vertrag (Spec §4, §5, §6, §8).

Diese Tests laufen gegen den internen Solver. Sie sichern ab, dass die zusaetzlichen
Request-Felder durchgereicht werden, die neuen Response-Felder sauber befuellt sind und
bestehende Clients ohne Aenderung weiterlaufen (§10.2).
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from app.api.v1.endpoints.rations_optimization import (
    _FAN_DEFAULT_MAX_ITERATIONS,
    _FAN_DEFAULT_TOLERANCE,
    _FAN_DEFAULT_TOLERANCE_WARN,
    _FAN_REFERENCE_PRESETS,
    _PENALTY_CLASS_WEIGHTS,
    _RELAXATION_DEFAULT,
    _RELAXATION_FACTORS,
    _FanOptions,
    _optimize_internal,
    _resolve_policy_profile,
    _resolve_runtime_options,
)


def _brother_profile(feeding_type: str = "PMR+Weide") -> Dict[str, Any]:
    return {
        "breed": "Deutsche Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 28,
        "milk_fat_pct": 4.1,
        "milk_protein_pct": 3.3,
        "lactation_stage_days": 90,
        "parity": 3,
        "feeding_type": feeding_type,
    }


def test_resolve_runtime_options_defaults_match_spec_v1():
    """Spec §11.1: fan_mode=auto_iterative, tol=0.05, warn=0.10, iter=5, policy=standard."""
    opts = _resolve_runtime_options({"feeding_type": "PMR"})
    assert opts["fan"]["mode"] == "auto_iterative"
    assert opts["fan"]["tolerance"] == pytest.approx(_FAN_DEFAULT_TOLERANCE)
    assert opts["fan"]["tolerance_warn"] == pytest.approx(_FAN_DEFAULT_TOLERANCE_WARN)
    assert opts["fan"]["max_iterations"] == _FAN_DEFAULT_MAX_ITERATIONS
    assert opts["relaxation_policy"] == _RELAXATION_DEFAULT
    assert opts["objective_strategy"] == "balance_then_cost"
    assert opts["policy_profile"] == "pmr_standard"
    assert opts["season_profile"] is None
    assert opts["disable_milk_tradeoff_between_stages"] is False
    assert opts["milk_tradeoff_max_pct_per_stage"] is None
    assert opts["stage2_minimize_feed_eur_per_day"] is False


def test_resolve_runtime_options_clamps_bad_values():
    """Schlechte Inputs werden in das zulaessige Fenster geklemmt statt einen Fehler zu werfen."""
    opts = _resolve_runtime_options(
        {"feeding_type": "TMR"},
        fan_options=_FanOptions(
            mode="unknown_mode",
            reference=99.0,
            tolerance=5.0,
            tolerance_warn=0.0,
            max_iterations=999,
        ),
        relaxation_policy="unknown_policy",
        objective_strategy="foo",
        season_profile="unknown_season",
    )
    assert opts["fan"]["mode"] == "auto_iterative"  # unknown -> Default
    assert opts["fan"]["tolerance"] <= 0.5
    assert opts["fan"]["tolerance_warn"] >= opts["fan"]["tolerance"]
    assert opts["fan"]["max_iterations"] <= 20
    assert opts["relaxation_policy"] == _RELAXATION_DEFAULT
    assert opts["objective_strategy"] == "balance_then_cost"
    assert opts["season_profile"] is None


def test_policy_profile_selection_spec_6_2():
    """Spec §6.2 + §12: TMR -> tmr_standard, PMR+Weide saisonal differenziert."""
    assert _resolve_policy_profile("TMR", None) == "tmr_standard"
    assert _resolve_policy_profile("PMR", None) == "pmr_standard"
    assert _resolve_policy_profile("PMR+Weide", None) == "pmr_standard"
    assert _resolve_policy_profile("PMR+Weide", "spring_young") == "pmr_pasture_spring"
    assert _resolve_policy_profile("PMR+Weide", "spring_mid") == "pmr_pasture_spring"
    # Spec §12 Erweiterung 2026-04-21: Sommer-/Herbst-Weide bekommen eigene Policy
    assert _resolve_policy_profile("PMR+Weide", "summer_mid") == "pmr_pasture_summer"
    assert _resolve_policy_profile("PMR+Weide", "summer_late") == "pmr_pasture_summer"
    assert _resolve_policy_profile("PMR+Weide", "autumn") == "pmr_pasture_autumn"
    assert _resolve_policy_profile("PMR+Weide", "winter") == "pmr_standard"


def test_fan_reference_presets_match_spec():
    """Spec §11.1: drei Presets 2.5 / 3.0 / 3.5."""
    assert _FAN_REFERENCE_PRESETS == (2.5, 3.0, 3.5)


def test_relaxation_factors_match_spec_5_3():
    """Spec §5.3: strict ×3 / standard ×1 / soft ×0.3."""
    assert _RELAXATION_FACTORS["strict"] == pytest.approx(3.0)
    assert _RELAXATION_FACTORS["standard"] == pytest.approx(1.0)
    assert _RELAXATION_FACTORS["soft"] == pytest.approx(0.3)


def test_penalty_class_weights_match_spec_5_2_1():
    """Spec §5.2.1: A ×10, B ×3, C ×1."""
    assert _PENALTY_CLASS_WEIGHTS == {"A": 10.0, "B": 3.0, "C": 1.0}


def test_optimize_response_contains_fan_calibration_and_active_policy_profile():
    """Slice 1: Response ist additiv erweitert; bestehende Felder bleiben vorhanden."""
    result = _optimize_internal(_brother_profile("PMR"))
    assert "fan_calibration" in result
    fan = result["fan_calibration"]
    assert fan["mode"] == "auto_iterative"
    assert fan["tolerance"] == pytest.approx(_FAN_DEFAULT_TOLERANCE)
    assert fan["max_iterations"] == _FAN_DEFAULT_MAX_ITERATIONS
    assert result["active_policy_profile"] in ("tmr_standard", "pmr_standard", "pmr_pasture_spring")
    assert result["relaxation_policy"] == "standard"
    assert result["objective_strategy"] == "balance_then_cost"
    assert "constraint_status" in result
    # bestehende Felder unveraendert sichtbar
    assert "nutrient_supply" in result
    assert "constraint_report" in result
    assert "metadata" in result
    assert result["metadata"]["optimization_strategy"] == "stage1_balance_then_stage2_cost"


def test_optimize_response_ration_items_carry_fan_slope_source():
    """Jede Rationsposition traegt das FAN-Herkunftsflag (Slice 1: 'fallback' default)."""
    result = _optimize_internal(_brother_profile("PMR"))
    assert result["status"] == "optimal"
    for item in result["ration_items"]:
        assert item.get("fan_slope_source") in ("exact", "mapped", "fallback")


def test_constraint_status_contains_hard_and_soft_entries():
    """Slice 1: constraint_status wird aus constraint_report abgeleitet, hart/weich klassifiziert."""
    result = _optimize_internal(_brother_profile("PMR"))
    status = result.get("constraint_status") or []
    assert status, "constraint_status muss befuellt sein"
    kinds = {row["kind"] for row in status}
    assert "hart" in kinds
    assert "weich" in kinds
    for row in status:
        assert row["kind"] in ("hart", "weich")
        if row["kind"] == "weich":
            assert row["class"] in ("A", "B", "C")
        if row["kind"] == "hart":
            assert row["class"] is None


def test_policy_profile_resolves_to_pmr_pasture_spring_when_season_given():
    """Policy wird aus feeding_type + season_profile abgeleitet."""
    opts = _resolve_runtime_options(
        {"feeding_type": "PMR+Weide"},
        season_profile="spring_young",
    )
    assert opts["policy_profile"] == "pmr_pasture_spring"
    assert opts["season_profile"] == "spring_young"


def test_backwards_compatibility_metadata_keeps_legacy_strategy_string():
    """Spec §10.2: bestehende Clients, die auf 'stage1_balance_then_stage2_cost' pruefen, bleiben gruen."""
    result = _optimize_internal(_brother_profile("TMR"))
    assert result["metadata"]["optimization_strategy"] == "stage1_balance_then_stage2_cost"
    # Neuer API-steuerbarer Wert parallel daneben
    assert result["metadata"]["objective_strategy"] == "balance_then_cost"
