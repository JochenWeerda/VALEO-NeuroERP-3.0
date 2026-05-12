from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException

from modules.agrar.services.settlement_calculator import (
    compute_settlement_amounts as _compute_settlement_amounts,
)


def compute_settlement_amounts(
    *,
    billing_quantity_kg: Decimal,
    unit_price_eur_per_ton: Decimal,
    deductions: list,
) -> dict[str, Decimal]:
    result = _compute_settlement_amounts(
        billing_quantity_kg=billing_quantity_kg,
        unit_price_eur_per_ton=unit_price_eur_per_ton,
        deductions=deductions,
    )
    if result["net_amount"] < Decimal("0"):
        raise HTTPException(status_code=400, detail="Deductions exceed gross amount")
    return result
