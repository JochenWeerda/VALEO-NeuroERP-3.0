"""
Inventory counts endpoints (l3c-inventur)
GET/POST/PATCH/DELETE for inventory count headers and lines.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import InventoryCount, InventoryCountLine
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


# ── Schemas ──────────────────────────────────────────────────────

class InventoryCountLineOut(BaseSchema):
    id: str
    inventory_count_id: str
    article_id: str
    expected_qty: float = 0
    counted_qty: float = 0
    difference: float = 0
    batch_number: Optional[str] = None


class InventoryCountLineCreate(BaseModel):
    article_id: str
    expected_qty: float = 0
    counted_qty: float = 0
    batch_number: Optional[str] = None
    warehouse_id: Optional[str] = None
    bin_location_id: Optional[str] = None


class InventoryCountLineUpdate(BaseModel):
    counted_qty: Optional[float] = None
    expected_qty: Optional[float] = None


class InventoryCountCreate(BaseModel):
    warehouse_id: str
    notes: Optional[str] = None


class InventoryCountOut(BaseSchema):
    id: str
    warehouse_id: str
    status: str
    total_items: int = 0
    discrepancies_found: int = 0
    notes: Optional[str] = None


# ── Routes ───────────────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse[InventoryCountOut])
async def list_inventory_counts(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Inventur Übersicht"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(InventoryCount).filter(InventoryCount.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[InventoryCountOut](
        items=[InventoryCountOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/", response_model=InventoryCountOut, status_code=201)
async def create_inventory_count(
    payload: InventoryCountCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Inventur-Kopf anlegen."""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    obj = InventoryCount(
        id=uuid7(),
        warehouse_id=payload.warehouse_id,
        status="open",
        total_items=0,
        discrepancies_found=0,
        tenant_id=tid,
    )
    if hasattr(obj, 'notes') and payload.notes:
        obj.notes = payload.notes
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return InventoryCountOut.model_validate(obj)


@router.get("/{count_id}", response_model=InventoryCountOut)
async def get_inventory_count(count_id: str, db: Session = Depends(get_db)):
    """Inventur-Kopf Detail."""
    obj = db.query(InventoryCount).filter(InventoryCount.id == count_id).first()
    if not obj:
        raise HTTPException(404, "Inventory count not found")
    return InventoryCountOut.model_validate(obj)


@router.delete("/{count_id}", status_code=204)
async def delete_inventory_count(count_id: str, db: Session = Depends(get_db)):
    """Inventur-Kopf loeschen."""
    obj = db.query(InventoryCount).filter(InventoryCount.id == count_id).first()
    if not obj:
        raise HTTPException(404, "Inventory count not found")
    db.query(InventoryCountLine).filter(InventoryCountLine.inventory_count_id == count_id).delete()
    db.delete(obj)
    db.commit()


@router.get("/{count_id}/lines", response_model=list[InventoryCountLineOut])
async def get_count_lines(count_id: str, db: Session = Depends(get_db)):
    """GET Inventur Positionen"""
    lines = db.query(InventoryCountLine).filter(
        InventoryCountLine.inventory_count_id == count_id
    ).all()
    return [InventoryCountLineOut.model_validate(l) for l in lines]


@router.post("/lines", response_model=InventoryCountLineOut, status_code=201)
async def create_count_line(
    payload: InventoryCountLineCreate,
    count_id: str = Query(...),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Inventur Daten anlegen"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    line = InventoryCountLine(
        id=uuid7(),
        inventory_count_id=count_id,
        article_id=payload.article_id,
        expected_qty=payload.expected_qty,
        counted_qty=payload.counted_qty,
        difference=payload.counted_qty - payload.expected_qty,
        batch_number=payload.batch_number,
        warehouse_id=payload.warehouse_id,
        bin_location_id=payload.bin_location_id,
        tenant_id=tid,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return InventoryCountLineOut.model_validate(line)


@router.patch("/lines/{line_id}", response_model=InventoryCountLineOut)
async def update_count_line(
    line_id: str,
    payload: InventoryCountLineUpdate,
    db: Session = Depends(get_db),
):
    """PATCH Inventur Daten ändern"""
    line = db.query(InventoryCountLine).filter(InventoryCountLine.id == line_id).first()
    if not line:
        raise HTTPException(404, "Inventory count line not found")
    if payload.counted_qty is not None:
        line.counted_qty = payload.counted_qty
    if payload.expected_qty is not None:
        line.expected_qty = payload.expected_qty
    line.difference = (line.counted_qty or 0) - (line.expected_qty or 0)
    db.commit()
    db.refresh(line)
    return InventoryCountLineOut.model_validate(line)


@router.delete("/lines/{line_id}", status_code=204)
async def delete_count_line(line_id: str, db: Session = Depends(get_db)):
    """POST Inventur Daten löschen"""
    line = db.query(InventoryCountLine).filter(InventoryCountLine.id == line_id).first()
    if not line:
        raise HTTPException(404, "Inventory count line not found")
    db.delete(line)
    db.commit()
