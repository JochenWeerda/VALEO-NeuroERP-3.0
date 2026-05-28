"""
Pricing Governance Endpoints — Wave 3 AP4
Klassifizierung von Pricing- und Marktdatenquellen.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.pricing_governance import (
    PricingSourceManifest,
    PricingGovernancePolicy,
    build_default_pricing_sources,
)
from app.domains.operations.models import PricingSourceDB

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/pricing", tags=["pricing", "governance"])


def _get_sources(tenant_id: str, db: Session) -> list[PricingSourceManifest]:
    rows = db.query(PricingSourceDB).filter(PricingSourceDB.tenant_id == tenant_id).all()
    if rows:
        return [PricingSourceManifest(**r.source_data) for r in rows]
    # Seed defaults on first access
    defaults = build_default_pricing_sources()
    for s in defaults:
        row = PricingSourceDB(
            source_id=s.source_id,
            tenant_id=tenant_id,
            source_data=s.model_dump(),
        )
        db.add(row)
    db.commit()
    return defaults


@router.get("/sources", response_model=list[PricingSourceManifest], summary="Pricing sources auflisten")
async def list_pricing_sources(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _get_sources(tenant_id, db)


@router.get("/governance", response_model=PricingGovernancePolicy, summary="Governance policy abrufen")
async def get_governance_policy(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    sources = _get_sources(tenant_id, db)
    default_source_id = None
    for s in sources:
        if s.source_type == "exchange" and s.reliability == "authoritative":
            default_source_id = s.source_id
            break
    return PricingGovernancePolicy(
        tenant_id=tenant_id,
        sources=sources,
        default_source_id=default_source_id,
        require_approval_for_manual_override=True,
    )
