"""
Warehouse transfer & stock correction endpoints (l3c-lager)
Covers Lager-zu-Lager, Bestandskorrektur, Lagerhallen, Lagerfaecher, Niederlassung.
"""

from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....infrastructure.models import (
    BinLocation,
    StockCorrection,
    StockCorrectionLine,
    WarehouseTransfer,
    WarehouseTransferLine,
)
from ..schemas.base import BaseSchema, PaginatedResponse

router = APIRouter()


def _get_transfer_or_404(db: Session, transfer_id: str, tenant_id: str) -> WarehouseTransfer:
    obj = (
        db.query(WarehouseTransfer)
        .filter(
            WarehouseTransfer.id == transfer_id,
            WarehouseTransfer.tenant_id == tenant_id,
        )
        .first()
    )
    if not obj:
        raise HTTPException(404, "Transfer not found")
    return obj


def _get_transfer_line_or_404(
    db: Session,
    transfer_id: str,
    line_id: str,
    tenant_id: str,
) -> WarehouseTransferLine:
    line = (
        db.query(WarehouseTransferLine)
        .filter(
            WarehouseTransferLine.id == line_id,
            WarehouseTransferLine.transfer_id == transfer_id,
            WarehouseTransferLine.tenant_id == tenant_id,
        )
        .first()
    )
    if not line:
        raise HTTPException(404, "Transfer line not found")
    return line


def _get_correction_or_404(db: Session, corr_id: str, tenant_id: str) -> StockCorrection:
    obj = (
        db.query(StockCorrection)
        .filter(
            StockCorrection.id == corr_id,
            StockCorrection.tenant_id == tenant_id,
        )
        .first()
    )
    if not obj:
        raise HTTPException(404, "Correction not found")
    return obj


def _get_correction_line_or_404(
    db: Session,
    corr_id: str,
    line_id: str,
    tenant_id: str,
) -> StockCorrectionLine:
    line = (
        db.query(StockCorrectionLine)
        .filter(
            StockCorrectionLine.id == line_id,
            StockCorrectionLine.correction_id == corr_id,
            StockCorrectionLine.tenant_id == tenant_id,
        )
        .first()
    )
    if not line:
        raise HTTPException(404, "Correction line not found")
    return line


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


@router.get("/", response_model=PaginatedResponse[TransferOut])
async def list_transfers(
    tenant_id: str = Depends(get_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(WarehouseTransfer).filter(WarehouseTransfer.tenant_id == tenant_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[TransferOut](
        items=[TransferOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{transfer_id}/lines", response_model=list[TransferLineOut])
async def get_transfer_lines(
    transfer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_transfer_or_404(db, transfer_id, tenant_id)
    lines = db.query(WarehouseTransferLine).filter(
        WarehouseTransferLine.transfer_id == transfer_id,
        WarehouseTransferLine.tenant_id == tenant_id,
    ).all()
    return [TransferLineOut.model_validate(line_item) for line_item in lines]


@router.post("/", response_model=TransferOut, status_code=201)
async def create_transfer(
    payload: TransferCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.uuid7 import uuid7

    obj = WarehouseTransfer(
        id=uuid7(),
        transfer_number=payload.transfer_number,
        from_warehouse_id=payload.from_warehouse_id,
        to_warehouse_id=payload.to_warehouse_id,
        notes=payload.notes,
        tenant_id=tenant_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return TransferOut.model_validate(obj)


@router.put("/{transfer_id}", response_model=TransferOut)
async def update_transfer(
    transfer_id: str,
    payload: TransferCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    obj = _get_transfer_or_404(db, transfer_id, tenant_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return TransferOut.model_validate(obj)


@router.post("/{transfer_id}/post", response_model=dict)
async def post_transfer(
    transfer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from datetime import date as dt_date

    from app.core.uuid7 import uuid7
    from sqlalchemy import text as sa_text

    transfer = _get_transfer_or_404(db, transfer_id, tenant_id)
    lines = db.query(WarehouseTransferLine).filter(
        WarehouseTransferLine.transfer_id == transfer_id,
        WarehouseTransferLine.tenant_id == tenant_id,
    ).all()
    if not lines:
        raise HTTPException(400, "Transfer hat keine Positionen")

    today = dt_date.today()
    movements_created = 0
    for line in lines:
        out_id = uuid7()
        in_id = uuid7()
        ref = f"UML-{transfer.transfer_number or transfer_id[:8]}"

        db.execute(
            sa_text(
                """
                INSERT INTO domain_inventory.inventory_stock_movements
                (id, article_id, warehouse_id, movement_type, quantity, unit,
                 charge, reference_number, movement_date, movement_time,
                 notes, booking_user, auto_created, ownership_type, tenant_id, created_at)
                VALUES (:id, :art, :wh, 'out', :qty, 't',
                        :batch, :ref, :date, NOW()::time,
                        :notes, 'system', true, 'owned', :tid, NOW())
                """
            ),
            {
                "id": out_id,
                "art": line.article_id,
                "wh": transfer.from_warehouse_id,
                "qty": line.quantity,
                "batch": getattr(line, "batch_number", None),
                "ref": ref,
                "date": today,
                "notes": f"Umlagerung Abgang {ref}",
                "tid": tenant_id,
            },
        )
        db.execute(
            sa_text(
                """
                INSERT INTO domain_inventory.inventory_stock_movements
                (id, article_id, warehouse_id, movement_type, quantity, unit,
                 charge, reference_number, movement_date, movement_time,
                 notes, booking_user, auto_created, ownership_type, tenant_id, created_at)
                VALUES (:id, :art, :wh, 'in', :qty, 't',
                        :batch, :ref, :date, NOW()::time,
                        :notes, 'system', true, 'owned', :tid, NOW())
                """
            ),
            {
                "id": in_id,
                "art": line.article_id,
                "wh": transfer.to_warehouse_id,
                "qty": line.quantity,
                "batch": getattr(line, "batch_number", None),
                "ref": ref,
                "date": today,
                "notes": f"Umlagerung Zugang {ref}",
                "tid": tenant_id,
            },
        )
        movements_created += 2

    if hasattr(transfer, "status"):
        transfer.status = "posted"
    db.commit()
    return {"success": True, "movements_created": movements_created, "transfer_id": transfer_id}


@router.delete("/{transfer_id}", status_code=204, response_class=Response)
async def delete_transfer(
    transfer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    obj = _get_transfer_or_404(db, transfer_id, tenant_id)
    db.delete(obj)
    db.commit()


@router.post("/{transfer_id}/lines", response_model=TransferLineOut, status_code=201)
async def create_transfer_line(
    transfer_id: str,
    payload: TransferLineCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.uuid7 import uuid7

    _get_transfer_or_404(db, transfer_id, tenant_id)
    line = WarehouseTransferLine(
        id=uuid7(),
        transfer_id=transfer_id,
        article_id=payload.article_id,
        quantity=payload.quantity,
        batch_number=payload.batch_number,
        tenant_id=tenant_id,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return TransferLineOut.model_validate(line)


@router.put("/{transfer_id}/lines/{line_id}", response_model=TransferLineOut)
async def update_transfer_line(
    transfer_id: str,
    line_id: str,
    payload: TransferLineCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_transfer_or_404(db, transfer_id, tenant_id)
    line = _get_transfer_line_or_404(db, transfer_id, line_id, tenant_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(line, field, value)
    db.commit()
    db.refresh(line)
    return TransferLineOut.model_validate(line)


@router.delete("/{transfer_id}/lines/{line_id}", status_code=204, response_class=Response)
async def delete_transfer_line(
    transfer_id: str,
    line_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_transfer_or_404(db, transfer_id, tenant_id)
    line = _get_transfer_line_or_404(db, transfer_id, line_id, tenant_id)
    db.delete(line)
    db.commit()


@router.get("/corrections", response_model=PaginatedResponse[CorrectionOut])
async def list_corrections(
    tenant_id: str = Depends(get_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(StockCorrection).filter(StockCorrection.tenant_id == tenant_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[CorrectionOut](
        items=[CorrectionOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/corrections/{corr_id}/lines", response_model=list[CorrectionLineOut])
async def get_correction_lines(
    corr_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_correction_or_404(db, corr_id, tenant_id)
    lines = db.query(StockCorrectionLine).filter(
        StockCorrectionLine.correction_id == corr_id,
        StockCorrectionLine.tenant_id == tenant_id,
    ).all()
    return [CorrectionLineOut.model_validate(line_item) for line_item in lines]


@router.post("/corrections", response_model=CorrectionOut, status_code=201)
async def create_correction(
    payload: CorrectionCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.uuid7 import uuid7

    obj = StockCorrection(
        id=uuid7(),
        correction_number=payload.correction_number,
        warehouse_id=payload.warehouse_id,
        reason=payload.reason,
        tenant_id=tenant_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return CorrectionOut.model_validate(obj)


@router.post("/corrections/{corr_id}/lines", response_model=CorrectionLineOut, status_code=201)
async def create_correction_line(
    corr_id: str,
    payload: CorrectionLineCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.uuid7 import uuid7

    _get_correction_or_404(db, corr_id, tenant_id)
    line = StockCorrectionLine(
        id=uuid7(),
        correction_id=corr_id,
        article_id=payload.article_id,
        old_quantity=payload.old_quantity,
        new_quantity=payload.new_quantity,
        difference=payload.new_quantity - payload.old_quantity,
        tenant_id=tenant_id,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return CorrectionLineOut.model_validate(line)


@router.put("/corrections/{corr_id}", response_model=CorrectionOut)
async def update_correction(
    corr_id: str,
    payload: CorrectionCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    obj = _get_correction_or_404(db, corr_id, tenant_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return CorrectionOut.model_validate(obj)


@router.delete("/corrections/{corr_id}", status_code=204, response_class=Response)
async def delete_correction(
    corr_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    obj = _get_correction_or_404(db, corr_id, tenant_id)
    db.delete(obj)
    db.commit()


@router.get("/bin-locations", response_model=list[BinLocationOut])
async def list_bin_locations(
    warehouse_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    q = db.query(BinLocation).filter(
        BinLocation.tenant_id == tenant_id,
        BinLocation.is_active == True,  # noqa: E712
    )
    if warehouse_id:
        q = q.filter(BinLocation.warehouse_id == warehouse_id)
    return [BinLocationOut.model_validate(b) for b in q.all()]
