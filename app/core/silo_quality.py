from __future__ import annotations

from decimal import Decimal
from typing import Optional


def _to_float(value: Decimal | float | int | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def weighted_quality_snapshot(lots: list[object]) -> dict[str, Optional[float]]:
    active = [
        lot
        for lot in lots
        if getattr(lot, "status", None) == "active" and _to_float(getattr(lot, "quantity_tons", None)) > 0
    ]
    if not active:
        return {
            "total_quantity_tons": 0.0,
            "moisture_avg_pct": None,
            "protein_avg_pct": None,
            "impurities_avg_pct": None,
            "hl_weight_avg": None,
            "lot_count": 0,
        }

    total = sum(_to_float(getattr(lot, "quantity_tons", None)) for lot in active)

    def _avg(field_name: str) -> Optional[float]:
        weighted_sum = 0.0
        weighted_total = 0.0
        for lot in active:
            metric = getattr(lot, field_name, None)
            if metric is None:
                continue
            qty = _to_float(getattr(lot, "quantity_tons", None))
            weighted_sum += float(metric) * qty
            weighted_total += qty
        if weighted_total <= 0:
            return None
        return round(weighted_sum / weighted_total, 2)

    return {
        "total_quantity_tons": round(total, 3),
        "moisture_avg_pct": _avg("moisture_pct"),
        "protein_avg_pct": _avg("protein_pct"),
        "impurities_avg_pct": _avg("impurities_pct"),
        "hl_weight_avg": _avg("hl_weight"),
        "lot_count": len(active),
    }
