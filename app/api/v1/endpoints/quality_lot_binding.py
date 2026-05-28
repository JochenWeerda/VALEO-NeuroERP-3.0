"""
Quality Lot Binding Endpoints — Wave 3 AP5
Verbindet Qualitaetsprotokoll mit Charge (Partie), Preis und Freigabe.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ....core.tenant import get_tenant_id
from ....core.quality_lot_binding import (
    LotQualityProfile,
    QualityReleaseDecision,
)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/agrar/quality-lots", tags=["agrar", "quality"])

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_LOTS: dict[str, dict[str, Any]] = {}  # tenant_id → {lot_id → profile dict}
_DECISIONS: dict[str, dict[str, Any]] = {}  # tenant_id → {lot_id → decision dict}


def _lot_store(tenant_id: str) -> dict[str, Any]:
    return _LOTS.setdefault(tenant_id, {})


def _decision_store(tenant_id: str) -> dict[str, Any]:
    return _DECISIONS.setdefault(tenant_id, {})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[LotQualityProfile], summary="Lots auflisten")
async def list_lots(tenant_id: str = Depends(get_tenant_id)):
    """List all quality lot profiles for the tenant."""
    store = _lot_store(tenant_id)
    return list(store.values())


@router.post("", response_model=LotQualityProfile, status_code=201, summary="Lot anlegen")
async def create_lot(
    profile: LotQualityProfile,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a quality lot profile."""
    store = _lot_store(tenant_id)
    profile = profile.model_copy(update={"tenant_id": tenant_id})
    store[profile.lot_id] = profile.model_dump()
    return profile


@router.get("/{lot_id}", response_model=LotQualityProfile, summary="Lot abrufen")
async def get_lot(
    lot_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get a quality lot profile by ID."""
    store = _lot_store(tenant_id)
    if lot_id not in store:
        raise HTTPException(status_code=404, detail="Lot not found")
    return store[lot_id]


@router.post("/{lot_id}/release-decision", response_model=QualityReleaseDecision, status_code=201, summary="Release decision anlegen")
async def create_release_decision(
    lot_id: str,
    decision: QualityReleaseDecision,
    tenant_id: str = Depends(get_tenant_id),
):
    """Record a quality release decision for a lot."""
    store = _lot_store(tenant_id)
    if lot_id not in store:
        raise HTTPException(status_code=404, detail="Lot not found")

    decision = decision.model_copy(update={"lot_id": lot_id})
    _decision_store(tenant_id)[lot_id] = decision.model_dump()

    # Update lot approval status
    lot = store[lot_id]
    status_map = {"approve": "approved", "reject": "rejected", "hold": "pending"}
    lot["approval_status"] = status_map.get(decision.decision, "pending")
    lot["price_deduction_pct"] = decision.price_deduction_applied_pct

    return decision
