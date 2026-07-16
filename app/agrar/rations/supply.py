"""Pure demand, coverage and trade-unit rules for feeding plans."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_CEILING
from typing import Any


class FeedingSupplyValidationError(ValueError):
    pass


@dataclass(frozen=True)
class SupplyProjection:
    daily_demand_kg: Decimal
    horizon_days: int
    net_demand_kg: Decimal
    safety_pct: Decimal
    safety_quantity_kg: Decimal
    gross_demand_kg: Decimal
    stock_kg: Decimal | None
    reach_days: Decimal | None
    shortage_kg: Decimal | None
    trade_unit_kg: Decimal | None
    suggested_order_kg: Decimal | None
    order_rounding_delta_kg: Decimal | None
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _value(raw: Any, label: str) -> Decimal:
    try:
        value = Decimal(str(raw))
    except Exception as exc:
        raise FeedingSupplyValidationError(f"{label} ist keine gueltige Zahl.") from exc
    if not value.is_finite():
        raise FeedingSupplyValidationError(f"{label} muss endlich sein.")
    return value


def calculate_supply(
    *, daily_demand_kg: Any, horizon_days: int, safety_pct: Any,
    stock_kg: Any | None, trade_unit_kg: Any | None,
) -> SupplyProjection:
    daily = _value(daily_demand_kg, "Tagesbedarf")
    safety = _value(safety_pct, "Sicherheitszuschlag")
    if daily < 0:
        raise FeedingSupplyValidationError("Tagesbedarf darf nicht negativ sein.")
    if horizon_days < 1 or horizon_days > 365:
        raise FeedingSupplyValidationError("Bedarfshorizont muss zwischen 1 und 365 Tagen liegen.")
    if safety < 0 or safety > 100:
        raise FeedingSupplyValidationError("Sicherheitszuschlag muss zwischen 0 und 100 Prozent liegen.")
    stock = None if stock_kg is None else _value(stock_kg, "Bestand")
    if stock is not None and stock < 0:
        raise FeedingSupplyValidationError("Bestand darf nicht negativ sein.")
    trade_unit = None if trade_unit_kg is None else _value(trade_unit_kg, "Handelseinheit")
    if trade_unit is not None and trade_unit <= 0:
        raise FeedingSupplyValidationError("Handelseinheit muss groesser als null sein.")

    net = daily * Decimal(horizon_days)
    safety_quantity = net * safety / Decimal(100)
    gross = net + safety_quantity
    reach = None if stock is None or daily == 0 else stock / daily
    shortage = None if stock is None else max(Decimal(0), gross - stock)
    if shortage is None or trade_unit is None:
        suggested = rounding_delta = None
    elif shortage == 0:
        suggested = rounding_delta = Decimal(0)
    else:
        suggested = (shortage / trade_unit).to_integral_value(rounding=ROUND_CEILING) * trade_unit
        rounding_delta = suggested - shortage
    status = "unknown" if stock is None else ("critical" if shortage and shortage > 0 else "sufficient")
    return SupplyProjection(
        daily_demand_kg=daily, horizon_days=horizon_days, net_demand_kg=net,
        safety_pct=safety, safety_quantity_kg=safety_quantity,
        gross_demand_kg=gross, stock_kg=stock, reach_days=reach,
        shortage_kg=shortage, trade_unit_kg=trade_unit,
        suggested_order_kg=suggested, order_rounding_delta_kg=rounding_delta,
        status=status,
    )


def trade_unit_to_kg(packaging_unit: str | None, package_size: Any | None) -> Decimal | None:
    if package_size is None:
        return None
    size = _value(package_size, "Packungsgroesse")
    if size <= 0:
        raise FeedingSupplyValidationError("Packungsgroesse muss groesser als null sein.")
    unit = (packaging_unit or "").strip().casefold()
    if unit in {"kg", "kilogramm"}:
        return size
    if unit in {"t", "tonne", "tonnen"}:
        return size * Decimal(1000)
    return None
