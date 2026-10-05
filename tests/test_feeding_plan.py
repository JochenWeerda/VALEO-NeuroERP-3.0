from decimal import Decimal

import pytest

from app.agrar.rations.feeding_plan import (
    FeedingPlanValidationError,
    build_mixing_instructions,
    round_to_dosing_step,
)
from app.core.screen_definitions import get_screen_definition


@pytest.mark.parametrize(("mode", "expected"), [
    ("nearest", Decimal("125.5")), ("up", Decimal("125.5")), ("down", Decimal("125.0")),
])
def test_dosing_rounding_is_explicit(mode: str, expected: Decimal) -> None:
    assert round_to_dosing_step(Decimal("125.25"), Decimal("0.5"), mode) == expected


def test_plan_scales_per_animal_amount_and_exposes_rounding_delta() -> None:
    instructions = build_mixing_instructions({"ration": [
        {"feed_id": "grass", "kg_fm": 12.345, "mixing_sequence": 2},
        {"feed_id": "mineral", "kg_fm": 0.157, "mixing_sequence": 1},
    ]}, animal_count=42, dosing_step_kg="0.5", rounding_mode="nearest")
    assert [item.feed_id for item in instructions] == ["mineral", "grass"]
    assert instructions[0].raw_batch_kg == Decimal("6.594")
    assert instructions[0].target_batch_kg == Decimal("6.5")
    assert instructions[0].rounding_delta_kg == Decimal("-0.094")


def test_unknown_amount_stays_unknown_instead_of_zero() -> None:
    instruction = build_mixing_instructions(
        {"ration": [{"feed_id": "unknown", "kg_fm": None}]},
        animal_count=10, dosing_step_kg="1", rounding_mode="nearest",
    )[0]
    assert instruction.kg_fm_per_animal is None
    assert instruction.raw_batch_kg is None
    assert instruction.target_batch_kg is None
    assert instruction.rounding_delta_kg is None


@pytest.mark.parametrize("payload", [
    {"animal_count": 0, "step": "1", "mode": "nearest"},
    {"animal_count": 1, "step": "0", "mode": "nearest"},
    {"animal_count": 1, "step": "1", "mode": "bankers"},
])
def test_invalid_scaling_contract_is_rejected(payload: dict) -> None:
    with pytest.raises(FeedingPlanValidationError):
        build_mixing_instructions(
            {"ration": [{"feed_id": "grass", "kg_fm": 1}]},
            animal_count=payload["animal_count"], dosing_step_kg=payload["step"],
            rounding_mode=payload["mode"],
        )


def test_feeding_plan_uses_native_meridian_object_page() -> None:
    definition = get_screen_definition("agrar/feeding-plan")
    assert definition["adapter"] == {
        "type": "native", "sourceId": "agrar/feeding-plan", "temporary": False,
    }
    assert definition["layout"]["floorplan"] == "objectPage"
    assert definition["layout"]["contextRail"] == "audit"
    assert [tab["key"] for tab in definition["tabs"]] == ["plan", "mixing", "provenance"]
    assert {action["key"] for action in definition["actions"]} == {"print_plan", "open_mobile"}
