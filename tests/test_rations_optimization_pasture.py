"""Tests fuer PMR+Weide-Modus der Rationsoptimierung.

Deckt die fachliche Ableitung aus DLG-Merkblatt 417 / 443 / DLG-Information 01|2023
und dem GfE-Workshop 2023 ab:

- PMR+Weide wird vom Solver als eigener Modus erkannt.
- Weidemineral Mg/Na wird automatisch als Sicherheitsbaustein in die Ration gebracht.
- Der Response enthaelt einen Weide-Risiko-Block mit K/Mg-, Rohprotein- und
  Milch-aus-Weide/Grassilage-Auswertung.
"""
from __future__ import annotations

from app.api.v1.endpoints.rations_optimization import (
    _is_pasture_pmr_system,
    _normalize_feeding_type,
    _optimize_internal,
)


def test_normalize_feeding_type_handles_aliases() -> None:
    assert _normalize_feeding_type("TMR") == "TMR"
    assert _normalize_feeding_type("tmr") == "TMR"
    assert _normalize_feeding_type("PMR") == "PMR"
    assert _normalize_feeding_type("PMR+Weide") == "PMR+Weide"
    assert _normalize_feeding_type("pmr+weide") == "PMR+Weide"
    assert _normalize_feeding_type("PMR_WEIDE") == "PMR+Weide"
    assert _normalize_feeding_type("pasture") == "PMR+Weide"
    assert _normalize_feeding_type(None) == "TMR"


def test_pasture_pmr_mode_autoactivates_via_feeding_type() -> None:
    assert _is_pasture_pmr_system([], {"feeding_type": "PMR+Weide"}) is True
    assert _is_pasture_pmr_system([], {"feeding_type": "TMR"}) is False
    assert _is_pasture_pmr_system([], {"feeding_type": "PMR"}) is False


def test_optimize_pmr_weide_adds_mg_supplement_and_pasture_risk() -> None:
    profile = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 25,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 120,
        "parity": 3,
        "feeding_type": "PMR+Weide",
    }

    result = _optimize_internal(profile)

    assert result["status"] == "optimal", result.get("warnings")
    assert result.get("metadata", {}).get("feeding_type") == "PMR+Weide"
    assert result.get("metadata", {}).get("optimization_strategy") == "stage1_balance_then_stage2_cost"

    pasture_risk = result.get("pasture_risk")
    assert pasture_risk is not None
    assert pasture_risk["active"] is True
    assert pasture_risk["feeding_type"] == "PMR+Weide"
    assert pasture_risk["pasture_dmi_kg"] >= 0.0
    assert pasture_risk["mg_supplement_dmi_kg"] >= 0.05

    ration_ids = {item["feed_id"] for item in result["ration_items"]}
    assert "special_weide_mg_mineral" in ration_ids

    milk_panel = pasture_risk["milk_from_pasture"]
    if pasture_risk["pasture_dmi_kg"] > 0:
        assert milk_panel is not None
        assert "limiting_milk_kg" in milk_panel


def test_optimize_tmr_does_not_force_mg_supplement() -> None:
    """Im reinen TMR-Modus wird das Weidemineral nicht als Pflichtbaustein erzwungen.

    Das Pasture-Risk-Panel kann dennoch erscheinen, wenn der Solver Weide-/
    Frischgrasfutter aus Kostengruenden in nennenswerter Menge einsetzt - das ist
    fachlich erwuenscht, weil die K/Mg-Warnung dann weiter gilt.
    """
    profile = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 25,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 120,
        "parity": 3,
        "feeding_type": "TMR",
    }

    result = _optimize_internal(profile)

    assert result["status"] == "optimal", result.get("warnings")
    assert result.get("metadata", {}).get("feeding_type") == "TMR"

    # Mg-Pflichtzufuhr gilt nur fuer PMR+Weide.
    ration_ids = {item["feed_id"] for item in result["ration_items"]}
    assert "special_weide_mg_mineral" not in ration_ids

    pasture_risk = result.get("pasture_risk")
    if pasture_risk and pasture_risk.get("active"):
        # Panel aktiviert sich nur wenn nennenswerte Weideaufnahme im TMR-Resultat.
        assert pasture_risk["pasture_dmi_kg"] > 1.0
