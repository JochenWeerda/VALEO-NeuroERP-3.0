"""Tests fuer die Best-Attainable-Recovery (RATION-CANON-04, Skill §4.2).

Ein technischer INFEASIBLE-Status darf nicht als leere fachliche Antwort
weitergegeben werden: bei positiver Wunschleistung liefert der Solver die
hoechste unter allen harten Grenzen erreichbare Ration (BEST_ATTAINABLE) mit
gefuelltem technical_max.

Solver-Lauf (mehrere Sonden pro Recovery, ~10-30 s):

    pytest tests/test_rations_best_attainable_recovery.py \
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


def test_high_target_triggers_recovery_with_real_ration():
    result = _solve(_profile(milk_kg_day=60))
    assert result.get("status") == "optimal"
    assert result.get("result_status") == "BEST_ATTAINABLE"

    rec = result.get("best_attainable_recovery")
    assert rec is not None
    assert rec["triggered"] is True
    assert rec["original_target_kg"] == 60.0
    assert 0 < rec["technical_max_kg"] < 60.0

    # Nutzbare Ration, nicht leer.
    assert len(result.get("ration_items") or []) > 0
    # Erklaerung fuer den Anwender.
    assert any("erreichbar" in w.lower() for w in result.get("warnings") or [])


def test_recovery_fills_technical_max_and_gap():
    result = _solve(_profile(milk_kg_day=60))
    att = result["attainability"]
    assert att["target"] == 60.0
    assert att["technical_max"] is not None
    assert att["safe_attainable"] is not None
    # Ziel nicht gedeckt -> positive Ziellücke, meets_target False.
    assert att["meets_target"] is False
    assert att["target_gap"] > 0
    # technical_max entspricht der hoechsten loesbaren Zielleistung.
    assert att["technical_max"] <= att["target"]


def test_recovery_keeps_original_infeasibility_diagnosis():
    result = _solve(_profile(milk_kg_day=60))
    rec = result["best_attainable_recovery"]
    # Die urspruengliche Ursache bleibt nachvollziehbar erhalten.
    assert "original_infeasibility" in rec


def test_feasible_target_does_not_trigger_recovery():
    result = _solve(_profile(milk_kg_day=32))
    assert result.get("status") == "optimal"
    assert result.get("result_status") in {"FEASIBLE_OPTIMAL", "FEASIBLE_NON_OPTIMAL"}
    # Kein Recovery-Block bei erreichbarem Ziel.
    rec = result.get("best_attainable_recovery")
    assert rec is None or rec.get("triggered") is not True
