"""
Preparation list endpoints (l3c-lager Rüstlisten)
GET/POST for preparation lists.
"""

from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import PreparationList, PreparationListLine
from ..schemas.base import PaginatedResponse, BaseSchema
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.tenant import get_tenant_id

router = APIRouter()


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


def _own_list(db: Session, list_id: str, tenant_id: str) -> PreparationList:
    obj = db.query(PreparationList).filter(
        PreparationList.id == list_id, PreparationList.tenant_id == tenant_id
    ).first()
    if not obj:
        raise HTTPException(404, "Preparation list not found")
    return obj


@router.get("/", response_model=PaginatedResponse[PrepListOut], summary="Preparation lists auflisten")
async def list_preparation_lists(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """GET Rüstlisten ermitteln"""
    q = db.query(PreparationList).filter(PreparationList.tenant_id == tenant_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[PrepListOut](
        items=[PrepListOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.get("/{list_id}", response_model=PrepListOut, summary="Preparation list abrufen")
async def get_preparation_list(
    list_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
):
    """GET einzelne Rüstliste"""
    obj = _own_list(db, list_id, tenant_id)
    return PrepListOut.model_validate(obj)


@router.put("/{list_id}", response_model=PrepListOut, summary="Preparation list aktualisieren", dependencies=SCHREIBEN["LAGER"])
async def update_preparation_list(
    list_id: str,
    payload: PrepListRemark,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """PUT Rüstliste aktualisieren (Notiz/Status)"""
    obj = _own_list(db, list_id, tenant_id)
    if obj.status == "processed":
        raise HTTPException(400, "Verarbeitete Rüstlisten können nicht geändert werden")
    obj.notes = payload.notes
    db.commit()
    db.refresh(obj)
    return PrepListOut.model_validate(obj)


@router.delete("/{list_id}", status_code=204, response_class=Response, response_model=None, summary="Preparation list löschen", dependencies=SCHREIBEN["LAGER"])
async def delete_preparation_list(
    list_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
):
    """DELETE Rüstliste (nur offene)"""
    obj = _own_list(db, list_id, tenant_id)
    if obj.status != "open":
        raise HTTPException(400, f"Nur offene Rüstlisten können gelöscht werden (Status: {obj.status})")
    db.delete(obj)
    db.commit()


@router.get("/{list_id}/lines", response_model=list[PrepListLineOut], summary="Prep list lines abrufen")
async def get_prep_list_lines(
    list_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
):
    """GET Rüstliste Positionen ermitteln"""
    _own_list(db, list_id, tenant_id)
    lines = db.query(PreparationListLine).filter(
        PreparationListLine.list_id == list_id, PreparationListLine.tenant_id == tenant_id
    ).all()
    return [PrepListLineOut.model_validate(line_item) for line_item in lines]


@router.post("/{list_id}/process", response_model=PrepListOut, summary="Preparation list verarbeiten", dependencies=SCHREIBEN["LAGER"])
async def process_preparation_list(
    list_id: str, payload: PrepListProcess, db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """POST Rüstliste Verarbeitet"""
    obj = _own_list(db, list_id, tenant_id)
    obj.status = payload.status
    db.commit()
    db.refresh(obj)
    return PrepListOut.model_validate(obj)


@router.post("/{list_id}/remark", response_model=PrepListOut, summary="Prep list remark hinzufügen", dependencies=SCHREIBEN["LAGER"])
async def add_prep_list_remark(
    list_id: str, payload: PrepListRemark, db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """POST Rüstliste Bemerkung"""
    obj = _own_list(db, list_id, tenant_id)
    obj.notes = payload.notes
    db.commit()
    db.refresh(obj)
    return PrepListOut.model_validate(obj)
