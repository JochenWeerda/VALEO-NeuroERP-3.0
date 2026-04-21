"""FAN-MODE-V1 Slice 6 (FAN-MODE-006) - Strafsatz-Konfiguration.

Spec 5.2:
  * normalisierte Strafe: penalty = base * class_weight * relaxation_factor * deviation_norm
  * drei Klassen A/B/C mit Gewichten 10 / 3 / 1
  * drei Policies strict / standard / soft mit monoton fallendem Faktor
"""
from __future__ import annotations

import pytest

from app.api.v1.endpoints.rations_optimization import (  # type: ignore
    _compute_penalty,
    _CONSTRAINT_CLASSIFICATION,
    _PENALTY_CLASS_WEIGHTS,
    _RELAXATION_FACTORS,
    _build_constraint_status_v2,
    _summarize_penalty,
)


# --- Configuration sanity ----------------------------------------------------

def test_class_weights_match_spec():
    assert _PENALTY_CLASS_WEIGHTS["A"] == 10.0
    assert _PENALTY_CLASS_WEIGHTS["B"] == 3.0
    assert _PENALTY_CLASS_WEIGHTS["C"] == 1.0


def test_relaxation_factors_are_monotone():
    # strict should penalise the most, soft the least
    assert _RELAXATION_FACTORS["strict"] > _RELAXATION_FACTORS["standard"] > _RELAXATION_FACTORS["soft"]
    assert _RELAXATION_FACTORS["standard"] == 1.0


def test_every_soft_constraint_has_a_class():
    for name, (kind, klass, unit, halfwidth, direction) in _CONSTRAINT_CLASSIFICATION.items():
        if kind == "weich":
            assert klass in ("A", "B", "C"), f"{name} missing class"
            assert halfwidth > 0, f"{name} must define halfwidth for normalisation"


# --- Penalty formula ---------------------------------------------------------

def _make_item(name, actual, target, unit=""):
    return {
        "name": name,
        "actual": actual,
        "target": target,
        "unit": unit,
        "fulfilled": False,
        "difference": actual - target,
    }


def test_deviation_norm_is_zero_when_in_corridor():
    # actual == target -> deviation_norm = 0, no penalty
    dev, pen, status = _compute_penalty(
        "peNDF (g/kg TM)", 180.0, 180.0, halfwidth=15.0, direction="min",
        relaxation_policy="standard", kind="weich", klass="B",
    )
    assert dev == 0.0
    assert pen == 0.0
    assert status == "ok"


def test_penalty_scales_linearly_with_deviation():
    # halfwidth=10, actual=target-20 (min direction) -> norm=2
    dev1, pen1, _ = _compute_penalty(
        "peNDF (g/kg TM)", 170.0, 180.0, halfwidth=10.0, direction="min",
        relaxation_policy="standard", kind="weich", klass="B",
    )
    dev2, pen2, _ = _compute_penalty(
        "peNDF (g/kg TM)", 160.0, 180.0, halfwidth=10.0, direction="min",
        relaxation_policy="standard", kind="weich", klass="B",
    )
    assert dev1 == pytest.approx(1.0, abs=1e-6)
    assert dev2 == pytest.approx(2.0, abs=1e-6)
    assert pen2 == pytest.approx(2 * pen1, rel=1e-6)


def test_class_weight_is_applied():
    args = dict(
        actual=80.0, target=100.0, halfwidth=10.0, direction="min",
        relaxation_policy="standard", kind="weich",
    )
    _, pen_A, _ = _compute_penalty("x", klass="A", **args)
    _, pen_B, _ = _compute_penalty("x", klass="B", **args)
    _, pen_C, _ = _compute_penalty("x", klass="C", **args)
    # Ratios follow the class weights exactly.
    assert pen_A == pytest.approx(10.0 * pen_C, rel=1e-6)
    assert pen_B == pytest.approx(3.0 * pen_C, rel=1e-6)


def test_relaxation_policy_scales_penalty_monotonically():
    args = dict(
        actual=80.0, target=100.0, halfwidth=10.0, direction="min",
        kind="weich", klass="B",
    )
    _, pen_strict, _ = _compute_penalty("x", relaxation_policy="strict", **args)
    _, pen_standard, _ = _compute_penalty("x", relaxation_policy="standard", **args)
    _, pen_soft, _ = _compute_penalty("x", relaxation_policy="soft", **args)
    assert pen_strict > pen_standard > pen_soft > 0.0


def test_hard_constraint_violation_reports_hard_violated():
    # halfwidth=0 and direction=min with actual<target -> hard_violated, no penalty_cost
    dev, pen, status = _compute_penalty(
        "ME (MJ/d)", 150.0, 200.0, halfwidth=0.0, direction="min",
        relaxation_policy="standard", kind="hart", klass=None,
    )
    assert status == "hard_violated"
    assert dev == 0.0
    assert pen == 0.0


def test_direction_target_penalises_both_sides():
    args = dict(
        halfwidth=1.0, direction="target",
        relaxation_policy="standard", kind="weich", klass="B",
    )
    dev_low, _, _ = _compute_penalty("x", actual=-2.0, target=0.0, **args)
    dev_high, _, _ = _compute_penalty("x", actual=2.0, target=0.0, **args)
    assert dev_low == pytest.approx(2.0)
    assert dev_high == pytest.approx(2.0)


# --- Status aggregation ------------------------------------------------------

def test_summary_splits_classes_and_counts_violations():
    report = [
        _make_item("ME (MJ/d)", 150.0, 200.0),                       # hart violated
        _make_item("peNDF (g/kg TM)", 160.0, 180.0, "g/kg TM"),      # weich B violated
        _make_item("RMD (g N/kg TM)", -3.0, 0.0, "g N/kg TM"),       # weich A violated
        _make_item("XL Rohfett (g/kg TM)", 30.0, 60.0, "g/kg TM"),   # weich C ok (direction=max, below max)
    ]
    status = _build_constraint_status_v2(report, relaxation_policy="standard")
    summary = _summarize_penalty(status)
    assert summary["hard_violations"] == 1
    assert summary["soft_violations"] >= 2
    assert summary["by_class"]["A"] > 0.0
    assert summary["by_class"]["B"] > 0.0
    assert summary["total"] == pytest.approx(
        summary["by_class"]["A"] + summary["by_class"]["B"] + summary["by_class"]["C"],
        rel=1e-6,
    )
