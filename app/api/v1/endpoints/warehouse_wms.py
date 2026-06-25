from __future__ import annotations
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.warehouse_service import WarehouseService

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class WarehouseWmsOut(BaseSchema):
    """Typed response schema for WarehouseWmsOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter()


def _svc(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> WarehouseService:
    return WarehouseService(db, tenant_id)


# ── Schemas ────────────────────────────────────────────────────────────────

class ZoneIn(BaseModel):
    zone_code: str
    name: str
    zone_type: str = "standard"
    description: Optional[str] = None


class BinIn(BaseModel):
    bin_code: str
    bin_type: str = "standard"
    capacity_kg: Optional[Decimal] = None
    aisle_id: Optional[str] = None


class AisleIn(BaseModel):
    aisle_code: str
    name: Optional[str] = None
    description: Optional[str] = None


class BinPatch(BaseModel):
    bin_type: Optional[str] = None
    capacity_kg: Optional[Decimal] = None
    is_blocked: Optional[bool] = None
    block_reason: Optional[str] = None
    aisle_id: Optional[str] = None


class BinStockLineQuantityIn(BaseModel):
    quantity_kg: Decimal


class StockMovementIn(BaseModel):
    bin_id: str
    article_id: str
    batch_number: Optional[str] = None
    best_before_date: Optional[str] = None
    quantity_kg: Decimal
    unit_cost: Optional[Decimal] = None
    movement_type: str
    reference: Optional[str] = None


class FefoSuggestionIn(BaseModel):
    warehouse_id: str
    article_id: str
    quantity_needed: Decimal


class PickListItem(BaseModel):
    article_id: str
    quantity_required: Decimal
    unit: str = "kg"


class PickListIn(BaseModel):
    warehouse_id: str
    items: list[PickListItem]
    source_doc_ref: Optional[str] = None
    source_doc_type: str = "MANUAL"
    strategy: str = "FEFO"
    created_by: Optional[str] = None


class PickConfirmLine(BaseModel):
    line_id: str
    quantity_picked: Decimal


class PickConfirmIn(BaseModel):
    picked_lines: list[PickConfirmLine]


class BinTransferIn(BaseModel):
    from_bin_id: str
    to_bin_id: str
    article_id: str
    batch_number: Optional[str] = None
    quantity_kg: Decimal
    best_before_date: Optional[str] = None


# ── Zones ──────────────────────────────────────────────────────────────────

@router.get("/zones", summary="Zones auflisten",
    response_model=WarehouseWmsOut
)
def list_zones(
    warehouse_id: str = Query(...),
    svc: WarehouseService = Depends(_svc),
):
    return svc.list_zones(warehouse_id)


@router.post("/zones", status_code=status.HTTP_201_CREATED, summary="Zone anlegen",
    response_model=WarehouseWmsOut
)
def create_zone(
    warehouse_id: str = Query(...),
    payload: ZoneIn = ...,
    svc: WarehouseService = Depends(_svc),
):
    return svc.create_zone(warehouse_id, payload.model_dump())


# ── Gänge (Aisles) ───────────────────────────────────────────────────────

@router.get("/aisles", summary="Gänge einer Zone auflisten",
    response_model=WarehouseWmsOut
)
def list_aisles(
    zone_id: str = Query(...),
    svc: WarehouseService = Depends(_svc),
):
    return svc.list_aisles(zone_id)


@router.post("/aisles", status_code=status.HTTP_201_CREATED, summary="Gang in Zone anlegen",
    response_model=WarehouseWmsOut
)
def create_aisle(
    zone_id: str = Query(...),
    payload: AisleIn = ...,
    svc: WarehouseService = Depends(_svc),
):
    try:
        return svc.create_aisle(zone_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Bins ───────────────────────────────────────────────────────────────────

@router.get("/bins", summary="Bins auflisten",
    response_model=list[WarehouseWmsOut]
)
def list_bins(
    warehouse_id: Optional[str] = Query(None),
    zone_id: Optional[str] = Query(None),
    aisle_id: Optional[str] = Query(None),
    only_active: bool = Query(True),
    svc: WarehouseService = Depends(_svc),
):
    return svc.list_bins(warehouse_id, zone_id, aisle_id, only_active)


@router.post("/bins", status_code=status.HTTP_201_CREATED, summary="Bin anlegen",
    response_model=WarehouseWmsOut
)
def create_bin(
    zone_id: str = Query(...),
    warehouse_id: str = Query(...),
    payload: BinIn = ...,
    svc: WarehouseService = Depends(_svc),
):
    try:
        return svc.create_bin(zone_id, warehouse_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/bins/{bin_id}", summary="Bin abrufen",
    response_model=WarehouseWmsOut
)
def get_bin_detail(bin_id: str, svc: WarehouseService = Depends(_svc)):
    row = svc.get_bin(bin_id)
    if not row:
        raise HTTPException(status_code=404, detail="Bin nicht gefunden")
    return row


@router.patch("/bins/{bin_id}", summary="Bin aktualisieren",
    response_model=WarehouseWmsOut
)
def patch_bin(
    bin_id: str,
    payload: BinPatch = ...,
    svc: WarehouseService = Depends(_svc),
):
    try:
        return svc.update_bin(bin_id, payload.model_dump(exclude_unset=True))
    except ValueError as e:
        msg = str(e)
        if msg.startswith("Bin nicht gefunden"):
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=422, detail=msg)


@router.get("/bins/{bin_id}/stock", summary="Bin stock abrufen",
    response_model=WarehouseWmsOut
)
def get_bin_stock(bin_id: str, svc: WarehouseService = Depends(_svc)):
    return svc.get_bin_stock(bin_id)


@router.patch(
    "/bins/{bin_id}/stock-lines/{stock_line_id}",
    summary="Bestandszeile (bin_stock) absolute Menge setzen",
    response_model=WarehouseWmsOut,
)
def patch_bin_stock_line(
    bin_id: str,
    stock_line_id: str,
    payload: BinStockLineQuantityIn = ...,
    svc: WarehouseService = Depends(_svc),
):
    try:
        return svc.set_bin_stock_line_quantity(bin_id, stock_line_id, payload.quantity_kg)
    except ValueError as e:
        msg = str(e)
        if "nicht gefunden" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=422, detail=msg)


# ── Stock Movements ────────────────────────────────────────────────────────

@router.post("/stock-movements", status_code=status.HTTP_201_CREATED, summary="Stock movement book",
    response_model=WarehouseWmsOut
)
def book_stock_movement(payload: StockMovementIn, svc: WarehouseService = Depends(_svc)):
    from datetime import date as date_type
    bbd = date_type.fromisoformat(payload.best_before_date) if payload.best_before_date else None
    try:
        mv_id = svc.book_stock_movement(
            bin_id=payload.bin_id,
            article_id=payload.article_id,
            batch_number=payload.batch_number,
            best_before_date=bbd,
            quantity_kg=payload.quantity_kg,
            unit_cost=payload.unit_cost,
            movement_type=payload.movement_type,
            reference=payload.reference,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"movement_id": mv_id}


@router.post("/stock-movements/fefo-suggestion", summary="Suggestion fefo",
    response_model=WarehouseWmsOut
)
def fefo_suggestion(payload: FefoSuggestionIn, svc: WarehouseService = Depends(_svc)):
    result = svc.fefo_pick_suggestion(payload.warehouse_id, payload.article_id, payload.quantity_needed)
    total_available = sum(r["pick_kg"] for r in result)
    return {
        "suggestions": result,
        "total_available_kg": total_available,
        "quantity_needed": float(payload.quantity_needed),
        "fully_covered": total_available >= float(payload.quantity_needed),
    }


# ── Pick Lists ─────────────────────────────────────────────────────────────

@router.post("/pick-lists", status_code=status.HTTP_201_CREATED, summary="Pick list anlegen",
    response_model=WarehouseWmsOut
)
def create_pick_list(payload: PickListIn, svc: WarehouseService = Depends(_svc)):
    items = [item.model_dump() for item in payload.items]
    return svc.create_pick_list(
        warehouse_id=payload.warehouse_id,
        items=items,
        source_doc_ref=payload.source_doc_ref,
        source_doc_type=payload.source_doc_type,
        strategy=payload.strategy,
        created_by=payload.created_by,
    )


@router.get("/pick-lists", summary="Pick lists auflisten",
    response_model=list[WarehouseWmsOut]
)
def list_pick_lists(
    warehouse_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    svc: WarehouseService = Depends(_svc),
):
    from sqlalchemy import text
    filters = ["tenant_id = :tid"]
    params: dict = {"tid": svc.tenant_id}
    if warehouse_id:
        filters.append("warehouse_id = :wid")
        params["wid"] = warehouse_id
    if status_filter:
        filters.append("status = :st")
        params["st"] = status_filter
    where = " AND ".join(filters)
    rows = svc.db.execute(
        text(f"SELECT * FROM domain_inventory.pick_lists WHERE {where} ORDER BY created_at DESC LIMIT 100"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        params,
    ).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/pick-lists/{pick_list_id}", summary="Pick list abrufen",
    response_model=WarehouseWmsOut
)
def get_pick_list(pick_list_id: str, svc: WarehouseService = Depends(_svc)):
    from sqlalchemy import text
    pl = svc.db.execute(
        text("SELECT * FROM domain_inventory.pick_lists WHERE id = :id AND tenant_id = :tid"),
        {"id": pick_list_id, "tid": svc.tenant_id},
    ).fetchone()
    if not pl:
        raise HTTPException(status_code=404, detail="Pick-Liste nicht gefunden")
    lines = svc.db.execute(
        text("SELECT * FROM domain_inventory.pick_list_lines WHERE pick_list_id = :plid ORDER BY sort_order"),
        {"plid": pick_list_id},
    ).fetchall()
    return {**dict(pl._mapping), "lines": [dict(l._mapping) for l in lines]}


class PickListFromDeliveryNoteIn(BaseModel):
    warehouse_id: Optional[str] = None
    strategy: str = "FEFO"
    created_by: Optional[str] = None


@router.post(
    "/pick-lists/from-delivery-note/{ls_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Kommissionierliste aus Lieferschein (WMS-PICK-LINK-001)",
    response_model=WarehouseWmsOut,
)
def create_pick_list_from_delivery_note(
    ls_id: str,
    payload: PickListFromDeliveryNoteIn,
    svc: WarehouseService = Depends(_svc),
):
    """Erstellt eine WMS-Kommissionierliste (Pick-Liste) aus einem gebuchten Lieferschein.

    Schließt den Belegbruch: Lieferschein (posted/printed) → Kommissionierliste → Warenausgang
    (shipped). Wenn alle Positionen bestätigt werden (confirm), setzt die Pick-Liste den
    Lieferschein-Status automatisch auf 'shipped'.
    """
    try:
        return svc.create_pick_list_from_delivery_note(
            ls_id=ls_id,
            warehouse_id=payload.warehouse_id,
            strategy=payload.strategy,
            created_by=payload.created_by,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/pick-lists/{pick_list_id}/confirm", summary="Pick list bestätigen",
    response_model=WarehouseWmsOut
)
def confirm_pick_list(
    pick_list_id: str,
    payload: PickConfirmIn,
    svc: WarehouseService = Depends(_svc),
):
    try:
        return svc.confirm_pick_list(pick_list_id, [l.model_dump() for l in payload.picked_lines])
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Transfers ──────────────────────────────────────────────────────────────

@router.post("/bin-transfers", status_code=status.HTTP_201_CREATED, summary="Transfer bin",
    response_model=WarehouseWmsOut
)
def bin_transfer(payload: BinTransferIn, svc: WarehouseService = Depends(_svc)):
    from datetime import date as date_type
    bbd = date_type.fromisoformat(payload.best_before_date) if payload.best_before_date else None
    try:
        return svc.transfer_bin_to_bin(
            from_bin_id=payload.from_bin_id,
            to_bin_id=payload.to_bin_id,
            article_id=payload.article_id,
            batch_number=payload.batch_number,
            quantity_kg=payload.quantity_kg,
            best_before_date=bbd,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── MHD Ampel ─────────────────────────────────────────────────────────────

@router.get("/mhd-alert", summary="Alert mhd",
    response_model=WarehouseWmsOut
)
def mhd_alert(
    warehouse_id: str = Query(...),
    days_warning: int = Query(30),
    days_critical: int = Query(7),
    svc: WarehouseService = Depends(_svc),
):
    return svc.get_mhd_alert(warehouse_id, days_warning, days_critical)


# ── Stock Valuation ────────────────────────────────────────────────────────

@router.get("/stock-valuation", summary="Valuation stock",
    response_model=list[WarehouseWmsOut]
)
def stock_valuation(
    warehouse_id: Optional[str] = Query(None),
    svc: WarehouseService = Depends(_svc),
):
    return svc.get_stock_valuation(warehouse_id)


# ── Einlagerungsstrategie (Putaway) ─────────────────────────────────────────

class PutawayRequest(BaseModel):
    article_id: str
    quantity_kg: float
    best_before_date: Optional[str] = None
    strategy: str = "CAPACITY"


@router.post("/warehouses/{warehouse_id}/suggest-putaway", summary="Einlagerungsvorschlag (Putaway)")
def suggest_putaway(
    warehouse_id: str,
    payload: PutawayRequest,
    svc: WarehouseService = Depends(_svc),
):
    from decimal import Decimal as _D
    from datetime import date as _date
    bbd = None
    if payload.best_before_date:
        try:
            bbd = _date.fromisoformat(payload.best_before_date)
        except ValueError:
            pass
    return svc.suggest_putaway_bin(
        warehouse_id=warehouse_id,
        article_id=payload.article_id,
        quantity_kg=_D(str(payload.quantity_kg)),
        best_before_date=bbd,
        strategy=payload.strategy,
    )
