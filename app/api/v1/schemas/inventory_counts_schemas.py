"""Pydantic schemas for the inventory counts domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


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

