"""Wizard weiche Ziele (policy_overrides.wizard_soft_goals) im LP-Welfare / Stage-2-Cost."""
from __future__ import annotations

from typing import Any, Dict

from app.api.v1.endpoints.rations_optimization import (
    _feed_is_soya,
    _optimize_internal,
    _resolve_runtime_options,
    _welfare_objective_coeff,
)


def _profile_tmr(**kwargs: Any) -> Dict[str, Any]:
    p: Dict[str, Any] = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 28,
        "milk_fat_pct": 4.1,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 100,
        "parity": 2,
        "feeding_type": "TMR",
    }
    p.update(kwargs)
    return p


def test_feed_is_soya_heuristic():
    assert _feed_is_soya({"name": "Sojaschrot", "group": "Kraftfutter"})
    assert _feed_is_soya({"name": "Soybean meal", "group": "Concentrate"})
    assert not _feed_is_soya({"name": "Rapsschrot", "group": "Kraftfutter"})


def test_welfare_raises_score_for_soya_when_minimize_flag():
    feed = {
        "name": "Sojaschrot",
        "me": 13.0,
        "sidp": 260.0,
        "ndf": 120.0,
        "st": 50.0,
        "zu": 20.0,
        "bst": 20.0,
        "xl": 20.0,
        "cp": 400.0,
        "k": 15.0,
        "price": 0.55,
    }
    base = _welfare_objective_coeff(feed)
    pen = _welfare_objective_coeff(feed, wizard_soft_goals={"minimize_soya": True})
    assert pen > base


def test_welfare_prefers_homegrown_gfa():
    feed = {
        "name": "Eigenes Grasssilage",
        "id": "gfa_abc",
        "_source": "gfa",
        "me": 10.5,
        "sidp": 90.0,
        "ndf": 450.0,
        "st": 10.0,
        "zu": 5.0,
        "bst": 2.0,
        "xl": 25.0,
        "cp": 140.0,
        "k": 20.0,
        "price": 0.25,
    }
    base = _welfare_objective_coeff(feed)
    pref = _welfare_objective_coeff(feed, wizard_soft_goals={"prefer_homegrown": True})
    assert pref < base


def test_optimize_metadata_lists_active_wizard_soft_flags():
    profile = _profile_tmr()
    opts = _resolve_runtime_options(
        profile,
        policy_overrides={
            "wizard_soft_goals": {
                "minimize_soya": True,
                "prefer_homegrown": False,
            }
        },
    )
    result = _optimize_internal(profile, runtime_options=opts)
    assert result.get("status") == "optimal"
    meta = result.get("metadata") or {}
    wlp = meta.get("wizard_soft_goals_lp") or {}
    assert wlp.get("minimize_soya") is True
    assert "prefer_homegrown" not in wlp
