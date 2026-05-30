"""Agribusiness Farmers Endpoint"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings

from app.api.v1.schemas.base import BaseSchema


router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class FarmerResponse(BaseModel):
    id: str
    farmerNumber: str
    firstName: str
    lastName: str
    fullName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    farmerType: str
    status: str
    portalAccessEnabled: bool
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FarmerListResponse(BaseModel):
    items: List[FarmerResponse]
    total: int


class DeleteFarmerRequest(BaseModel):
    reason: str


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/farmers", response_model=FarmerListResponse, summary="Farmers auflisten")
def list_farmers(
    db: Session = Depends(get_db),
    tenant_id: Optional[str] = None,
):
    """List all farmers for the current tenant."""
    from app.infrastructure.models.agribusiness_models import Farmer
    from sqlalchemy import text

    effective_tenant = tenant_id or DEFAULT_TENANT

    rows = (
        db.query(Farmer)
        .filter(Farmer.tenant_id == effective_tenant)
        .order_by(Farmer.last_name, Farmer.first_name)
        .all()
    )

    items = [
        FarmerResponse(
            id=r.id,
            farmerNumber=r.farmer_number,
            firstName=r.first_name,
            lastName=r.last_name,
            fullName=r.full_name,
            email=r.email,
            phone=r.phone,
            farmerType=r.farmer_type or "standard",
            status=r.status or "active",
            portalAccessEnabled=bool(r.portal_access_enabled),
            createdAt=r.created_at.isoformat() if r.created_at else None,
            updatedAt=r.updated_at.isoformat() if r.updated_at else None,
        )
        for r in rows
    ]

    return FarmerListResponse(items=items, total=len(items))


@router.delete("/farmers/{farmer_id}", status_code=204, response_class=Response, summary="Farmer löschen")
def delete_farmer(
    farmer_id: str,
    body: DeleteFarmerRequest,
    db: Session = Depends(get_db),
    tenant_id: Optional[str] = None,
):
    """Delete a farmer record. Requires a reason in the request body."""
    from app.infrastructure.models.agribusiness_models import Farmer
    import logging

    logger = logging.getLogger(__name__)
    effective_tenant = tenant_id or DEFAULT_TENANT

    farmer = (
        db.query(Farmer)
        .filter(Farmer.id == farmer_id, Farmer.tenant_id == effective_tenant)
        .first()
    )
    if farmer is None:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")

    logger.info(
        "Farmer %s (%s %s) deleted by tenant=%s. Reason: %s",
        farmer_id,
        farmer.first_name,
        farmer.last_name,
        effective_tenant,
        body.reason,
    )
    db.delete(farmer)
    db.commit()
    return Response(status_code=204)
