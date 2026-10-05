from decimal import Decimal

import pytest

from app.agrar.rations.supply import (
    FeedingSupplyValidationError,
    calculate_supply,
    trade_unit_to_kg,
)


def test_supply_exposes_safety_and_trade_unit_rounding() -> None:
    result = calculate_supply(
        daily_demand_kg="525", horizon_days=14, safety_pct="10",
        stock_kg="5000", trade_unit_kg="1000",
    )
    assert result.net_demand_kg == Decimal("7350")
    assert result.safety_quantity_kg == Decimal("735")
    assert result.gross_demand_kg == Decimal("8085")
    assert result.shortage_kg == Decimal("3085")
    assert result.suggested_order_kg == Decimal("4000")
    assert result.order_rounding_delta_kg == Decimal("915")
    assert result.status == "critical"


def test_unknown_stock_never_becomes_zero_shortage_or_order() -> None:
    result = calculate_supply(
        daily_demand_kg=100, horizon_days=7, safety_pct=5,
        stock_kg=None, trade_unit_kg=25,
    )
    assert result.stock_kg is None
    assert result.reach_days is None
    assert result.shortage_kg is None
    assert result.suggested_order_kg is None
    assert result.status == "unknown"


@pytest.mark.parametrize(("unit", "size", "expected"), [
    ("kg", "25", Decimal("25")), ("t", "1.5", Decimal("1500")),
    ("Sack", "25", None), (None, None, None),
])
def test_trade_unit_conversion_is_explicit(unit: str | None, size: str | None,
                                           expected: Decimal | None) -> None:
    assert trade_unit_to_kg(unit, size) == expected


@pytest.mark.parametrize("patch", [
    {"horizon_days": 0}, {"safety_pct": -1}, {"safety_pct": 101},
    {"stock_kg": -1}, {"trade_unit_kg": 0},
])
def test_invalid_supply_boundaries_are_rejected(patch: dict) -> None:
    values = {"daily_demand_kg": 10, "horizon_days": 14, "safety_pct": 5,
              "stock_kg": 100, "trade_unit_kg": 25, **patch}
    with pytest.raises(FeedingSupplyValidationError):
        calculate_supply(**values)
