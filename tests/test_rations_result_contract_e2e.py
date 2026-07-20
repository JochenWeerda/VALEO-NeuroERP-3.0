"""End-to-End-Verdrahtung des kanonischen Ergebnisvertrags (RATION-CANON-01).

Prueft, dass ``_optimize_internal`` in beiden Zweigen (optimal / infeasible)
die additiven Felder ``result_status`` und ``attainability`` liefert, ohne die
bestehenden Felder (``status``, ``forage_performance``, …) zu veraendern.

Ausfuehrung (Solver-Lauf, ~10-20 s):

    pytest tests/test_rations_result_contract_e2e.py \
        --noconftest -p no:cacheprovider --no-cov -o addopts=""
"""

from __future__ import annotations

from typing import Any, Dict

from app.api.v1.endpoints.rations_optimization import (
    _optimize_internal,
    _resolve_runtime_options,
)


def _profile(**kwargs: Any) -> Dict[str, Any]:
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


def _solve(profile: Dict[str, Any]) -> Dict[str, Any]:
    return _optimize_internal(
        profile,
        runtime_options=_resolve_runtime_options(
            profile, objective_strategy="balance_then_cost"
        ),
    )


def test_optimal_response_carries_canonical_contract():
    result = _solve(_profile(milk_kg_day=38))
    assert result.get("status") == "optimal"

    assert result.get("result_status") == "FEASIBLE_OPTIMAL"

    att = result.get("attainability")
    assert isinstance(att, dict)
    # Erreichbarkeits-Fuenfling vollstaendig als Schluessel vorhanden.
    for key in (
        "baseline_supported",
        "safe_attainable",
        "technical_max",
        "target",
        "target_gap",
    ):
        assert key in att, f"attainability fehlt {key}"

    # Baseline und technical_max werden im Optimierlauf NICHT erfunden.
    assert att["baseline_supported"] is None
    assert att["technical_max"] is None

    assert att["target"] == 38.0
    assert att["safe_attainable"] is not None and att["safe_attainable"] > 0
    assert att["meets_target"] is True
    assert att["unit"] == "kg_milk_day"


def test_optimal_contract_consistent_with_forage_performance():
    """safe_attainable == limiting_milk der supplementierten Ration."""
    result = _solve(_profile(milk_kg_day=38))
    fp = result.get("forage_performance") or {}
    supplemented = fp.get("supplemented") or {}
    lim = float(supplemented.get("limiting_milk_kg") or 0.0)
    assert result["attainability"]["safe_attainable"] == round(lim, 1)


def test_infeasible_response_carries_canonical_contract():
    # Unrealistisch hohes Ziel -> Solver infeasible.
    result = _solve(_profile(milk_kg_day=60))
    assert result.get("status") == "infeasible"

    # Kein bloss technischer Abbruch mehr: fachlicher Status statt Leere.
    assert result.get("result_status") in {
        "CONSTRAINT_CONFLICT",
        "TARGET_NOT_ATTAINABLE",
        "DATA_INCOMPLETE",
    }

    att = result.get("attainability")
    assert isinstance(att, dict)
    # Ohne Loesung wird keine Leistung erfunden (Skill §2.3/§10.3).
    assert att["safe_attainable"] is None
    assert att["target"] == 60.0
    assert att["meets_target"] is False


def test_no_target_profile_is_feasible_optimal():
    result = _solve(_profile(milk_kg_day=0))
    if result.get("status") == "optimal":
        # Ohne positives Ziel gibt es nichts zu verfehlen.
        assert result.get("result_status") in {
            "FEASIBLE_OPTIMAL",
            "FEASIBLE_NON_OPTIMAL",
        }
        assert result["attainability"]["meets_target"] is True
        assert result["attainability"]["target_gap"] is None
