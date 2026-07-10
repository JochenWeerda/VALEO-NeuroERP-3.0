"""UIX-081 Twin-Panel Read-Model fuer Silozellen."""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from math import ceil, sqrt
from typing import Any

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/lager/silo", tags=["lager", "silo", "twin"])

_CACHE_TTL_SECONDS = 30
_MAX_CELLS = 300


class TwinShapeOut(BaseModel):
    kind: str
    x: float | None = None
    y: float | None = None
    w: float | None = None
    h: float | None = None
    points: list[list[float]] | None = None


class TwinCellOut(BaseModel):
    id: str
    label: str
    shape: TwinShapeOut


class TwinPlanOut(BaseModel):
    plan_id: str
    canvas: dict[str, float]
    cells: list[TwinCellOut]


class TwinMetricOut(BaseModel):
    key: str
    label: str
    kind: str
    warnAbove: float | None = None


class SiloCellsTwinOut(BaseModel):
    plan: TwinPlanOut
    metrics: list[TwinMetricOut]
    cellData: dict[str, dict[str, Any]] = Field(default_factory=dict)
    cellLinks: dict[str, dict[str, str]] = Field(default_factory=dict)
    updatedAt: str
    cacheTtlSeconds: int
    count: int


def _float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _shape_for(row: dict[str, Any], index: int, total: int) -> dict[str, float | str]:
    width = 92.0
    height = 64.0
    gap = 16.0
    if row.get("layout_x") is not None and row.get("layout_y") is not None:
        return {
            "kind": "rect",
            "x": _float(row.get("layout_x")),
            "y": _float(row.get("layout_y")),
            "w": width,
            "h": height,
        }
    cols = max(1, ceil(sqrt(max(total, 1))))
    return {
        "kind": "rect",
        "x": (index % cols) * (width + gap) + gap,
        "y": (index // cols) * (height + gap) + gap,
        "w": width,
        "h": height,
    }


def _canvas(cells: list[dict[str, Any]]) -> dict[str, float]:
    if not cells:
        return {"width": 640.0, "height": 360.0}
    max_x = max(_float(cell["shape"].get("x")) + _float(cell["shape"].get("w"), 92.0) for cell in cells)
    max_y = max(_float(cell["shape"].get("y")) + _float(cell["shape"].get("h"), 64.0) for cell in cells)
    return {"width": max(640.0, max_x + 16.0), "height": max(360.0, max_y + 16.0)}


def _map_rows(rows: list[dict[str, Any]], *, plan_id: str) -> SiloCellsTwinOut:
    cells: list[dict[str, Any]] = []
    cell_data: dict[str, dict[str, Any]] = {}
    cell_links: dict[str, dict[str, str]] = {}
    total = min(len(rows), _MAX_CELLS)
    for index, row in enumerate(rows[:_MAX_CELLS]):
        cell_id = str(row.get("id"))
        capacity_kg = _float(row.get("capacity_kg"))
        stock_kg = _float(row.get("current_stock_kg"))
        fill_pct = round((stock_kg / capacity_kg) * 100, 2) if capacity_kg > 0 else 0.0
        qs_status = str(row.get("qs_status") or "frei")
        label = str(row.get("name") or row.get("cell_code") or cell_id)
        cells.append({
            "id": cell_id,
            "label": label,
            "shape": _shape_for(row, index, total),
        })
        cell_data[cell_id] = {
            "fill_pct": fill_pct,
            "stock_kg": round(stock_kg, 3),
            "capacity_kg": round(capacity_kg, 3),
            "locked": qs_status in {"gesperrt", "reinigung"},
            "qs_status": qs_status,
            "cell_code": row.get("cell_code"),
            "material_id": row.get("current_material_id"),
            "lot_id": row.get("current_lot_id"),
            "legacy_silo_id": row.get("legacy_silo_id"),
        }
        cell_links[cell_id] = {
            "route": f"/lager/silo-zellen/{cell_id}",
            "screen_id": "lager/silo-cell",
        }

    return SiloCellsTwinOut(
        plan=TwinPlanOut(plan_id=plan_id, canvas=_canvas(cells), cells=cells),
        metrics=[
            TwinMetricOut(key="fill_pct", label="Fuellstand", kind="percent", warnAbove=90.0),
            TwinMetricOut(key="stock_kg", label="Bestand kg", kind="number"),
            TwinMetricOut(key="capacity_kg", label="Kapazitaet kg", kind="number"),
            TwinMetricOut(key="locked", label="Gesperrt", kind="flag"),
            TwinMetricOut(key="qs_status", label="QS", kind="status"),
        ],
        cellData=cell_data,
        cellLinks=cell_links,
        updatedAt=datetime.now(UTC).isoformat(),
        cacheTtlSeconds=_CACHE_TTL_SECONDS,
        count=len(cells),
    )


@router.get("/cells", response_model=SiloCellsTwinOut, summary="Twin-Read-Model fuer Silozellen")
async def list_silo_cells_twin(
    response: Response,
    warehouse_id: str | None = Query(default=None, max_length=64),
    silo_system_id: str | None = Query(default=None, max_length=64),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> SiloCellsTwinOut:
    params: dict[str, Any] = {
        "tenant_id": tenant_id,
        "warehouse_id": warehouse_id,
        "silo_system_id": silo_system_id,
    }
    rows = db.execute(
        text("""
            SELECT id, silo_system_id, warehouse_id, cell_code, name, capacity_kg,
                   current_stock_kg, current_material_id, current_lot_id,
                   legacy_silo_id, qs_status, layout_x, layout_y
            FROM domain_inventory.silo_cells
            WHERE tenant_id = :tenant_id
              AND is_active = true
              AND (:warehouse_id IS NULL OR warehouse_id = :warehouse_id)
              AND (:silo_system_id IS NULL OR silo_system_id = :silo_system_id)
            ORDER BY cell_code
            LIMIT :limit
        """),
        {**params, "limit": _MAX_CELLS},
    ).mappings().all()
    response.headers["Cache-Control"] = f"private, max-age={_CACHE_TTL_SECONDS}"
    plan_id = f"silo-cells:{warehouse_id or 'all'}:{silo_system_id or 'all'}"
    return _map_rows([dict(row) for row in rows], plan_id=plan_id)
