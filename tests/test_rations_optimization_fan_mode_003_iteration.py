"""FAN-MODE-003 Gate-Tests: FAN-Iteration, Katalog-Herkunft (exact/mapped/fallback).

Spec §8.2 + §8.4:
 - Katalog wird auf jede Futterposition angewendet, jeder Feed traegt _fan_slope_source.
 - auto_iterative liefert eine Iterationshistorie und konvergiert unter _FAN_DEFAULT_TOLERANCE.
 - reference klemmt FANi auf den Preset/Freiwert und markiert converged=True.
 - evaluation_only rechnet ohne FAN-Korrektur, markiert converged=True.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from app.api.v1.endpoints.rations_optimization import (
    _FanOptions,
    _annotate_feeds_with_fan_catalog,
    _apply_fan_effect,
    _classify_feed_to_fan_group,
    _fan1_reference_kg,
    _fani_from_result,
    _load_fan_catalog,
    _optimize_internal,
    _resolve_runtime_options,
)


def _profile(feeding_type: str = "PMR", milk: float = 28.0) -> Dict[str, Any]:
    return {
        "breed": "Deutsche Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": milk,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 120,
        "parity": 3,
        "feeding_type": feeding_type,
    }


def test_catalog_loads_with_meta_and_groups():
    catalog = _load_fan_catalog()
    assert "_meta" in catalog
    assert catalog["_meta"].get("version")
    assert "groups" in catalog
    assert "default" in catalog["groups"]


def test_feed_classification_maps_weide_to_pasture_spring():
    feed_spring = {"name": "Weide Fruehjahr jung", "futterart": "Gruenfutter", "group": "Grundfutter"}
    grp = _classify_feed_to_fan_group(feed_spring, season_profile="spring_young")
    assert grp == "roughage_pasture_spring_young"


def test_feed_classification_maps_cereal_and_protein():
    mais = {"name": "Maismehl", "futterart": "Getreide", "group": "Kraftfutter"}
    ses = {"name": "Sojaextraktionsschrot", "futterart": "Proteintraeger", "group": "Kraftfutter"}
    assert _classify_feed_to_fan_group(mais) in ("concentrate_cereal",)
    assert _classify_feed_to_fan_group(ses) in ("concentrate_protein",)


def test_annotate_sets_fan_slope_source_on_each_feed():
    feeds = [
        {"name": "Weide Fruehjahr jung", "me": 11.0, "sidp": 140.0},
        {"name": "Maismehl", "me": 13.4, "sidp": 100.0},
        {"name": "Exotisches Spezialfuttermittel XYZ", "me": 10.0, "sidp": 90.0},
    ]
    info = _annotate_feeds_with_fan_catalog(feeds, season_profile="spring_young")
    for f in feeds:
        assert f["_fan_slope_source"] in ("exact", "mapped", "fallback")
        assert "_fan_slope_me" in f
        assert "_fan_k_fan1" in f
    assert info["feeds_exact"] + info["feeds_mapped"] + info["feeds_fallback"] == 3
    assert info["version"] is not None


def test_apply_fan_effect_reduces_me_at_high_fani():
    feeds = [
        {"name": "Weide Fruehjahr jung", "me": 11.0, "sidp": 150.0},
    ]
    _annotate_feeds_with_fan_catalog(feeds, season_profile="spring_young")
    base_me = feeds[0]["me"]
    adjusted_fan3 = _apply_fan_effect(feeds, 3.0)
    # Negativer slope_me (pasture_spring_young = -0.12) => ME sinkt bei FANi > 1
    assert adjusted_fan3[0]["me"] < base_me
    # sidP erhoeht sich leicht durch k_fan1 > 0
    assert adjusted_fan3[0]["sidp"] > 150.0


def test_apply_fan_effect_is_identity_at_fan1_one():
    feeds = [
        {"name": "Maismehl", "me": 13.4, "sidp": 100.0},
    ]
    _annotate_feeds_with_fan_catalog(feeds)
    adj = _apply_fan_effect(feeds, 1.0)
    assert adj[0]["me"] == pytest.approx(13.4)
    assert adj[0]["sidp"] == pytest.approx(100.0)


def test_fan1_reference_kg_for_650_bw_is_about_6_4():
    fan1 = _fan1_reference_kg({"body_weight_kg": 650})
    assert 6.0 <= fan1 <= 7.0


def test_fani_from_result_ratio():
    fani = _fani_from_result([22.0], {"body_weight_kg": 650})
    assert 3.0 <= fani <= 4.0


def test_auto_iterative_mode_converges_and_reports_iterations():
    result = _optimize_internal(_profile("PMR"))
    assert result["status"] == "optimal"
    fan_cal = result["fan_calibration"]
    assert fan_cal["mode"] == "auto_iterative"
    assert fan_cal["converged"] is True
    assert fan_cal["iteration_count"] >= 1
    # FANi muss in einem plausiblen Bereich liegen
    assert 1.5 <= (fan_cal["fani_final"] or 0.0) <= 5.0
    # Katalog-Herkunft ist befuellt
    assert fan_cal["catalog_version"] is not None
    total = fan_cal["feeds_exact"] + fan_cal["feeds_mapped"] + fan_cal["feeds_fallback"]
    assert total > 0


def test_reference_mode_uses_preset():
    runtime = _resolve_runtime_options(
        _profile("PMR"),
        fan_options=_FanOptions(mode="reference", reference=3.0),
    )
    result = _optimize_internal(_profile("PMR"), runtime_options=runtime)
    assert result["status"] == "optimal"
    fan_cal = result["fan_calibration"]
    assert fan_cal["mode"] == "reference"
    assert fan_cal["reference"] == pytest.approx(3.0)
    assert fan_cal["fani_final"] == pytest.approx(3.0)
    assert fan_cal["converged"] is True


def test_evaluation_only_mode_does_not_adjust_coefficients():
    runtime = _resolve_runtime_options(
        _profile("PMR"),
        fan_options=_FanOptions(mode="evaluation_only"),
    )
    result = _optimize_internal(_profile("PMR"), runtime_options=runtime)
    assert result["status"] == "optimal"
    fan_cal = result["fan_calibration"]
    assert fan_cal["mode"] == "evaluation_only"
    assert fan_cal["converged"] is True


def test_ration_items_expose_fan_slope_source_from_catalog():
    result = _optimize_internal(_profile("PMR"))
    assert result["status"] == "optimal"
    sources = {item.get("fan_slope_source") for item in result["ration_items"]}
    # Es muss mindestens ein exact- oder mapped-Eintrag vorkommen, nicht alles fallback
    assert sources - {"fallback"}, f"Alle Positionen sind fallback: {sources}"
