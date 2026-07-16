from decimal import Decimal

import pytest

from app.agrar.rations.actual_feeding import (
    ActualFeedingValidationError,
    calculate_component_actual,
    calculate_value_consequences,
    validate_components,
)


def test_component_actual_keeps_absolute_and_percent_deviation() -> None:
    result = calculate_component_actual(target_kg="100", actual_kg="108.5")
    assert result.target_kg == Decimal("100")
    assert result.delta_kg == Decimal("8.5")
    assert result.delta_pct == Decimal("8.500")


def test_zero_target_has_no_invented_percentage() -> None:
    result = calculate_component_actual(target_kg=0, actual_kg=3)
    assert result.delta_kg == Decimal("3")
    assert result.delta_pct is None


@pytest.mark.parametrize("target,actual", [(-1, 0), (1, -1), ("NaN", 1)])
def test_amount_boundaries_are_rejected(target: object, actual: object) -> None:
    with pytest.raises(ActualFeedingValidationError):
        calculate_component_actual(target_kg=target, actual_kg=actual)


def test_value_consequences_keep_missing_coverage_unknown() -> None:
    result = calculate_value_consequences(
        target_kg=100, actual_kg=110, price_eur_t=None,
        nutrient_values=[{"code": "crude_protein", "value": "80", "unit": "g_per_kg", "basis": "fresh_matter"}],
    )
    assert result["cost"] is None
    assert result["missing"] == ["price"]
    assert result["nutrients"][0]["delta"] == Decimal("800")
    assert result["nutrients"][0]["result_unit"] == "g"


def test_unsupported_nutrient_unit_is_reported_not_silently_converted() -> None:
    result = calculate_value_consequences(
        target_kg=10, actual_kg=8, price_eur_t=50,
        nutrient_values=[{"code": "dry_matter", "value": 40, "unit": "percent", "basis": "fresh_matter"}],
    )
    assert result["cost"]["delta_eur"] == Decimal("-0.1")
    assert result["nutrients"] == []
    assert result["missing"] == ["nutrient:dry_matter:unsupported_unit"]


def test_component_set_rejects_duplicates_and_unknown_feeds() -> None:
    with pytest.raises(ActualFeedingValidationError, match="doppelt"):
        validate_components([{"feed_id": "a"}, {"feed_id": "a"}], {"a", "b"})
    with pytest.raises(ActualFeedingValidationError, match="nicht im Plan"):
        validate_components([{"feed_id": "x"}], {"a", "b"})
    with pytest.raises(ActualFeedingValidationError, match="fehlt"):
        validate_components([{"feed_id": "a"}], {"a", "b"})
