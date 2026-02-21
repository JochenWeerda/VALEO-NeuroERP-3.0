"""
Warehouse transfer & stock correction endpoints (l3c-lager)
Covers Lager-zu-Lager, Bestandskorrektur, Lagerhallen, Lagerfächer, Niederlassung.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import (
    WarehouseTransfer, WarehouseTransferLine,
    StockCorrection, StockCorrectionLine,
    BinLocation, Warehouse,
)
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


# ── Schemas ──────────────────────────────────────────────────────

class TransferOut(BaseSchema):
    id: str
    transfer_number: str
    from_warehouse_id: str
    to_warehouse_id: str
    status: str = "draft"
    notes: Optional[str] = None


class TransferLineOut(BaseSchema):
    id: str
    transfer_id: str
    article_id: str
    quantity: float
    batch_number: Optional[str] = None


class TransferCreate(BaseModel):
    transfer_number: str
    from_warehouse_id: str
    to_warehouse_id: str
    notes: Optional[str] = None


class TransferLineCreate(BaseModel):
    article_id: str
    quantity: float
    batch_number: Optional[str] = None


class CorrectionOut(BaseSchema):
    id: str
    correction_number: str
    warehouse_id: str
    reason: Optional[str] = None
    status: str = "draft"


class CorrectionLineOut(BaseSchema):
    id: str
    correction_id: str
    article_id: str
    old_quantity: float
    new_quantity: float
    difference: float


class CorrectionCreate(BaseModel):
    correction_number: str
    warehouse_id: str
    reason: Optional[str] = None


class CorrectionLineCreate(BaseModel):
    article_id: str
    old_quantity: float
    new_quantity: float


class BinLocationOut(BaseSchema):
    id: str
    code: str
    warehouse_id: str
    zone: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None


# ── Lager-zu-Lager ──────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse[TransferOut])
async def list_transfers(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Lager-zu-Lager Buchungen (Kopf-Daten) ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(WarehouseTransfer).filter(WarehouseTransfer.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[TransferOut](
        items=[TransferOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.get("/{transfer_id}/lines", response_model=list[TransferLineOut])
async def get_transfer_lines(transfer_id: str, db: Session = Depends(get_db)):
    """GET Lager-zu-Lager Buchungen (Positionen) ermitteln"""
    lines = db.query(WarehouseTransferLine).filter(
        WarehouseTransferLine.transfer_id == transfer_id
    ).all()
    return [TransferLineOut.model_validate(l) for l in lines]


@router.post("/", response_model=TransferOut, status_code=201)
async def create_transfer(
    payload: TransferCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Lager-zu-Lager Buchung Anlegen"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    obj = WarehouseTransfer(
        id=uuid7(),
        transfer_number=payload.transfer_number,
        from_warehouse_id=payload.from_warehouse_id,
        to_warehouse_id=payload.to_warehouse_id,
        notes=payload.notes,
        tenant_id=tid,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return TransferOut.model_validate(obj)


@router.put("/{transfer_id}", response_model=TransferOut)
async def update_transfer(
    transfer_id: str, payload: TransferCreate, db: Session = Depends(get_db),
):
    """PUT Lager-zu-Lager Buchung Bearbeiten"""
    obj = db.query(WarehouseTransfer).filter(WarehouseTransfer.id == transfer_id).first()
    if not obj:
        raise HTTPException(404, "Transfer not found")
    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    db.commit()
    db.refresh(obj)
    return TransferOut.model_validate(obj)


@router.delete("/{transfer_id}", status_code=204)
async def delete_transfer(transfer_id: str, db: Session = Depends(get_db)):
    """DEL Lager-zu-Lager Buchung Löschen"""
    obj = db.query(WarehouseTransfer).filter(WarehouseTransfer.id == transfer_id).first()
    if not obj:
        raise HTTPException(404, "Transfer not found")
    db.delete(obj)
    db.commit()


@router.post("/{transfer_id}/lines", response_model=TransferLineOut, status_code=201)
async def create_transfer_line(
    transfer_id: str,
    payload: TransferLineCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Lager-zu-Lager Buchung: Position Anlegen"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    line = WarehouseTransferLine(
        id=uuid7(),
        transfer_id=transfer_id,
        article_id=payload.article_id,
        quantity=payload.quantity,
        batch_number=payload.batch_number,
        tenant_id=tid,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return TransferLineOut.model_validate(line)


@router.put("/{transfer_id}/lines/{line_id}", response_model=TransferLineOut)
async def update_transfer_line(
    transfer_id: str, line_id: str,
    payload: TransferLineCreate, db: Session = Depends(get_db),
):
    """PUT Lager-zu-Lager Buchung: Position Bearbeiten"""
    line = db.query(WarehouseTransferLine).filter(WarehouseTransferLine.id == line_id).first()
    if not line:
        raise HTTPException(404, "Transfer line not found")
    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(line, f, v)
    db.commit()
    db.refresh(line)
    return TransferLineOut.model_validate(line)


@router.delete("/{transfer_id}/lines/{line_id}", status_code=204)
async def delete_transfer_line(
    transfer_id: str, line_id: str, db: Session = Depends(get_db),
):
    """DEL Lager-zu-Lager Buchung: Position Löschen"""
    line = db.query(WarehouseTransferLine).filter(WarehouseTransferLine.id == line_id).first()
    if not line:
        raise HTTPException(404, "Transfer line not found")
    db.delete(line)
    db.commit()


# ── Bestandskorrektur ───────────────────────────────────────────

@router.get("/corrections", response_model=PaginatedResponse[CorrectionOut])
async def list_corrections(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Bestandskorrektur (Kopf-Daten) ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(StockCorrection).filter(StockCorrection.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[CorrectionOut](
        items=[CorrectionOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.get("/corrections/{corr_id}/lines", response_model=list[CorrectionLineOut])
async def get_correction_lines(corr_id: str, db: Session = Depends(get_db)):
    """GET Bestandskorrektur Positionen ermitteln"""
    lines = db.query(StockCorrectionLine).filter(
        StockCorrectionLine.correction_id == corr_id
    ).all()
    return [CorrectionLineOut.model_validate(l) for l in lines]


@router.post("/corrections", response_model=CorrectionOut, status_code=201)
async def create_correction(
    payload: CorrectionCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Bestandskorrektur Anlegen"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    obj = StockCorrection(
        id=uuid7(),
        correction_number=payload.correction_number,
        warehouse_id=payload.warehouse_id,
        reason=payload.reason,
        tenant_id=tid,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return CorrectionOut.model_validate(obj)


@router.post("/corrections/{corr_id}/lines", response_model=CorrectionLineOut, status_code=201)
async def create_correction_line(
    corr_id: str,
    payload: CorrectionLineCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Bestandskorrektur Position Anlegen"""
    from app.core.uuid7 import uuid7
    tid = tenant_id or DEFAULT_TENANT
    line = StockCorrectionLine(
        id=uuid7(),
        correction_id=corr_id,
        article_id=payload.article_id,
        old_quantity=payload.old_quantity,
        new_quantity=payload.new_quantity,
        difference=payload.new_quantity - payload.old_quantity,
        tenant_id=tid,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return CorrectionLineOut.model_validate(line)


@router.put("/corrections/{corr_id}", response_model=CorrectionOut)
async def update_correction(
    corr_id: str, payload: CorrectionCreate, db: Session = Depends(get_db),
):
    """PUT Bestandskorrektur Bearbeiten"""
    obj = db.query(StockCorrection).filter(StockCorrection.id == corr_id).first()
    if not obj:
        raise HTTPException(404, "Correction not found")
    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    db.commit()
    db.refresh(obj)
    return CorrectionOut.model_validate(obj)


@router.delete("/corrections/{corr_id}", status_code=204)
async def delete_correction(corr_id: str, db: Session = Depends(get_db)):
    """DEL Bestandskorrektur Löschen"""
    obj = db.query(StockCorrection).filter(StockCorrection.id == corr_id).first()
    if not obj:
        raise HTTPException(404, "Correction not found")
    db.delete(obj)
    db.commit()


# ── Lagerfächer / Lagerhallen ────────────────────────────────────

@router.get("/bin-locations", response_model=list[BinLocationOut])
async def list_bin_locations(
    warehouse_id: Optional[str] = Query(None),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """GET Lagerfächer ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(BinLocation).filter(BinLocation.tenant_id == tid, BinLocation.is_active == True)  # noqa: E712
    if warehouse_id:
        q = q.filter(BinLocation.warehouse_id == warehouse_id)
    return [BinLocationOut.model_validate(b) for b in q.all()]
