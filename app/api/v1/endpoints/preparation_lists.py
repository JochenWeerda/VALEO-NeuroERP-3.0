"""
Preparation list endpoints (l3c-lager Rüstlisten)
GET/POST for preparation lists.
"""

from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import PreparationList, PreparationListLine
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class PrepListOut(BaseSchema):
    id: str
    list_number: str
    status: str = "open"
    notes: Optional[str] = None
    warehouse_id: Optional[str] = None


class PrepListLineOut(BaseSchema):
    id: str
    list_id: str
    article_id: str
    required_qty: float
    picked_qty: float = 0
    bin_location_id: Optional[str] = None


class PrepListProcess(BaseModel):
    status: str = "processed"


class PrepListRemark(BaseModel):
    notes: str


@router.get("/", response_model=PaginatedResponse[PrepListOut])
async def list_preparation_lists(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Rüstlisten ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(PreparationList).filter(PreparationList.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[PrepListOut](
        items=[PrepListOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.get("/{list_id}", response_model=PrepListOut)
async def get_preparation_list(list_id: str, db: Session = Depends(get_db)):
    """GET einzelne Rüstliste"""
    obj = db.query(PreparationList).filter(PreparationList.id == list_id).first()
    if not obj:
        raise HTTPException(404, "Preparation list not found")
    return PrepListOut.model_validate(obj)


@router.put("/{list_id}", response_model=PrepListOut)
async def update_preparation_list(
    list_id: str,
    payload: PrepListRemark,
    db: Session = Depends(get_db),
):
    """PUT Rüstliste aktualisieren (Notiz/Status)"""
    obj = db.query(PreparationList).filter(PreparationList.id == list_id).first()
    if not obj:
        raise HTTPException(404, "Preparation list not found")
    if obj.status == "processed":
        raise HTTPException(400, "Verarbeitete Rüstlisten können nicht geändert werden")
    obj.notes = payload.notes
    db.commit()
    db.refresh(obj)
    return PrepListOut.model_validate(obj)


@router.delete("/{list_id}", status_code=204, response_class=Response)
async def delete_preparation_list(list_id: str, db: Session = Depends(get_db)):
    """DELETE Rüstliste (nur offene)"""
    obj = db.query(PreparationList).filter(PreparationList.id == list_id).first()
    if not obj:
        raise HTTPException(404, "Preparation list not found")
    if obj.status != "open":
        raise HTTPException(400, f"Nur offene Rüstlisten können gelöscht werden (Status: {obj.status})")
    db.delete(obj)
    db.commit()


@router.get("/{list_id}/lines", response_model=list[PrepListLineOut])
async def get_prep_list_lines(list_id: str, db: Session = Depends(get_db)):
    """GET Rüstliste Positionen ermitteln"""
    lines = db.query(PreparationListLine).filter(
        PreparationListLine.list_id == list_id
    ).all()
    return [PrepListLineOut.model_validate(line_item) for line_item in lines]


@router.post("/{list_id}/process", response_model=PrepListOut)
async def process_preparation_list(
    list_id: str, payload: PrepListProcess, db: Session = Depends(get_db),
):
    """POST Rüstliste Verarbeitet"""
    obj = db.query(PreparationList).filter(PreparationList.id == list_id).first()
    if not obj:
        raise HTTPException(404, "Preparation list not found")
    obj.status = payload.status
    db.commit()
    db.refresh(obj)
    return PrepListOut.model_validate(obj)


@router.post("/{list_id}/remark", response_model=PrepListOut)
async def add_prep_list_remark(
    list_id: str, payload: PrepListRemark, db: Session = Depends(get_db),
):
    """POST Rüstliste Bemerkung"""
    obj = db.query(PreparationList).filter(PreparationList.id == list_id).first()
    if not obj:
        raise HTTPException(404, "Preparation list not found")
    obj.notes = payload.notes
    db.commit()
    db.refresh(obj)
    return PrepListOut.model_validate(obj)
