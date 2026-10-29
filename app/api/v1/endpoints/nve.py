"""
NVE / SSCC shipping-unit endpoints (l3c-nve)
GET/POST for Nummer der Versandeinheit.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import ShippingUnit
from ..schemas.base import PaginatedResponse, BaseSchema
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.tenant import get_tenant_id

router = APIRouter()


class NVEOut(BaseSchema):
    id: str
    sscc: str
    status: str = "created"
    order_id: Optional[str] = None
    delivery_note_id: Optional[str] = None
    weight: Optional[float] = None


class NVECreate(BaseModel):
    sscc: str
    order_id: Optional[str] = None
    delivery_note_id: Optional[str] = None
    weight: Optional[float] = None
    contents: Optional[list] = None


@router.get("/", response_model=PaginatedResponse[NVEOut], summary="Nves auflisten")
async def list_nves(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """GET NVE ermitteln"""
    q = db.query(ShippingUnit).filter(ShippingUnit.tenant_id == tenant_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[NVEOut](
        items=[NVEOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/", response_model=NVEOut, status_code=201, summary="Nve anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_nve(
    payload: NVECreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """POST NVE anlegen"""
    from app.core.uuid7 import uuid7
    obj = ShippingUnit(
        id=uuid7(),
        sscc=payload.sscc,
        order_id=payload.order_id,
        delivery_note_id=payload.delivery_note_id,
        weight=payload.weight,
        contents=payload.contents or [],
        tenant_id=tenant_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return NVEOut.model_validate(obj)
