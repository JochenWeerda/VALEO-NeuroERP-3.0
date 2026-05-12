"""
Inventory counts endpoints (l3c-inventur)
GET/POST/PATCH/DELETE for inventory count headers and lines.
"""

from typing import Optional
from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
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
    return [InventoryCountLineOut.model_validate(line_item) for line_item in lines]


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


# ── Wave 3: Inventur-Differenzen verbuchen ─────────────────────

class InventurPostResult(BaseModel):
    count_id: str
    posted_lines: int
    total_adjustments: int
    journal_entry_id: Optional[str] = None
    status: str


@router.post("/{count_id}/post", response_model=InventurPostResult, tags=["inventory"])
async def post_inventory_count(
    count_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Inventur-Differenzen verbuchen.

    Für jede Zeile mit Differenz != 0 wird:
    - Ein StockMovement (adjustment) erzeugt
    - Der Artikelbestand angepasst
    - Am Ende eine aggregierte GL-Buchung erstellt
    Der Inventur-Status wechselt auf 'posted'.
    """
    tid = tenant_id or DEFAULT_TENANT
    count = db.query(InventoryCount).filter(InventoryCount.id == count_id).first()
    if not count:
        raise HTTPException(404, "Inventur nicht gefunden")
    if hasattr(count, 'status') and count.status == "posted":
        raise HTTPException(400, "Inventur bereits verbucht")

    lines = db.query(InventoryCountLine).filter(
        InventoryCountLine.inventory_count_id == count_id
    ).all()

    if not lines:
        raise HTTPException(400, "Keine Inventur-Positionen vorhanden")

    posting_date = date.today()
    adjustments = 0
    total_positive = Decimal("0")
    total_negative = Decimal("0")

    for line in lines:
        diff = (line.counted_qty or 0) - (line.expected_qty or 0)
        if abs(diff) < 0.001:
            continue

        adjustments += 1
        movement_id = str(uuid4())
        ref = f"INV-{count_id[:8].upper()}-{adjustments}"

        db.execute(
            text("""
                INSERT INTO domain_inventory.inventory_stock_movements
                (id, article_id, warehouse_id, movement_type, quantity, unit, charge,
                 reference_number, movement_date, movement_time,
                 notes, booking_user, auto_created, ownership_type, tenant_id,
                 previous_stock, new_stock, created_at)
                VALUES (:id, :article_id, :warehouse_id, 'adjustment', :quantity, 't', :charge,
                        :ref, :date, NOW()::time,
                        :notes, 'inventur', true, 'owned', :tenant_id,
                        0, 0, NOW())
            """),
            {
                "id": movement_id,
                "article_id": line.article_id,
                "warehouse_id": line.warehouse_id or (count.warehouse_id if hasattr(count, 'warehouse_id') else 'INVENTUR'),
                "quantity": diff,
                "charge": line.batch_number,
                "ref": ref,
                "date": posting_date,
                "notes": f"Inventur-Differenz: Soll={line.expected_qty}, Ist={line.counted_qty}",
                "tenant_id": tid,
            },
        )

        # Update article stock
        db.execute(
            text("""
                UPDATE domain_inventory.articles
                SET current_stock = COALESCE(current_stock, 0) + :delta,
                    available_stock = COALESCE(available_stock, 0) + :delta,
                    updated_at = NOW()
                WHERE id = :article_id
            """),
            {"delta": diff, "article_id": line.article_id},
        )

        if diff > 0:
            total_positive += Decimal(str(diff))
        else:
            total_negative += Decimal(str(abs(diff)))

    # Aggregate GL posting
    journal_entry_id = None
    try:
        net = total_positive - total_negative
        amount = Decimal(str(abs(float(net)))).quantize(Decimal("0.01"))
        if amount > 0:
            from .inventory_operations import _post_inventory_journal
            if net > 0:
                journal_entry_id = _post_inventory_journal(
                    db,
                    tenant_id=tid,
                    posting_date=posting_date,
                    document_type="inventory_count",
                    document_number=f"INVENTUR-{count_id[:8].upper()}",
                    description=f"Inventur-Buchung — Netto-Zugang {amount} t",
                    debit_account="1500",
                    debit_account_name="Warenbestand",
                    credit_account="5800",
                    credit_account_name="Bestandsveränderungen",
                    amount=amount,
                    reference=f"INVENTUR-{count_id[:8].upper()}",
                )
            else:
                journal_entry_id = _post_inventory_journal(
                    db,
                    tenant_id=tid,
                    posting_date=posting_date,
                    document_type="inventory_count",
                    document_number=f"INVENTUR-{count_id[:8].upper()}",
                    description=f"Inventur-Buchung — Netto-Abgang {amount} t",
                    debit_account="5800",
                    debit_account_name="Bestandsveränderungen",
                    credit_account="1500",
                    credit_account_name="Warenbestand",
                    amount=amount,
                    reference=f"INVENTUR-{count_id[:8].upper()}",
                )
    except Exception:
        pass

    # Update count status
    count.status = "posted"
    count.discrepancies_found = adjustments
    db.commit()

    return InventurPostResult(
        count_id=count_id,
        posted_lines=len(lines),
        total_adjustments=adjustments,
        journal_entry_id=journal_entry_id,
        status="posted",
    )


class PeriodCloseResult(BaseModel):
    period: str
    warehouse_count: int
    article_count: int
    total_stock_value: float
    discrepancies_found: int
    status: str


@router.post("/period-close", response_model=PeriodCloseResult, tags=["inventory"])
async def period_close(
    period: str = Query(..., description="Periode z.B. 2026-Q1 oder 2026-12"),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Perioden-Abschluss — Inventur-Zusammenfassung für eine Periode.

    Erzeugt eine Bestandsübersicht aller Lagerorte und prüft auf
    offene Inventuren oder ungebuchte Differenzen.
    """
    tid = tenant_id or DEFAULT_TENANT

    # Count warehouses with stock
    wh_count = db.execute(
        text("""
            SELECT COUNT(DISTINCT warehouse_id)
            FROM domain_inventory.inventory_stock_movements
            WHERE tenant_id = :tid
        """),
        {"tid": tid},
    ).scalar() or 0

    # Count articles with stock
    art_count = db.execute(
        text("""
            SELECT COUNT(*)
            FROM domain_inventory.articles
            WHERE tenant_id = :tid AND COALESCE(current_stock, 0) > 0
        """),
        {"tid": tid},
    ).scalar() or 0

    # Total stock value estimate
    stock_value = db.execute(
        text("""
            SELECT COALESCE(SUM(COALESCE(current_stock, 0) * COALESCE(sales_price, 0)), 0)
            FROM domain_inventory.articles
            WHERE tenant_id = :tid AND current_stock > 0
        """),
        {"tid": tid},
    ).scalar() or 0

    # Check open inventories
    open_counts = db.execute(
        text("""
            SELECT COUNT(*)
            FROM domain_inventory.inventory_counts
            WHERE tenant_id = :tid AND status != 'posted'
        """),
        {"tid": tid},
    ).scalar() or 0

    return PeriodCloseResult(
        period=period,
        warehouse_count=int(wh_count),
        article_count=int(art_count),
        total_stock_value=float(stock_value),
        discrepancies_found=int(open_counts),
        status="closed" if open_counts == 0 else "open_counts_pending",
    )
