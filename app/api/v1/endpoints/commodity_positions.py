"""
Commodity Position Matrix API: Matrix, Drilldown, KPI, Coverage Monitor, Refresh.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rbac import Permission, require_permission
from app.core.tenant import get_tenant_id
from app.domains.operations.models import PosPositionOverride
from app.services.position_service import (
    PositionCalculationService,
    PERIOD_MODE_MONTH,
    PERIOD_MODE_QUARTER,
    PERIOD_MODE_WEEK,
)
from app.services.position_snapshot_service import PositionSnapshotService

router = APIRouter(prefix="/positions", tags=["positions", "commodity"])


class PeriodCellOut(BaseModel):
    period_key: str
    qty_buy_open: float
    qty_sell_open: float
    qty_net: float
    severity: str
    qty_tolerance: Optional[float] = None


class ArticleRowOut(BaseModel):
    article_id: str
    article_name: str
    unit: str
    sum_buy_open: float
    sum_sell_open: float
    sum_net: float
    cells: list[PeriodCellOut]


class MatrixResponse(BaseModel):
    period_keys: list[str]
    rows: list[ArticleRowOut]
    as_of_date: date
    period_mode: str


class ContractOpenItemOut(BaseModel):
    contract_id: str
    contract_no: str
    party_id: str
    position_no: int
    article_id: str
    qty_contract: float
    qty_delivered: float
    qty_rest: float
    unit: str
    unit_price: Optional[float] = None
    valid_to: Optional[datetime] = None
    clerk_id: Optional[str] = None


class MovementItemOut(BaseModel):
    movement_id: str
    contract_id: str
    order_no: Optional[str] = None
    delivery_note_no: Optional[str] = None
    invoice_no: Optional[str] = None
    movement_date: Optional[datetime] = None
    quantity: float
    unit_price: Optional[float] = None
    route_no: Optional[str] = None


class TopCauserOut(BaseModel):
    contract_id: str
    contract_no: str
    contract_type: str
    qty_rest: float
    share_pct: Optional[float] = None


class DrilldownResponse(BaseModel):
    article_id: str
    article_name: str
    period_key: str
    branch_id: Optional[str] = None
    qty_buy_open: float
    qty_sell_open: float
    qty_net: float
    severity: str
    buy_contracts: list[ContractOpenItemOut]
    sell_contracts: list[ContractOpenItemOut]
    movements: list[MovementItemOut]
    top_causers: list[TopCauserOut]


class CoverageItemOut(BaseModel):
    article_id: str
    article_name: str
    period_key: str
    qty_buy_open: float
    qty_sell_open: float
    qty_net: float
    qty_tolerance: Optional[float] = None
    severity: str
    responsible: Optional[str] = None
    override_status: Optional[str] = None


class CoverageMonitorResponse(BaseModel):
    items: list[CoverageItemOut]
    total: int


class KpiResponse(BaseModel):
    short_cell_count: int
    max_short_qty: float
    max_short_article_id: Optional[str] = None
    max_short_period_key: Optional[str] = None
    expiring_coverage_count: int


def _decimal_to_float(d: Optional[Decimal]) -> float:
    return float(d) if d is not None else 0.0


@router.get("/matrix", response_model=MatrixResponse, summary="Matrix abrufen")
def get_matrix(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
    branch_id: Optional[str] = Query(None),
    as_of_date: date = Query(default=None),
    period_mode: str = Query(default="M", description="W | M | Q"),
    period_from: str = Query(..., description="YYYY-MM or YYYY-Wnn or YYYY-Qn"),
    period_to: str = Query(..., description="YYYY-MM or YYYY-Wnn or YYYY-Qn"),
    article_ids: Optional[str] = Query(None, description="Comma-separated article IDs"),
    use_cache: bool = Query(False),
    view_mode: str = Query("physisch_disponiert", description="physisch_disponiert | inkl_archiv"),
) -> Any:
    if as_of_date is None:
        as_of_date = date.today()
    pm = period_mode.upper() or "M"
    if pm not in (PERIOD_MODE_WEEK, PERIOD_MODE_MONTH, PERIOD_MODE_QUARTER):
        pm = PERIOD_MODE_MONTH
    vm = view_mode or "physisch_disponiert"
    if vm not in ("physisch", "physisch_disponiert", "inkl_archiv"):
        vm = "physisch_disponiert"
    ids = [x.strip() for x in article_ids.split(",")] if article_ids else None
    svc = PositionSnapshotService(db) if use_cache else PositionCalculationService(db)
    if use_cache:
        matrix = svc.get_or_refresh(
            tenant_id=tenant_id,
            branch_id=branch_id,
            as_of_date=as_of_date,
            period_mode=pm,
            period_from=period_from,
            period_to=period_to,
            article_ids=ids,
            use_cache=True,
            view_mode=vm,
        )
    else:
        matrix = PositionCalculationService(db).calculate_matrix(
            tenant_id=tenant_id,
            branch_id=branch_id,
            as_of_date=as_of_date,
            period_mode=pm,
            period_from=period_from,
            period_to=period_to,
            article_ids=ids,
            view_mode=vm,
        )
    rows_out = [
        ArticleRowOut(
            article_id=r.article_id,
            article_name=r.article_name,
            unit=r.unit,
            sum_buy_open=_decimal_to_float(r.sum_buy_open),
            sum_sell_open=_decimal_to_float(r.sum_sell_open),
            sum_net=_decimal_to_float(r.sum_net),
            cells=[
                PeriodCellOut(
                    period_key=c.period_key,
                    qty_buy_open=_decimal_to_float(c.qty_buy_open),
                    qty_sell_open=_decimal_to_float(c.qty_sell_open),
                    qty_net=_decimal_to_float(c.qty_net),
                    severity=c.severity,
                    qty_tolerance=_decimal_to_float(c.qty_tolerance) if c.qty_tolerance is not None else None,
                )
                for c in r.cells
            ],
        )
        for r in matrix.rows
    ]
    return MatrixResponse(period_keys=matrix.period_keys, rows=rows_out, as_of_date=matrix.as_of_date, period_mode=matrix.period_mode)


@router.get("/cell/{article_id}/{period_key}", response_model=DrilldownResponse, summary="Cell drilldown abrufen")
def get_cell_drilldown(
    article_id: str,
    period_key: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
    branch_id: Optional[str] = Query(None),
    as_of_date: Optional[date] = Query(None),
    period_mode: str = Query(default="M"),
    view_mode: str = Query("physisch_disponiert", description="physisch_disponiert | inkl_archiv"),
) -> Any:
    as_of = as_of_date or date.today()
    pm = (period_mode or "M").upper()
    vm = view_mode or "physisch_disponiert"
    if vm not in ("physisch", "physisch_disponiert", "inkl_archiv"):
        vm = "physisch_disponiert"
    svc = PositionCalculationService(db)
    drill = svc.get_drilldown(
        tenant_id=tenant_id,
        branch_id=branch_id,
        article_id=article_id,
        period_key=period_key,
        as_of_date=as_of,
        period_mode=pm,
        view_mode=vm,
    )
    if not drill:
        raise HTTPException(status_code=404, detail="Position nicht gefunden")
    return DrilldownResponse(
        article_id=drill.article_id,
        article_name=drill.article_name,
        period_key=drill.period_key,
        branch_id=drill.branch_id,
        qty_buy_open=_decimal_to_float(drill.qty_buy_open),
        qty_sell_open=_decimal_to_float(drill.qty_sell_open),
        qty_net=_decimal_to_float(drill.qty_net),
        severity=drill.severity,
        buy_contracts=[
            ContractOpenItemOut(
                contract_id=x.contract_id,
                contract_no=x.contract_no,
                party_id=x.party_id,
                position_no=x.position_no,
                article_id=x.article_id,
                qty_contract=_decimal_to_float(x.qty_contract),
                qty_delivered=_decimal_to_float(x.qty_delivered),
                qty_rest=_decimal_to_float(x.qty_rest),
                unit=x.unit,
                unit_price=_decimal_to_float(x.unit_price) if x.unit_price is not None else None,
                valid_to=x.valid_to,
                clerk_id=x.clerk_id,
            )
            for x in drill.buy_contracts
        ],
        sell_contracts=[
            ContractOpenItemOut(
                contract_id=x.contract_id,
                contract_no=x.contract_no,
                party_id=x.party_id,
                position_no=x.position_no,
                article_id=x.article_id,
                qty_contract=_decimal_to_float(x.qty_contract),
                qty_delivered=_decimal_to_float(x.qty_delivered),
                qty_rest=_decimal_to_float(x.qty_rest),
                unit=x.unit,
                unit_price=_decimal_to_float(x.unit_price) if x.unit_price is not None else None,
                valid_to=x.valid_to,
                clerk_id=x.clerk_id,
            )
            for x in drill.sell_contracts
        ],
        movements=[
            MovementItemOut(
                movement_id=m.movement_id,
                contract_id=m.contract_id,
                order_no=m.order_no,
                delivery_note_no=m.delivery_note_no,
                invoice_no=m.invoice_no,
                movement_date=m.movement_date,
                quantity=_decimal_to_float(m.quantity),
                unit_price=_decimal_to_float(m.unit_price) if m.unit_price is not None else None,
                route_no=m.route_no,
            )
            for m in drill.movements
        ],
        top_causers=[
            TopCauserOut(
                contract_id=t.contract_id,
                contract_no=t.contract_no,
                contract_type=t.contract_type,
                qty_rest=_decimal_to_float(t.qty_rest),
                share_pct=t.share_pct,
            )
            for t in drill.top_causers
        ],
    )


def _coverage_override_map(
    db: Session, tenant_id: str, branch_id: Optional[str]
) -> dict[tuple[str, str], tuple[str, Optional[str]]]:
    """(article_id, period_key) -> (status, responsible)."""
    q = db.query(PosPositionOverride).filter(
        PosPositionOverride.tenant_id == tenant_id,
        PosPositionOverride.status.in_(["REQUESTED", "APPROVED"]),
    )
    if branch_id:
        q = q.filter(
            (PosPositionOverride.branch_id.is_(None)) | (PosPositionOverride.branch_id == branch_id)
        )
    overrides = q.all()
    out: dict[tuple[str, str], tuple[str, Optional[str]]] = {}
    for r in overrides:
        key = (r.article_id, r.period_key)
        resp = r.approved_by or r.requested_by
        if key not in out or r.status == "APPROVED":
            out[key] = (r.status, resp)
    return out


@router.get("/coverage-monitor", response_model=CoverageMonitorResponse, summary="Coverage monitor abrufen")
def get_coverage_monitor(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
    branch_id: Optional[str] = Query(None),
    as_of_date: Optional[date] = Query(None),
    period_mode: str = Query(default="M"),
    period_from: str = Query(...),
    period_to: str = Query(...),
    severity_filter: Optional[str] = Query(None, description="RED, YELLOW, or RED,YELLOW"),
    without_override_only: bool = Query(False, description="Nur Positionen ohne Override anzeigen"),
    view_mode: str = Query("physisch_disponiert", description="physisch_disponiert | inkl_archiv"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    as_of = as_of_date or date.today()
    vm = view_mode or "physisch_disponiert"
    if vm not in ("physisch", "physisch_disponiert", "inkl_archiv"):
        vm = "physisch_disponiert"
    matrix = PositionCalculationService(db).calculate_matrix(
        tenant_id=tenant_id,
        branch_id=branch_id,
        as_of_date=as_of,
        period_mode=(period_mode or "M").upper(),
        period_from=period_from,
        period_to=period_to,
        article_ids=None,
        view_mode=vm,
    )
    override_map = _coverage_override_map(db, tenant_id, branch_id)
    items: list[CoverageItemOut] = []
    for row in matrix.rows:
        for cell in row.cells:
            if severity_filter:
                allowed = cell.severity in [s.strip() for s in severity_filter.split(",")]
                if not allowed:
                    continue
            if cell.severity not in ("RED", "YELLOW"):
                continue
            key = (row.article_id, cell.period_key)
            ov = override_map.get(key)
            if without_override_only and ov is not None:
                continue
            status_str, responsible = ov if ov else (None, None)
            items.append(
                CoverageItemOut(
                    article_id=row.article_id,
                    article_name=row.article_name,
                    period_key=cell.period_key,
                    qty_buy_open=_decimal_to_float(cell.qty_buy_open),
                    qty_sell_open=_decimal_to_float(cell.qty_sell_open),
                    qty_net=_decimal_to_float(cell.qty_net),
                    qty_tolerance=_decimal_to_float(cell.qty_tolerance) if cell.qty_tolerance is not None else None,
                    severity=cell.severity,
                    responsible=responsible,
                    override_status=status_str,
                )
            )
    total = len(items)
    items = items[skip : skip + limit]
    return CoverageMonitorResponse(items=items, total=total)


@router.get("/kpi", response_model=KpiResponse, summary="Kpi abrufen")
def get_kpi(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
    branch_id: Optional[str] = Query(None),
    as_of_date: Optional[date] = Query(None),
    period_mode: str = Query(default="M"),
    period_from: str = Query(...),
    period_to: str = Query(...),
    article_ids: Optional[str] = Query(None),
    view_mode: str = Query("physisch_disponiert", description="physisch_disponiert | inkl_archiv"),
) -> Any:
    as_of = as_of_date or date.today()
    vm = view_mode or "physisch_disponiert"
    if vm not in ("physisch", "physisch_disponiert", "inkl_archiv"):
        vm = "physisch_disponiert"
    ids = [x.strip() for x in article_ids.split(",")] if article_ids else None
    kpi = PositionCalculationService(db).calculate_kpi(
        tenant_id=tenant_id,
        branch_id=branch_id,
        as_of_date=as_of,
        period_mode=(period_mode or "M").upper(),
        period_from=period_from,
        period_to=period_to,
        article_ids=ids,
        view_mode=vm,
    )
    return KpiResponse(
        short_cell_count=kpi.short_cell_count,
        max_short_qty=_decimal_to_float(kpi.max_short_qty),
        max_short_article_id=kpi.max_short_article_id,
        max_short_period_key=kpi.max_short_period_key,
        expiring_coverage_count=kpi.expiring_coverage_count,
    )


@router.post("/refresh", summary="Snapshot aktualisieren")
def refresh_snapshot(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
    branch_id: Optional[str] = Query(None),
    as_of_date: Optional[date] = Query(None),
    period_mode: str = Query(default="M"),
    period_from: str = Query(...),
    period_to: str = Query(...),
    article_ids: Optional[str] = Query(None),
    view_mode: str = Query("physisch_disponiert", description="physisch_disponiert | inkl_archiv"),
) -> Any:
    as_of = as_of_date or date.today()
    vm = view_mode or "physisch_disponiert"
    if vm not in ("physisch", "physisch_disponiert", "inkl_archiv"):
        vm = "physisch_disponiert"
    ids = [x.strip() for x in article_ids.split(",")] if article_ids else None
    count = PositionSnapshotService(db).refresh_snapshot(
        tenant_id=tenant_id,
        branch_id=branch_id,
        as_of_date=as_of,
        period_mode=(period_mode or "M").upper(),
        period_from=period_from,
        period_to=period_to,
        article_ids=ids,
        view_mode=vm,
    )
    return {"ok": True, "cells_written": count}
