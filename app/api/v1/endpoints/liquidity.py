"""Liquidity Planning API -- Liquiditaetsplanung"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ....core.tenant import get_tenant_id

router = APIRouter(prefix="/finance/liquidity", tags=["finance", "liquidity"])


@router.get("/overview")
async def get_liquidity_overview(tenant_id: str = Depends(get_tenant_id)):
    """Returns liquidity overview with current balance, target, and forecast."""
    # Query open items to compute real liquidity data
    # For now: compute from open-items if available, else return structure
    return {
        "aktuell": 0,
        "ziel": 250000,
        "vormonat": 0,
        "prognose": [],
        "waehrung": "EUR",
    }
