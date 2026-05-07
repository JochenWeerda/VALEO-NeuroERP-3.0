"""Regression: dreistufige Milch-Welfare-Kosten-Pipeline im LP."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from app.api.v1.endpoints.rations_optimization import _optimize_internal, _resolve_runtime_options


def _profile_hi(**kwargs: Any) -> Dict[str, Any]:
    p: Dict[str, Any] = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 38,
        "milk_fat_pct": 4.1,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 90,
        "parity": 2,
        "feeding_type": "TMR",
    }
    p.update(kwargs)
    return p


def test_limiting_milk_respects_headroom_vs_profile():
    """Milch-Stufe zielt nach oben begrenzt auf Ist-Leistung + Headroom."""
    profile = _profile_hi()
    result = _optimize_internal(
        profile,
        runtime_options=_resolve_runtime_options(profile, objective_strategy="balance_then_cost"),
    )
    assert result.get("status") == "optimal", result.get("warnings")
    ns = result.get("nutrient_supply") or {}
    lim = float(ns.get("limiting_milk_kg") or 0.0)
    cap = float(profile["milk_kg_day"]) * 1.05 + 0.8
    assert lim <= cap, f"limiting milk {lim} soll nicht stark ueber Profil+5% ({cap}) liegen"


def test_stage2_targets_ecm_efficiency_by_default():
    profile = _profile_hi()
    result = _optimize_internal(
        profile,
        runtime_options=_resolve_runtime_options(profile, objective_strategy="balance_then_cost"),
    )
    assert result.get("status") == "optimal"
    assert result.get("feed_cost_eur_per_kg_ecm") is not None
    assert float(result["feed_cost_eur_per_kg_ecm"]) > 0
    mode = result.get("solver_stage2_lp_mode")
    assert mode in (
        "min_eur_per_kg_ecm",
        "feed_cost_eur_per_kg_ecm_relaxed",
        "min_eur_per_kg_ecm_policy",
        "feed_eur_per_day_fallback",
        "feed_eur_per_day_policy",
    )
    opts = _resolve_runtime_options(
        {"feeding_type": "TMR", "milk_kg_day": 30},
        disable_milk_tradeoff_between_stages=True,
        milk_tradeoff_max_pct_per_stage=1.0,
    )
    assert opts["disable_milk_tradeoff_between_stages"] is True
    assert opts["milk_tradeoff_max_pct_per_stage"] == pytest.approx(1.0)
