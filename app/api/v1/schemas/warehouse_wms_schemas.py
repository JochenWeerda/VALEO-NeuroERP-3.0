"""Pydantic schemas for the warehouse wms domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class WarehouseWmsOut(BaseSchema):
    """Typed response schema for WarehouseWmsOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class ZoneIn(BaseModel):
    zone_code: str
    name: str
    zone_type: str = "standard"
    description: Optional[str] = None


class BinIn(BaseModel):
    bin_code: str
    bin_type: str = "standard"
    capacity_kg: Optional[Decimal] = None


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


class PickListIn(BaseModel):
    warehouse_id: str
    items: list[PickListItem]
    source_doc_ref: Optional[str] = None
    source_doc_type: str = "MANUAL"
    strategy: str = "FEFO"
    created_by: Optional[str] = None


class PickConfirmIn(BaseModel):
    picked_lines: list[PickConfirmLine]


class BinTransferIn(BaseModel):
    from_bin_id: str
    to_bin_id: str
    article_id: str
    batch_number: Optional[str] = None
    quantity_kg: Decimal
    best_before_date: Optional[str] = None

