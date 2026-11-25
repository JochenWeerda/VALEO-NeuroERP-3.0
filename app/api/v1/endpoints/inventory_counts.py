"""
Inventory counts endpoints (l3c-inventur)
GET/POST/PATCH/DELETE for inventory count headers and lines.
"""

from typing import Optional
from datetime import date
from decimal import Decimal

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....infrastructure.models import InventoryCount, InventoryCountLine
from ..schemas.base import PaginatedResponse, BaseSchema
import logging
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

logger = logging.getLogger(__name__)

router = APIRouter()


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

def _inventur(db: Session, tenant_id: str, count_id: str):
    """Die Inventur des angemeldeten Mandanten — eine fremde gibt es fuer ihn nicht.

    Bis 12.10.2026 kam der Mandant aus dem Query-Parameter, und lesen, loeschen und verbuchen
    einer einzelnen Inventur filterten gar nicht.
    """
    return db.query(InventoryCount).filter(
        InventoryCount.id == count_id, InventoryCount.tenant_id == tenant_id
    ).first()


@router.get("/", response_model=PaginatedResponse[InventoryCountOut], summary="Inventory counts auflisten")
async def list_inventory_counts(
    tenant_id: str = Depends(get_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Inventur Übersicht"""
    tid = tenant_id
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


@router.post("/", response_model=InventoryCountOut, status_code=201, summary="Inventory count anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_inventory_count(
    payload: InventoryCountCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Inventur-Kopf anlegen."""
    from app.core.uuid7 import uuid7
    tid = tenant_id
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


@router.get("/{count_id}", response_model=InventoryCountOut, summary="Inventory count abrufen")
async def get_inventory_count(
    count_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
):
    """Inventur-Kopf Detail."""
    obj = _inventur(db, tenant_id, count_id)
    if not obj:
        raise HTTPException(404, "Inventory count not found")
    return InventoryCountOut.model_validate(obj)


@router.delete("/{count_id}", status_code=204, response_class=Response, response_model=None, summary="Inventory count löschen", dependencies=SCHREIBEN["LAGER"])
async def delete_inventory_count(
    count_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
):
    """Inventur-Kopf loeschen."""
    obj = _inventur(db, tenant_id, count_id)
    if not obj:
        raise HTTPException(404, "Inventory count not found")
    db.query(InventoryCountLine).filter(InventoryCountLine.inventory_count_id == count_id).delete()
    db.delete(obj)
    db.commit()


@router.get("/{count_id}/lines", response_model=list[InventoryCountLineOut], summary="Count lines abrufen")
async def get_count_lines(
    count_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
):
    """GET Inventur Positionen"""
    if not _inventur(db, tenant_id, count_id):
        raise HTTPException(404, "Inventory count not found")
    lines = db.query(InventoryCountLine).filter(
        InventoryCountLine.inventory_count_id == count_id
    ).all()
    return [InventoryCountLineOut.model_validate(line_item) for line_item in lines]


@router.post("/lines", response_model=InventoryCountLineOut, status_code=201, summary="Count line anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_count_line(
    payload: InventoryCountLineCreate,
    count_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """POST Inventur Daten anlegen"""
    from app.core.uuid7 import uuid7
    tid = tenant_id
    if not _inventur(db, tid, count_id):
        raise HTTPException(404, "Inventory count not found")
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


@router.patch("/lines/{line_id}", response_model=InventoryCountLineOut, summary="Count line aktualisieren", dependencies=SCHREIBEN["LAGER"])
async def update_count_line(
    line_id: str,
    payload: InventoryCountLineUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """PATCH Inventur Daten ändern"""
    line = db.query(InventoryCountLine).filter(
        InventoryCountLine.id == line_id, InventoryCountLine.tenant_id == tenant_id
    ).first()
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


@router.delete("/lines/{line_id}", status_code=204, response_class=Response, response_model=None, summary="Count line löschen", dependencies=SCHREIBEN["LAGER"])
async def delete_count_line(
    line_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
):
    """POST Inventur Daten löschen"""
    line = db.query(InventoryCountLine).filter(
        InventoryCountLine.id == line_id, InventoryCountLine.tenant_id == tenant_id
    ).first()
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


@router.post("/{count_id}/post", response_model=InventurPostResult, tags=["inventory"], summary="Inventory count erstellen", dependencies=SCHREIBEN["LAGER"])
async def post_inventory_count(
    count_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Inventur-Differenzen verbuchen.

    Für jede Zeile mit Differenz != 0 wird:
    - Ein StockMovement (adjustment) erzeugt
    - Der Artikelbestand angepasst
    - Am Ende eine aggregierte GL-Buchung erstellt
    Der Inventur-Status wechselt auf 'posted'.
    """
    tid = tenant_id
    count = _inventur(db, tid, count_id)
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

    # Buchungsentwurf zum gleitenden Durchschnitt, vor den Bewegungen (Schnitt = Stand vor der Inventur).
    from app.services.bestandsbewertung import BuchungNichtMoeglich, entwerfe_bestandsbuchung

    from .inventory_operations import melde_fehlende_bewertung

    differenzen = [(str(z.article_id), Decimal(str((z.counted_qty or 0) - (z.expected_qty or 0))), "t")
                   for z in lines if abs((z.counted_qty or 0) - (z.expected_qty or 0)) >= 0.001]
    journal_entry_id = None
    if differenzen:
        try:
            journal_entry_id = entwerfe_bestandsbuchung(
                db, tid, f"INVENTUR-{count_id[:8].upper()}", f"Inventurdifferenzen {count_id[:8]}", posting_date,
                differenzen)
        except BuchungNichtMoeglich as grund:
            melde_fehlende_bewertung("inventory_counts_gl", f"INVENTUR-{count_id[:8].upper()} ({grund})")

    for line in lines:
        diff = (line.counted_qty or 0) - (line.expected_qty or 0)
        if abs(diff) < 0.001:
            continue

        adjustments += 1
        ref = f"INV-{count_id[:8].upper()}-{adjustments}"
        lager = line.warehouse_id or count.warehouse_id  # inventory_counts.warehouse_id ist NOT NULL

        # Kanonischer Buchungsdienst (Konsolidierung, 25.11.2026): echter Vorher-/Nachherbestand statt 0, Artikelbestand
        # mandantengebunden (bis dahin WHERE id ohne Mandant), Unterdeckung, Buchungsschluessel je Inventurzeile.
        from app.domains.inventory.application.services.inventory_service import InventoryService

        try:
            InventoryService(db).process_stock_movement(
                str(line.article_id), str(lager), "adjustment", Decimal(str(diff)), unit="t",
                movement_date=posting_date, reference_number=ref, charge=line.batch_number, booking_user="inventur",
                auto_created=True, notes=f"Inventur-Differenz: Soll={line.expected_qty}, Ist={line.counted_qty}",
                tenant_id=tid, buchungsschluessel=f"inventur:{count_id}:{line.id}", commit=False)
        except ValueError as fehler:
            db.rollback()
            raise HTTPException(422, f"Inventurzeile {line.id}: {fehler}") from fehler

        if diff > 0:
            total_positive += Decimal(str(diff))
        else:
            total_negative += Decimal(str(abs(diff)))

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


@router.post("/period-close", response_model=PeriodCloseResult, tags=["inventory"], summary="Close period", dependencies=SCHREIBEN["LAGER"])
async def period_close(
    period: str = Query(..., description="Periode z.B. 2026-Q1 oder 2026-12"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Perioden-Abschluss — Inventur-Zusammenfassung für eine Periode.

    Erzeugt eine Bestandsübersicht aller Lagerorte und prüft auf
    offene Inventuren oder ungebuchte Differenzen.
    """
    tid = tenant_id

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
