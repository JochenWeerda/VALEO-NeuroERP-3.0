"""
Pick-list endpoints (l3c-pickliste)
GET/POST for pick lists with booking, parking, and cancellation.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import PickList
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class PickListOut(BaseSchema):
    id: str
    pick_list_number: int
    status: str = "open"
    tour_id: Optional[str] = None
    order_id: Optional[str] = None
    notes: Optional[str] = None


class PickListEdit(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None


class PickListBooking(BaseModel):
    """Shared payload for booking / parking operations."""
    tour_id: Optional[str] = None
    order_id: Optional[str] = None


@router.get("/", response_model=PaginatedResponse[PickListOut], summary="Pick lists auflisten")
async def list_pick_lists(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Pickliste ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(PickList).filter(PickList.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[PickListOut](
        items=[PickListOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/{pl_id}/edit", response_model=PickListOut, summary="Pick list bearbeiten")
async def edit_pick_list(
    pl_id: str, payload: PickListEdit, db: Session = Depends(get_db),
):
    """POST Pickliste bearbeiten"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)


@router.post("/{pl_id}/cancel", response_model=PickListOut, summary="Pick list stornieren")
async def cancel_pick_list(pl_id: str, db: Session = Depends(get_db)):
    """POST Pickliste bearbeiten abbrechen"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    obj.status = "cancelled"
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)


@router.post("/{pl_id}/cancel-delete", response_model=PickListOut, summary="Delete pick list stornieren")
async def cancel_delete_pick_list(pl_id: str, db: Session = Depends(get_db)):
    """POST Pickliste bearbeiten abbrechen (Buchungen löschen)"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    obj.status = "cancelled_deleted"
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)


@router.post("/{pl_id}/book-order", response_model=PickListOut, summary="Pick list order book")
async def book_pick_list_order(
    pl_id: str, payload: PickListBooking, db: Session = Depends(get_db),
):
    """POST Pickliste buchen Auftrag / Tour"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    obj.status = "booked"
    if payload.tour_id:
        obj.tour_id = payload.tour_id
    if payload.order_id:
        obj.order_id = payload.order_id
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)


@router.post("/{pl_id}/park-order", response_model=PickListOut, summary="Pick list order park")
async def park_pick_list_order(
    pl_id: str, payload: PickListBooking, db: Session = Depends(get_db),
):
    """POST Pickliste parken Auftrag / Tour"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    obj.status = "parked"
    if payload.tour_id:
        obj.tour_id = payload.tour_id
    if payload.order_id:
        obj.order_id = payload.order_id
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)


@router.post("/{pl_id}/book-internal", response_model=PickListOut, summary="Pick list internal book")
async def book_pick_list_internal(
    pl_id: str, db: Session = Depends(get_db),
):
    """POST Pickliste buchen Interner Auftrag"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    obj.status = "booked_internal"
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)


@router.post("/{pl_id}/park-internal", response_model=PickListOut, summary="Pick list internal park")
async def park_pick_list_internal(
    pl_id: str, db: Session = Depends(get_db),
):
    """POST Pickliste parken Interner Auftrag"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    obj.status = "parked_internal"
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)


@router.post("/{pl_id}/book-free", response_model=PickListOut, summary="Pick list free book")
async def book_pick_list_free(
    pl_id: str, db: Session = Depends(get_db),
):
    """POST 'Freie' Pickliste buchen"""
    obj = db.query(PickList).filter(PickList.id == pl_id).first()
    if not obj:
        raise HTTPException(404, "Pick list not found")
    obj.status = "booked_free"
    db.commit()
    db.refresh(obj)
    return PickListOut.model_validate(obj)
