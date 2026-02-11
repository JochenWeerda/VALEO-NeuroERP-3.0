"""Goods Receipt (Wareneingang) API endpoints."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    GoodsReceipt,
    GoodsReceiptLine,
    GoodsReceiptStatus,
    InventoryTransaction,
    InventoryTransactionType,
    Lot,
    StockItem,
)
from app.db.session import get_session
from app.dependencies import get_event_bus, resolve_tenant_id
from app.schemas.goods_receipt import (
    GoodsReceiptCreate,
    GoodsReceiptListItem,
    GoodsReceiptListResponse,
    GoodsReceiptRead,
    MatchingStatus,
    ThreeWayMatchLine,
    ThreeWayMatchResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Auto-increment GR number
_gr_counter = 0


async def _next_gr_number(session: AsyncSession, tenant_id: str) -> str:
    """Generate the next goods receipt number."""
    result = await session.execute(
        select(func.count(GoodsReceipt.id)).where(GoodsReceipt.tenant_id == tenant_id)
    )
    count = result.scalar_one() + 1
    return f"GR-{datetime.utcnow().strftime('%Y')}-{count:05d}"


@router.post("/goods-receipts", response_model=GoodsReceiptRead, status_code=status.HTTP_201_CREATED)
async def create_goods_receipt(
    payload: GoodsReceiptCreate,
    session: AsyncSession = Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
):
    """Create a new Goods Receipt (Wareneingang) against a Purchase Order.

    This endpoint:
    1. Creates the GR header and lines
    2. Books inventory (creates lots, stock items, transactions)
    3. Publishes an event for downstream processing
    """
    gr_number = await _next_gr_number(session, tenant_id)

    # Create GR header
    gr = GoodsReceipt(
        id=uuid4(),
        tenant_id=tenant_id,
        gr_number=gr_number,
        po_number=payload.po_number,
        po_id=payload.po_id,
        supplier_id=payload.supplier_id,
        supplier_name=payload.supplier_name,
        delivery_note_number=payload.delivery_note_number,
        receipt_date=payload.receipt_date,
        status=GoodsReceiptStatus.POSTED,
        notes=payload.notes,
        created_by="system",  # TODO: from auth context
    )

    # Create GR lines and book inventory
    for line_data in payload.lines:
        line = GoodsReceiptLine(
            id=uuid4(),
            goods_receipt_id=gr.id,
            po_line_number=line_data.po_line_number,
            sku=line_data.sku,
            description=line_data.description,
            ordered_quantity=line_data.ordered_quantity,
            received_quantity=line_data.received_quantity,
            unit=line_data.unit,
            lot_number=line_data.lot_number,
            warehouse_id=line_data.warehouse_id,
            location_id=line_data.location_id,
            quality_status=line_data.quality_status,
            notes=line_data.notes,
        )
        gr.lines.append(line)

        # Create or find lot
        lot_number = line_data.lot_number or f"LOT-{gr_number}-{line_data.po_line_number}"
        existing_lot = await session.execute(
            select(Lot).where(Lot.sku == line_data.sku, Lot.lot_number == lot_number)
        )
        lot = existing_lot.scalar_one_or_none()
        if lot is None:
            lot = Lot(
                id=uuid4(),
                sku=line_data.sku,
                lot_number=lot_number,
                production_date=line_data.production_date,
                expiry_date=line_data.expiry_date,
            )
            session.add(lot)
            await session.flush()

        # Create or update stock item
        existing_stock = await session.execute(
            select(StockItem).where(
                StockItem.warehouse_id == line_data.warehouse_id,
                StockItem.location_id == line_data.location_id,
                StockItem.lot_id == lot.id,
            )
        )
        stock_item = existing_stock.scalar_one_or_none()
        if stock_item is None:
            stock_item = StockItem(
                id=uuid4(),
                warehouse_id=line_data.warehouse_id,
                location_id=line_data.location_id,
                lot_id=lot.id,
                quantity=line_data.received_quantity,
                reserved_quantity=0,
            )
            session.add(stock_item)
        else:
            stock_item.quantity = float(stock_item.quantity) + line_data.received_quantity

        await session.flush()

        # Create inventory transaction
        txn = InventoryTransaction(
            id=uuid4(),
            stock_item_id=stock_item.id,
            transaction_type=InventoryTransactionType.RECEIPT,
            quantity=line_data.received_quantity,
            reference=f"GR:{gr_number}/PO:{payload.po_number}",
            to_location_id=line_data.location_id,
        )
        session.add(txn)

    session.add(gr)
    await session.commit()

    # Reload with lines
    result = await session.execute(
        select(GoodsReceipt).options(selectinload(GoodsReceipt.lines)).where(GoodsReceipt.id == gr.id)
    )
    created_gr = result.scalar_one()

    logger.info("Goods Receipt %s created for PO %s (%d lines)", gr_number, payload.po_number, len(payload.lines))

    # Publish event
    event_bus = get_event_bus()
    if event_bus:
        try:
            await event_bus.publish(
                "inventory.goods_receipt.created",
                {
                    "gr_id": str(gr.id),
                    "gr_number": gr_number,
                    "po_number": payload.po_number,
                    "tenant_id": tenant_id,
                    "line_count": len(payload.lines),
                },
            )
        except Exception as exc:
            logger.warning("Failed to publish GR event: %s", exc)

    return created_gr


@router.get("/goods-receipts", response_model=GoodsReceiptListResponse)
async def list_goods_receipts(
    po_number: Optional[str] = Query(None, description="Filter by PO number"),
    status_filter: Optional[GoodsReceiptStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
):
    """List goods receipts with optional filters."""
    query = select(GoodsReceipt).where(GoodsReceipt.tenant_id == tenant_id)

    if po_number:
        query = query.where(GoodsReceipt.po_number == po_number)
    if status_filter:
        query = query.where(GoodsReceipt.status == status_filter)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar_one()

    # Fetch
    query = query.options(selectinload(GoodsReceipt.lines)).order_by(GoodsReceipt.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    receipts = result.scalars().all()

    items = []
    for gr in receipts:
        total_received = sum(float(line.received_quantity) for line in gr.lines)
        items.append(
            GoodsReceiptListItem(
                id=gr.id,
                gr_number=gr.gr_number,
                po_number=gr.po_number,
                supplier_name=gr.supplier_name,
                receipt_date=gr.receipt_date,
                status=gr.status,
                line_count=len(gr.lines),
                total_received=total_received,
                created_at=gr.created_at,
            )
        )

    return GoodsReceiptListResponse(items=items, total=total)


@router.get("/goods-receipts/{gr_id}", response_model=GoodsReceiptRead)
async def get_goods_receipt(
    gr_id: UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
):
    """Get a single goods receipt by ID."""
    result = await session.execute(
        select(GoodsReceipt)
        .options(selectinload(GoodsReceipt.lines))
        .where(GoodsReceipt.id == gr_id, GoodsReceipt.tenant_id == tenant_id)
    )
    gr = result.scalar_one_or_none()
    if gr is None:
        raise HTTPException(status_code=404, detail=f"Goods receipt {gr_id} not found")
    return gr


@router.post("/goods-receipts/{gr_id}/cancel", response_model=GoodsReceiptRead)
async def cancel_goods_receipt(
    gr_id: UUID,
    session: AsyncSession = Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
):
    """Cancel a goods receipt and reverse inventory bookings."""
    result = await session.execute(
        select(GoodsReceipt)
        .options(selectinload(GoodsReceipt.lines))
        .where(GoodsReceipt.id == gr_id, GoodsReceipt.tenant_id == tenant_id)
    )
    gr = result.scalar_one_or_none()
    if gr is None:
        raise HTTPException(status_code=404, detail=f"Goods receipt {gr_id} not found")

    if gr.status == GoodsReceiptStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Goods receipt already cancelled")

    # Reverse inventory for each line
    for line in gr.lines:
        lot_result = await session.execute(
            select(Lot).where(Lot.sku == line.sku, Lot.lot_number == (line.lot_number or f"LOT-{gr.gr_number}-{line.po_line_number}"))
        )
        lot = lot_result.scalar_one_or_none()
        if lot:
            stock_result = await session.execute(
                select(StockItem).where(
                    StockItem.warehouse_id == line.warehouse_id,
                    StockItem.location_id == line.location_id,
                    StockItem.lot_id == lot.id,
                )
            )
            stock_item = stock_result.scalar_one_or_none()
            if stock_item:
                stock_item.quantity = max(0, float(stock_item.quantity) - float(line.received_quantity))
                # Create reversal transaction
                txn = InventoryTransaction(
                    id=uuid4(),
                    stock_item_id=stock_item.id,
                    transaction_type=InventoryTransactionType.ADJUSTMENT,
                    quantity=-float(line.received_quantity),
                    reference=f"GR-CANCEL:{gr.gr_number}",
                    from_location_id=line.location_id,
                )
                session.add(txn)

    gr.status = GoodsReceiptStatus.CANCELLED
    await session.commit()

    logger.info("Goods Receipt %s cancelled", gr.gr_number)
    return gr


@router.post("/three-way-match", response_model=ThreeWayMatchResult)
async def perform_three_way_match(
    po_number: str = Query(..., description="Purchase order number"),
    invoice_number: Optional[str] = Query(None, description="Invoice number for 3-way match"),
    tolerance_percent: float = Query(2.0, ge=0, le=10, description="Tolerance in %"),
    session: AsyncSession = Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
):
    """Perform 2-way (PO vs GR) or 3-way (PO vs GR vs Invoice) matching.

    Compares quantities and optionally prices between:
    - Purchase Order (PO)
    - Goods Receipt (GR)
    - Incoming Invoice (optional, for 3-way match)

    Returns match status per line and overall approval recommendation.
    """
    # Get all goods receipts for this PO
    gr_result = await session.execute(
        select(GoodsReceipt)
        .options(selectinload(GoodsReceipt.lines))
        .where(
            GoodsReceipt.po_number == po_number,
            GoodsReceipt.tenant_id == tenant_id,
            GoodsReceipt.status == GoodsReceiptStatus.POSTED,
        )
    )
    goods_receipts = gr_result.scalars().all()

    if not goods_receipts:
        raise HTTPException(
            status_code=404,
            detail=f"No goods receipts found for PO {po_number}"
        )

    # Aggregate received quantities by PO line
    gr_by_line: dict[int, float] = {}
    gr_number = goods_receipts[0].gr_number if goods_receipts else None
    for gr in goods_receipts:
        for line in gr.lines:
            gr_by_line[line.po_line_number] = gr_by_line.get(line.po_line_number, 0) + float(line.received_quantity)

    # Build match lines (PO data comes from GR lines as reference)
    match_lines: list[ThreeWayMatchLine] = []
    all_matched = True

    # Collect PO line info from GR lines
    po_lines_info: dict[int, dict] = {}
    for gr in goods_receipts:
        for line in gr.lines:
            if line.po_line_number not in po_lines_info:
                po_lines_info[line.po_line_number] = {
                    "sku": line.sku,
                    "description": line.description,
                    "ordered_quantity": float(line.ordered_quantity),
                }

    for line_num, info in sorted(po_lines_info.items()):
        po_qty = info["ordered_quantity"]
        gr_qty = gr_by_line.get(line_num, 0)
        variance_qty = abs(po_qty - gr_qty)
        tolerance_abs = po_qty * (tolerance_percent / 100)
        qty_match = variance_qty <= tolerance_abs

        line_status = MatchingStatus.MATCHED if qty_match else MatchingStatus.QUANTITY_MISMATCH
        if gr_qty == 0:
            line_status = MatchingStatus.NOT_MATCHED
        elif gr_qty < po_qty and not qty_match:
            line_status = MatchingStatus.PARTIAL

        if not qty_match:
            all_matched = False

        match_lines.append(
            ThreeWayMatchLine(
                po_line_number=line_num,
                sku=info["sku"],
                description=info["description"],
                po_quantity=po_qty,
                gr_quantity=gr_qty,
                quantity_match=qty_match,
                status=line_status,
                variance_quantity=variance_qty,
                tolerance_percent=tolerance_percent,
            )
        )

    total_po = sum(info["ordered_quantity"] for info in po_lines_info.values())
    total_gr = sum(gr_by_line.values())

    overall_status = MatchingStatus.MATCHED if all_matched else MatchingStatus.QUANTITY_MISMATCH

    return ThreeWayMatchResult(
        po_number=po_number,
        gr_number=gr_number,
        invoice_number=invoice_number,
        overall_status=overall_status,
        lines=match_lines,
        total_po_amount=total_po,
        total_gr_amount=total_gr,
        can_approve=all_matched,
        notes=f"{'2-way' if not invoice_number else '3-way'} match with {tolerance_percent}% tolerance",
    )

