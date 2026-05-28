"""Pydantic schemas for the commodity positions domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


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

