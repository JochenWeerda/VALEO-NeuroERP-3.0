"""FAN-MODE-002 Gate-Tests: Hart/Weich-Trennung und Penalty-Scoring (Spec §5.2 + §10.1).

Diese Tests sichern die dreistufige Logik ab:
 - Harte Constraints werden bei Verletzung mit status='hard_violated' markiert.
 - Weiche Constraints liefern pro Verletzung eine positive penalty_cost gemaess
   Formel  penalty = base × class_weight × relaxation_factor × deviation_norm.
 - relaxation_policy skaliert die Penalty linear (strict ×3 / standard ×1 / soft ×0.3).
 - Die Bruder-Regression (§10.1): OHNE Mg-Supplement muss ein klarer Grund vorliegen,
   nie ein pauschales technisches 'infeasible' ohne Erklaerung.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pytest

from app.api.v1.endpoints.rations_optimization import (
    _PENALTY_CLASS_WEIGHTS,
    _RELAXATION_FACTORS,
    _build_constraint_status_v2,
    _compute_penalty,
    _optimize_internal,
    _resolve_runtime_options,
    _summarize_penalty,
)


def _brother_profile() -> Dict[str, Any]:
    return {
        "breed": "Deutsche Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 25,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 120,
        "parity": 3,
        "feeding_type": "PMR+Weide",
    }


def _find(status: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
    for row in status:
        if row["name"] == name:
            return row
    raise AssertionError(f"Constraint '{name}' fehlt im status: {[r['name'] for r in status]}")


def test_compute_penalty_normalizes_deviation_and_applies_class_weight():
    """Spec §5.2.1: deviation_norm = violation/halfwidth; penalty = base × class_weight × factor × dev."""
    dev, pen, _ = _compute_penalty(
        "aNDFomGF (g/kg TM)",
        actual=150.0, target=180.0, halfwidth=30.0, direction="min",
        relaxation_policy="standard", kind="weich", klass="B",
    )
    assert dev == pytest.approx(1.0)  # 30 g/kg Untermaß / 30 halbbreite = 1.0
    assert pen == pytest.approx(1.0 * _PENALTY_CLASS_WEIGHTS["B"] * _RELAXATION_FACTORS["standard"] * 1.0)


def test_compute_penalty_hard_constraint_has_no_penalty_but_reports_hard_violated():
    """Harte Constraints bekommen keine Penalty; Unterdeckung => status=hard_violated."""
    dev, pen, status = _compute_penalty(
        "ME (MJ/d)",
        actual=170.0, target=200.0, halfwidth=0.0, direction="min",
        relaxation_policy="standard", kind="hart", klass=None,
    )
    assert dev == 0.0
    assert pen == 0.0
    assert status == "hard_violated"


def test_relaxation_policy_scales_penalty_linearly():
    """strict verdreifacht, soft drittelt die Penalty."""
    base_inp = dict(
        actual=150.0, target=180.0, halfwidth=30.0, direction="min",
        kind="weich", klass="B",
    )
    _, pen_strict, _ = _compute_penalty("x", relaxation_policy="strict", **base_inp)
    _, pen_standard, _ = _compute_penalty("x", relaxation_policy="standard", **base_inp)
    _, pen_soft, _ = _compute_penalty("x", relaxation_policy="soft", **base_inp)
    assert pen_strict == pytest.approx(pen_standard * 3.0)
    assert pen_soft == pytest.approx(pen_standard * 0.3)


def test_penalty_only_charges_on_violation_direction():
    """Ueberdeckung bei direction=min erzeugt keine Penalty."""
    dev, pen, status = _compute_penalty(
        "aNDFomGF (g/kg TM)",
        actual=250.0, target=180.0, halfwidth=30.0, direction="min",
        relaxation_policy="standard", kind="weich", klass="B",
    )
    assert dev == 0.0
    assert pen == 0.0
    assert status == "ok"


def test_build_constraint_status_v2_classifies_hard_and_soft_entries():
    report = [
        {"name": "ME (MJ/d)", "actual": 190.0, "target": 200.0, "fulfilled": False, "unit": "MJ/d"},
        {"name": "aNDFomGF (g/kg TM)", "actual": 150.0, "target": 180.0, "fulfilled": False, "unit": "g/kg TM"},
        {"name": "Grundfutteranteil (%TM)", "actual": 60.0, "target": 55.0, "fulfilled": True, "unit": "%TM"},
    ]
    status = _build_constraint_status_v2(report, relaxation_policy="standard")
    me = _find(status, "ME (MJ/d)")
    ndfom = _find(status, "aNDFomGF (g/kg TM)")
    gf = _find(status, "Grundfutteranteil (%TM)")
    assert me["kind"] == "hart" and me["status"] == "hard_violated"
    assert ndfom["kind"] == "weich" and ndfom["class"] == "B"
    assert ndfom["penalty_cost"] > 0.0
    assert gf["kind"] == "weich" and gf["penalty_cost"] == 0.0


def test_optimize_response_contains_penalty_summary_with_class_breakdown():
    result = _optimize_internal(_brother_profile())
    assert result["status"] == "optimal"
    summary = result.get("penalty_summary")
    assert summary is not None
    assert set(summary["by_class"].keys()) == {"A", "B", "C"}
    assert summary["total"] == pytest.approx(sum(summary["by_class"].values()))
    assert summary["hard_violations"] == 0  # Bruder-Fall mit Mg-Supplement ist erfuellbar


def test_constraint_status_contains_extras_rmd_and_k_mg_ratio():
    result = _optimize_internal(_brother_profile())
    status = result["constraint_status"]
    rmd = _find(status, "RMD (g N/kg TM)")
    kmg = _find(status, "K:Mg-Ratio")
    assert rmd["kind"] == "weich" and rmd["class"] == "A"
    assert kmg["kind"] == "weich" and kmg["class"] == "A"


def test_summarize_penalty_aggregates_per_class():
    rows = [
        {"kind": "weich", "class": "A", "penalty_cost": 4.0, "status": "violated"},
        {"kind": "weich", "class": "B", "penalty_cost": 2.0, "status": "violated"},
        {"kind": "weich", "class": "C", "penalty_cost": 0.0, "status": "ok"},
        {"kind": "hart",  "class": None, "penalty_cost": 0.0, "status": "hard_violated"},
    ]
    summary = _summarize_penalty(rows)
    assert summary["total"] == pytest.approx(6.0)
    assert summary["by_class"] == {"A": 4.0, "B": 2.0, "C": 0.0}
    assert summary["soft_violations"] == 2
    assert summary["hard_violations"] == 1


# ---------------------------------------------------------------------------
# Spec §10.1 – Bruder-Regression als Abnahmekriterium
# ---------------------------------------------------------------------------

def test_brother_spring_case_without_mg_supplement_reports_clear_diagnosis_not_generic_infeasible():
    """OHNE Mg-Supplement: entweder optimal oder infeasible MIT klarer Diagnose.

    Spec §10.1: 'kein pauschales infeasible wegen PMR-/Weide-Fehlmodellierung;
    stattdessen klare Diagnose, warum die Ration scheitert, z.B. Mg/K-Risiko'.
    """
    profile = _brother_profile()
    # Nur Weide + Grassilage + Maismehl + Gerstenmehl, OHNE jede Mg-Mineralfuettermoeglichkeit:
    feeds_whitelist = ["dlg_10180010", "dlg_10100020", "dlg_30880030", "dlg_30820030"]
    # Damit nicht automatisch supplementiert wird, geben wir keinen Mg-Supplement-Feed an:
    # Allerdings fuegt _optimize_internal bei PMR+Weide das supplement automatisch hinzu.
    # Wir testen also in TMR-Modus (das erzwingt Mg aus Grundfutter/Kraftfutter).
    profile_no_supplement = {**profile, "feeding_type": "TMR"}
    result = _optimize_internal(profile_no_supplement, feed_ids=feeds_whitelist)

    # Erwartete Zustaende:
    #  - optimal: ok (Solver hat selbst Mg gefunden), oder
    #  - infeasible MIT klarer Diagnose und benanntem Grund
    if result["status"] == "optimal":
        assert result["penalty_summary"]["hard_violations"] == 0
    else:
        diag = result.get("diagnosis")
        assert diag is not None, "Ohne Mg-Supplement muss eine Diagnose vorliegen"
        assert diag["reason"] is not None
        assert diag["reason"] != "generic", (
            f"Kein pauschales generisches infeasible erlaubt (Spec §10.1): gaps={diag.get('gaps')}"
        )
        assert diag["gaps"], "Die Diagnose muss Luecken benennen"
        assert diag["suggestions"], "Die Diagnose muss Loesungsvorschlaege liefern"


def test_brother_spring_case_with_mg_supplement_is_optimal_with_no_hard_violations():
    """MIT Mg-Supplement (PMR+Weide): Solver muss optimal lsoen und keine harten Verletzungen."""
    result = _optimize_internal(_brother_profile())
    assert result["status"] == "optimal"
    assert result["penalty_summary"]["hard_violations"] == 0


def test_response_includes_objective_strategy_from_runtime_options():
    runtime = _resolve_runtime_options(_brother_profile())
    runtime["relaxation_policy"] = "strict"
    result = _optimize_internal(_brother_profile(), runtime_options=runtime)
    assert result["relaxation_policy"] == "strict"
