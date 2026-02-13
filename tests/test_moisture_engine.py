import pytest
from decimal import Decimal

from modules.agrar.services.moisture_engine import (
    MoistureEngineInput,
    calculate_billing_weight,
)


def test_moisture_engine_deducts_weight_for_high_moisture():
    result = calculate_billing_weight(
        MoistureEngineInput(
            net_weight_kg=Decimal("10000"),
            moisture_pct=Decimal("18.0"),
            impurities_pct=Decimal("3.0"),
            target_moisture_pct=Decimal("14.0"),
            base_impurities_pct=Decimal("2.0"),
        )
    )
    assert result.billing_weight_kg < Decimal("10000")
    assert result.deduction_kg > Decimal("0")


def test_moisture_engine_caps_bonus_by_default():
    result = calculate_billing_weight(
        MoistureEngineInput(
            net_weight_kg=Decimal("10000"),
            moisture_pct=Decimal("12.0"),
            impurities_pct=Decimal("1.0"),
            target_moisture_pct=Decimal("14.0"),
            base_impurities_pct=Decimal("2.0"),
            allow_bonus=False,
        )
    )
    assert result.billing_weight_kg == Decimal("10000.000")
    assert result.deduction_kg == Decimal("0.000")


def test_moisture_engine_rejects_invalid_ranges():
    with pytest.raises(ValueError):
        calculate_billing_weight(
            MoistureEngineInput(
                net_weight_kg=Decimal("1000"),
                moisture_pct=Decimal("100.0"),
            )
        )
