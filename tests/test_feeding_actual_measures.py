from decimal import Decimal

import pytest

from app.agrar.rations.actual_measures import (
    DeviationPolicyError,
    calculate_iofc,
    evaluate_deviation,
    validate_thresholds,
)


def test_class_specific_threshold_yields_explainable_critical_finding() -> None:
    finding = evaluate_deviation(
        target_kg=100,
        actual_kg=113,
        warning_pct=5,
        critical_pct=10,
        feed_class="forage",
        policy_version=3,
    )
    assert finding is not None
    assert finding["severity"] == "critical"
    assert finding["delta_kg"] == Decimal("13")
    assert finding["delta_pct"] == Decimal("13.000")
    assert finding["threshold_pct"] == Decimal("10")
    assert finding["feed_class"] == "forage"
    assert finding["policy_version"] == 3


def test_value_within_class_threshold_has_no_finding() -> None:
    assert (
        evaluate_deviation(
            target_kg=100,
            actual_kg=104,
            warning_pct=5,
            critical_pct=10,
            feed_class="forage",
            policy_version=1,
        )
        is None
    )


def test_zero_target_does_not_invent_percentage_or_threshold_finding() -> None:
    assert (
        evaluate_deviation(
            target_kg=0,
            actual_kg=2,
            warning_pct=5,
            critical_pct=10,
            feed_class="mineral",
            policy_version=1,
        )
        is None
    )


@pytest.mark.parametrize("warning,critical", [(0, 10), (5, 4), (-1, 5), (5, 101)])
def test_invalid_threshold_policy_is_rejected(
    warning: object, critical: object
) -> None:
    with pytest.raises(DeviationPolicyError):
        validate_thresholds(warning, critical)


def test_iofc_requires_complete_basis_and_keeps_formula_inputs() -> None:
    assert (
        calculate_iofc(milk_kg=None, milk_price_eur_kg="0.48", feed_cost_eur="5.2")
        is None
    )
    result = calculate_iofc(milk_kg="35", milk_price_eur_kg="0.48", feed_cost_eur="5.2")
    assert result == {
        "milk_revenue_eur": Decimal("16.80"),
        "feed_cost_eur": Decimal("5.2"),
        "iofc_eur": Decimal("11.60"),
        "formula": "milk_kg * milk_price_eur_kg - feed_cost_eur",
    }
