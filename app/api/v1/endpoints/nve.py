"""
NVE / SSCC shipping-unit endpoints (l3c-nve)
GET/POST for Nummer der Versandeinheit.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import ShippingUnit
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


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


@router.get("/", response_model=PaginatedResponse[NVEOut])
async def list_nves(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET NVE ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(ShippingUnit).filter(ShippingUnit.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[NVEOut](
        items=[NVEOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/", response_model=NVEOut, status_code=201)
async def create_nve(
    payload: NVECreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST NVE anlegen"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    obj = ShippingUnit(
        id=uuid7(),
        sscc=payload.sscc,
        order_id=payload.order_id,
        delivery_note_id=payload.delivery_note_id,
        weight=payload.weight,
        contents=payload.contents or [],
        tenant_id=tid,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return NVEOut.model_validate(obj)
