"""
Agrar weighing domain service helpers.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException

from modules.agrar.services.moisture_engine import MoistureEngineInput, calculate_billing_weight


def validate_and_compute_weights(
    gross_weight: Optional[float],
    tare_weight: Optional[float],
    net_weight: Optional[float],
) -> float | None:
    if gross_weight is not None and gross_weight < 0:
        raise HTTPException(status_code=400, detail="gross_weight must be >= 0")
    if tare_weight is not None and tare_weight < 0:
        raise HTTPException(status_code=400, detail="tare_weight must be >= 0")
    if net_weight is not None and net_weight < 0:
        raise HTTPException(status_code=400, detail="net_weight must be >= 0")

    if gross_weight is not None and tare_weight is not None:
        if gross_weight < tare_weight:
            raise HTTPException(status_code=400, detail="gross_weight must be >= tare_weight")
        computed = float(gross_weight - tare_weight)
        if net_weight is not None and abs(float(net_weight) - computed) > 0.001:
            raise HTTPException(status_code=400, detail="net_weight does not match gross_weight - tare_weight")
        return computed
    return net_weight


def resolve_ticket_allocation_quantity(ticket, requested_quantity: Optional[float]) -> Decimal:
    if requested_quantity is not None:
        quantity = Decimal(str(requested_quantity))
    elif ticket.billing_weight is not None:
        quantity = Decimal(str(ticket.billing_weight))
    elif ticket.net_weight is not None:
        quantity = Decimal(str(ticket.net_weight))
    else:
        raise HTTPException(status_code=400, detail="Ticket has no allocatable quantity")

    if quantity <= Decimal("0"):
        raise HTTPException(status_code=400, detail="Allocation quantity must be > 0")
    return quantity


def derive_billing_weight(
    *,
    net_weight: Optional[float],
    billing_weight: Optional[float],
    moisture_pct: Optional[float],
    impurities_pct: Optional[float],
    quality_data: Optional[dict[str, Any]],
) -> Optional[float]:
    if billing_weight is not None:
        return billing_weight
    if net_weight is None:
        return None
    if moisture_pct is None and impurities_pct is None:
        return None

    cfg = quality_data or {}
    result = calculate_billing_weight(
        MoistureEngineInput(
            net_weight_kg=Decimal(str(net_weight)),
            moisture_pct=Decimal(str(moisture_pct if moisture_pct is not None else 0)),
            impurities_pct=Decimal(str(impurities_pct if impurities_pct is not None else 0)),
            target_moisture_pct=Decimal(str(cfg.get("target_moisture_pct", 14.0))),
            base_impurities_pct=Decimal(str(cfg.get("base_impurities_pct", 2.0))),
            allow_bonus=bool(cfg.get("allow_bonus", False)),
        )
    )
    return float(result.billing_weight_kg)

