"""Regression: Wizard-gesteuerte TM-Band- und Ziel-TM-Anbindung an _gfe_requirements."""
from __future__ import annotations

from typing import Any, Dict

import pytest

from app.api.v1.endpoints.rations_optimization import _gfe_requirements, _optimize_internal


def _base_profile(**kwargs: Any) -> Dict[str, Any]:
    p: Dict[str, Any] = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 30,
        "milk_fat_pct": 4.1,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 100,
        "parity": 2,
        "feeding_type": "TMR",
    }
    p.update(kwargs)
    return p


def test_gfe_requirements_target_dmi_kg_sets_plan():
    req = _gfe_requirements(_base_profile(target_dmi_kg=22.0))
    assert req.dmi_min_kg == pytest.approx(22.0 * 0.90)
    assert req.dmi_max_kg == pytest.approx(min(22.0 * 1.10, 28.5))
    assert req.dmi_target_kg == pytest.approx((req.dmi_min_kg + req.dmi_max_kg) / 2.0)


def test_gfe_requirements_wizard_dmi_band_overrides():
    req = _gfe_requirements(
        _base_profile(target_dmi_kg=24.0, wizard_dmi_min_kg=20.0, wizard_dmi_max_kg=21.0)
    )
    assert req.dmi_min_kg == pytest.approx(20.0)
    assert req.dmi_max_kg == pytest.approx(21.0)
    assert req.dmi_target_kg == pytest.approx(20.5)


def test_optimize_internal_smoke_with_wizard_dmi_and_target():
    result = _optimize_internal(
        _base_profile(target_dmi_kg=23.0, wizard_dmi_min_kg=22.0, wizard_dmi_max_kg=24.0)
    )
    assert result.get("status") in ("optimal", "feasible", "suboptimal")
    assert result.get("ration_items")
    dmi = float(result["nutrient_supply"]["dmi_kg"])
    assert 21.5 <= dmi <= 24.6
