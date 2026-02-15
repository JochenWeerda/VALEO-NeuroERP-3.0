"""
Agrar settlement calculation domain service.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def round_money(value: Decimal | float | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_qty(value: Decimal | float | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def calc_deduction_amount(deduction, billing_qty_tons: Decimal) -> Decimal:
    if deduction.mode == "fixed":
        return round_money(deduction.fixed_amount_eur or 0)
    basis = round_qty(deduction.basis_quantity_tons) if deduction.basis_quantity_tons is not None else billing_qty_tons
    return round_money(Decimal(str(deduction.rate_per_ton_eur or 0)) * basis)


def compute_settlement_amounts(
    *,
    billing_quantity_kg: Decimal,
    unit_price_eur_per_ton: Decimal,
    deductions: list,
) -> dict[str, Decimal]:
    billing_qty_tons = (billing_quantity_kg / Decimal("1000")).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    gross_amount = round_money(billing_qty_tons * unit_price_eur_per_ton)
    total_deductions = round_money(sum(calc_deduction_amount(d, billing_qty_tons) for d in deductions))
    net_amount = round_money(gross_amount - total_deductions)
    return {
        "billing_qty_tons": billing_qty_tons,
        "gross_amount": gross_amount,
        "total_deductions": total_deductions,
        "net_amount": net_amount,
    }

