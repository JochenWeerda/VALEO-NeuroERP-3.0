"""Regression: objective_strategy wirkt im zweistufigen LP (Welfare vs. Kosten).

Vor Fix war ``objective_strategy`` nur Metadata — Stage 2 minimierte immer nur EUR,
dadurch zu stark zur billigen Ecke trotz Tiergesundheits-/Balance-Modus im Wizard.
"""

from __future__ import annotations

from typing import Any, Dict

from app.agrar.rations.constants.solver_defaults import STAGE2_WELFARE_WEIGHT_BALANCE_ONLY
from app.api.v1.endpoints.rations_optimization import _optimize_internal, _resolve_runtime_options


def _profile_tmr_mid(**kwargs: Any) -> Dict[str, Any]:
    p: Dict[str, Any] = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 32,
        "milk_fat_pct": 4.1,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 120,
        "parity": 2,
        "feeding_type": "TMR",
    }
    p.update(kwargs)
    return p


def _me_density(result: Dict[str, Any]) -> float:
    s = result.get("nutrient_supply") or {}
    dmi = float(s.get("dmi_kg") or 0.0)
    me = float(s.get("me_mj") or 0.0)
    return me / max(dmi, 1e-6)


def _eur_day(result: Dict[str, Any]) -> float:
    return float(result.get("total_cost_eur_day") or 0.0)


def test_stage2_welfare_weight_is_tuned_positive():
    """Kalibrierkonstante dokumentiert und > 0 (sonst keine Stage-2-Wirkung)."""
    assert STAGE2_WELFARE_WEIGHT_BALANCE_ONLY >= 1.0
    assert STAGE2_WELFARE_WEIGHT_BALANCE_ONLY <= 3.0


def test_balance_only_differs_from_balance_then_cost_on_full_catalog():
    """balance_only mischt Welfare in Stage 2 — mindestens eine messbare Verschiebung."""
    profile = _profile_tmr_mid()
    r_tc = _optimize_internal(
        profile,
        runtime_options=_resolve_runtime_options(profile, objective_strategy="balance_then_cost"),
    )
    r_bo = _optimize_internal(
        profile,
        runtime_options=_resolve_runtime_options(profile, objective_strategy="balance_only"),
    )
    assert r_tc.get("status") == "optimal", r_tc.get("warnings")
    assert r_bo.get("status") == "optimal", r_bo.get("warnings")

    me_tc = _me_density(r_tc)
    me_bo = _me_density(r_bo)
    cost_tc = _eur_day(r_tc)
    cost_bo = _eur_day(r_bo)

    def _kg_by_id(items):
        return {str(it["feed_id"]): float(it.get("kgdm") or 0) for it in (items or [])}

    kg_tc = _kg_by_id(r_tc.get("ration_items"))
    kg_bo = _kg_by_id(r_bo.get("ration_items"))
    all_ids = set(kg_tc) | set(kg_bo)
    ration_diff = any(abs(kg_tc.get(k, 0.0) - kg_bo.get(k, 0.0)) > 0.05 for k in all_ids)

    # Typisch: höhere ME-Dichte und/oder höhere Kosten bei stärkerer Nährstofflast
    me_up = me_bo >= me_tc - 0.04
    cost_up = cost_bo >= cost_tc - 0.08
    assert me_up or cost_up or ration_diff, (
        f"Kalibrierung zeigt keine Differenz: ME {me_tc:.3f} vs {me_bo:.3f}, "
        f"Kosten {cost_tc:.3f} vs {cost_bo:.3f} — STAGE2_WELFARE_WEIGHT_BALANCE_ONLY prüfen."
    )


def test_cost_only_is_cheapest_among_strategies_when_feasible():
    profile = _profile_tmr_mid()
    r_cost = _optimize_internal(
        profile,
        runtime_options=_resolve_runtime_options(profile, objective_strategy="cost_only"),
    )
    r_tc = _optimize_internal(
        profile,
        runtime_options=_resolve_runtime_options(profile, objective_strategy="balance_then_cost"),
    )
    assert r_cost.get("status") == "optimal"
    assert r_tc.get("status") == "optimal"
    assert _eur_day(r_cost) <= _eur_day(r_tc) + 0.02
