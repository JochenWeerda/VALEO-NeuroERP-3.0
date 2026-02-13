"""
Agrar moisture/shrinkage calculation domain service (AGRAR-SET-02).

Implements deterministic billing weight calculation from net weight,
moisture and impurities with configurable reference values.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


def _d(value: Decimal | float | int) -> Decimal:
    return Decimal(str(value))


def _q3(value: Decimal | float | int) -> Decimal:
    return _d(value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class MoistureEngineInput:
    net_weight_kg: Decimal
    moisture_pct: Decimal
    impurities_pct: Decimal = Decimal("0")
    target_moisture_pct: Decimal = Decimal("14.0")
    base_impurities_pct: Decimal = Decimal("2.0")
    allow_bonus: bool = False


@dataclass(frozen=True)
class MoistureEngineResult:
    net_weight_kg: Decimal
    billing_weight_kg: Decimal
    moisture_factor: Decimal
    impurities_factor: Decimal
    deduction_kg: Decimal


def _validate_percentage(name: str, value: Decimal) -> None:
    if value < Decimal("0") or value >= Decimal("100"):
        raise ValueError(f"{name} must be in [0, 100)")


def calculate_billing_weight(inp: MoistureEngineInput) -> MoistureEngineResult:
    if inp.net_weight_kg <= 0:
        raise ValueError("net_weight_kg must be > 0")

    _validate_percentage("moisture_pct", inp.moisture_pct)
    _validate_percentage("impurities_pct", inp.impurities_pct)
    _validate_percentage("target_moisture_pct", inp.target_moisture_pct)
    _validate_percentage("base_impurities_pct", inp.base_impurities_pct)

    moisture_factor = (Decimal("100") - inp.moisture_pct) / (Decimal("100") - inp.target_moisture_pct)
    impurities_factor = (Decimal("100") - inp.impurities_pct) / (Decimal("100") - inp.base_impurities_pct)

    raw_billing = inp.net_weight_kg * moisture_factor * impurities_factor
    if not inp.allow_bonus and raw_billing > inp.net_weight_kg:
        raw_billing = inp.net_weight_kg

    billing_weight = _q3(raw_billing)
    deduction = _q3(inp.net_weight_kg - billing_weight)

    return MoistureEngineResult(
        net_weight_kg=_q3(inp.net_weight_kg),
        billing_weight_kg=billing_weight,
        moisture_factor=moisture_factor.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
        impurities_factor=impurities_factor.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
        deduction_kg=deduction,
    )

