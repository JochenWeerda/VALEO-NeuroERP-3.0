from decimal import Decimal

import pytest

from app.core.exceptions import ValidationFailedError
from app.api.v1.endpoints.agrar_settlements import (
    DeductionInput,
)
from app.services.agrar_settlement_service import AgrarSettlementService
from modules.agrar.services.settlement_calculator import calc_deduction_amount


def test_calc_deduction_per_ton():
    d = DeductionInput(deduction_type="drying", mode="per_ton", rate_per_ton_eur=2.5)
    amount = calc_deduction_amount(d, Decimal("12.500"))
    assert amount == Decimal("31.25")


def test_compute_settlement_amounts_with_deductions():
    deductions = [
        DeductionInput(deduction_type="drying", mode="per_ton", rate_per_ton_eur=4.0),
        DeductionInput(deduction_type="freight", mode="fixed", fixed_amount_eur=25.0),
    ]
    amounts = AgrarSettlementService.compute_amounts(
        billing_quantity_kg=Decimal("10000"),
        unit_price_eur_per_ton=Decimal("225.50"),
        deductions=deductions,
    )
    assert amounts["gross_amount"] == Decimal("2255.00")
    assert amounts["total_deductions"] == Decimal("65.00")
    assert amounts["net_amount"] == Decimal("2190.00")


def test_compute_settlement_rejects_negative_net():
    deductions = [DeductionInput(deduction_type="other", mode="fixed", fixed_amount_eur=9999.0)]
    with pytest.raises(ValidationFailedError):
        AgrarSettlementService.compute_amounts(
            billing_quantity_kg=Decimal("1000"),
            unit_price_eur_per_ton=Decimal("10.00"),
            deductions=deductions,
        )
