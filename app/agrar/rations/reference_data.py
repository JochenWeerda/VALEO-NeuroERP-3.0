"""Canonical feeding nutrient, unit, matter-basis and rounding contracts.

The module deliberately uses ``Decimal`` throughout. FM/TM conversion differs
for quantities and concentrations and therefore requires an explicit value kind.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    ROUND_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
    Decimal,
    localcontext,
)
from enum import StrEnum


class MatterBasis(StrEnum):
    FRESH_MATTER = "fresh_matter"
    DRY_MATTER = "dry_matter"


class BasisValueKind(StrEnum):
    QUANTITY = "quantity"
    CONCENTRATION = "concentration"


class RoundingMode(StrEnum):
    HALF_UP = "half_up"
    HALF_EVEN = "half_even"
    DOWN = "down"
    UP = "up"


_ROUNDING = {
    RoundingMode.HALF_UP: ROUND_HALF_UP,
    RoundingMode.HALF_EVEN: ROUND_HALF_EVEN,
    RoundingMode.DOWN: ROUND_DOWN,
    RoundingMode.UP: ROUND_UP,
}


@dataclass(frozen=True, slots=True)
class UnitDefinition:
    code: str
    display_name: str
    dimension: str
    factor_to_base: Decimal
    precision: int

    def __post_init__(self) -> None:
        if not self.code.strip() or not self.dimension.strip():
            raise ValueError("Einheit und Dimension sind erforderlich.")
        if self.factor_to_base <= 0:
            raise ValueError("Der Einheitenfaktor muss groesser als null sein.")
        if not 0 <= self.precision <= 12:
            raise ValueError("Die Einheitenpraezision muss zwischen 0 und 12 liegen.")


def _decimal(value: Decimal | int | str) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def round_decimal(value: Decimal | int | str, precision: int,
                  mode: RoundingMode = RoundingMode.HALF_UP) -> Decimal:
    if not 0 <= precision <= 12:
        raise ValueError("Rundungspraezision muss zwischen 0 und 12 liegen.")
    quantum = Decimal(1).scaleb(-precision)
    return _decimal(value).quantize(quantum, rounding=_ROUNDING[mode])


def convert_unit(value: Decimal | int | str, from_unit: UnitDefinition,
                 to_unit: UnitDefinition,
                 mode: RoundingMode = RoundingMode.HALF_UP) -> Decimal:
    if from_unit.dimension != to_unit.dimension:
        raise ValueError(
            f"Dimension stimmt nicht ueberein: {from_unit.dimension} -> {to_unit.dimension}."
        )
    with localcontext() as context:
        context.prec = 64
        converted = _decimal(value) * from_unit.factor_to_base / to_unit.factor_to_base
    return round_decimal(converted, to_unit.precision, mode)


def convert_basis(
    value: Decimal | int | str,
    from_basis: MatterBasis,
    to_basis: MatterBasis,
    dry_matter_pct: Decimal | int | str,
    kind: BasisValueKind = BasisValueKind.QUANTITY,
) -> Decimal:
    """Convert FM/TM without implicit rounding.

    Quantities: FM -> TM multiplies with the dry-matter fraction.
    Concentrations: FM -> TM divides by it. Reverse conversion is symmetric.
    """
    amount = _decimal(value)
    dry_matter = _decimal(dry_matter_pct)
    if not Decimal("0") < dry_matter <= Decimal("100"):
        raise ValueError("Trockenmasse muss groesser 0 und hoechstens 100 Prozent sein.")
    if from_basis == to_basis:
        return amount
    with localcontext() as context:
        context.prec = 64
        fraction = dry_matter / Decimal("100")
        fm_to_dm = from_basis == MatterBasis.FRESH_MATTER
        multiply = fm_to_dm == (kind == BasisValueKind.QUANTITY)
        return amount * fraction if multiply else amount / fraction
