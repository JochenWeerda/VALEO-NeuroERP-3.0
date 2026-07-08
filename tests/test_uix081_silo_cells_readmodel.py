"""UIX-081: Silozellen-Read-Model fuer Twin-Panel."""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any

import pytest
from fastapi import Response

from app.api.v1.endpoints.silo_cells_readmodel import list_silo_cells_twin

pytestmark = pytest.mark.unit


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self.rows


class _Db:
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows
        self.calls: list[tuple[Any, dict[str, Any]]] = []

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        self.calls.append((statement, params))
        return _Result(self.rows)


def _call(db: _Db, *, tenant_id: str = "tenant-a", warehouse_id: str | None = None):
    response = Response()
    result = asyncio.run(
        list_silo_cells_twin(
            response,
            warehouse_id=warehouse_id,
            silo_system_id=None,
            tenant_id=tenant_id,
            db=db,  # type: ignore[arg-type]
        )
    )
    return result, response


def test_silo_cells_readmodel_is_tenant_isolated_and_cacheable() -> None:
    db = _Db([
        {
            "id": "cell-1",
            "cell_code": "A01",
            "name": "Silo A01",
            "capacity_kg": Decimal("100000"),
            "current_stock_kg": Decimal("92000"),
            "current_material_id": "weizen",
            "current_lot_id": "lot-1",
            "legacy_silo_id": "legacy-1",
            "qs_status": "gesperrt",
            "layout_x": Decimal("12"),
            "layout_y": Decimal("34"),
        }
    ])

    result, response = _call(db, tenant_id="tenant-uix081", warehouse_id="wh-1")

    params = db.calls[0][1]
    assert params["tenant_id"] == "tenant-uix081"
    assert params["warehouse_id"] == "wh-1"
    assert response.headers["cache-control"] == "private, max-age=30"
    assert result.count == 1
    assert result.plan.cells[0].shape.x == 12.0
    assert result.cellData["cell-1"]["fill_pct"] == 92.0
    assert result.cellData["cell-1"]["locked"] is True
    assert result.cellLinks["cell-1"]["route"] == "/lager/silo-zellen/cell-1"


def test_silo_cells_readmodel_returns_empty_plan_without_5xx() -> None:
    result, response = _call(_Db([]))

    assert result.count == 0
    assert result.plan.cells == []
    assert result.plan.canvas["width"] >= 640
    assert result.cacheTtlSeconds == 30
    assert response.headers["cache-control"] == "private, max-age=30"
