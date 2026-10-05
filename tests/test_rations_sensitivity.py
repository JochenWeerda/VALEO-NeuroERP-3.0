"""Tests fuer die parametrische Sensitivitaetsanalyse (RATION-WB-07, Skill §8).

Ein Solve je Sweep-Schritt (mehrere Sekunden gesamt):

    pytest tests/test_rations_sensitivity.py \
        --noconftest -p no:cacheprovider --no-cov -o addopts=""
"""

from __future__ import annotations

from typing import Any, Dict

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.rations_optimization import (
    _SensitivityBody,
    _SensitivitySweep,
    _get_feeds,
    _run_sensitivity,
    _sensitivity_steps,
)


def _profile(**kw: Any) -> Dict[str, Any]:
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
    p.update(kw)
    return p


class TestStepAxis:
    def test_inclusive_range(self):
        assert _sensitivity_steps(1.0, 3.0, 0.5) == [1.0, 1.5, 2.0, 2.5, 3.0]

    def test_capped_at_20(self):
        steps = _sensitivity_steps(0.0, 1000.0, 1.0)
        assert len(steps) == 20

    def test_swapped_bounds_normalized(self):
        assert _sensitivity_steps(3.0, 1.0, 1.0) == [1.0, 2.0, 3.0]


class TestMilkTargetSweep:
    def test_cost_rises_with_target(self):
        body = _SensitivityBody(
            cow_profile=_profile(),
            sweep=_SensitivitySweep(parameter="milk_target", start=34, stop=40, step=2),
        )
        out = _run_sensitivity(body)
        assert out["parameter"] == "milk_target"
        assert out["unit"] == "kg Milch/Tag"
        assert [s["value"] for s in out["steps"]] == [34.0, 36.0, 38.0, 40.0]
        costs = [s["cost_eur_cow_day"] for s in out["steps"]]
        assert all(c is not None for c in costs)
        # hoehere Zielleistung ist nicht guenstiger.
        assert costs[-1] >= costs[0]

    def test_each_step_has_contract_fields(self):
        body = _SensitivityBody(
            cow_profile=_profile(),
            sweep=_SensitivitySweep(parameter="milk_target", start=34, stop=36, step=2),
        )
        out = _run_sensitivity(body)
        for s in out["steps"]:
            for key in (
                "value", "result_status", "me_density_mj_kgdm",
                "cost_eur_cow_day", "attainable_output_kg", "binding_constraints",
            ):
                assert key in s


class TestFeedSweep:
    def test_feed_max_sweep_runs(self):
        fid = _get_feeds()[0]["id"]
        body = _SensitivityBody(
            cow_profile=_profile(),
            sweep=_SensitivitySweep(
                parameter="feed_max_kg", feed_id=fid, start=2.0, stop=4.0, step=1.0
            ),
        )
        out = _run_sensitivity(body)
        assert out["feed_id"] == fid
        assert len(out["steps"]) == 3


class TestValidation:
    def test_unknown_parameter_raises_422(self):
        body = _SensitivityBody(
            cow_profile=_profile(),
            sweep=_SensitivitySweep(parameter="bogus", start=1, stop=2, step=1),
        )
        with pytest.raises(HTTPException) as exc:
            _run_sensitivity(body)
        assert exc.value.status_code == 422

    def test_feed_param_without_feed_id_raises(self):
        body = _SensitivityBody(
            cow_profile=_profile(),
            sweep=_SensitivitySweep(parameter="feed_max_kg", start=1, stop=2, step=1),
        )
        with pytest.raises(HTTPException):
            _run_sensitivity(body)
