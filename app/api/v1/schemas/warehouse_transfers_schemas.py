"""Pydantic schemas for the warehouse transfers domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class TransferOut(BaseSchema):
    id: str
    transfer_number: str
    from_warehouse_id: str
    to_warehouse_id: str
    status: str = "draft"
    notes: Optional[str] = None


class TransferLineOut(BaseSchema):
    id: str
    transfer_id: str
    article_id: str
    quantity: float
    batch_number: Optional[str] = None


class TransferCreate(BaseModel):
    transfer_number: str
    from_warehouse_id: str
    to_warehouse_id: str
    notes: Optional[str] = None


class TransferLineCreate(BaseModel):
    article_id: str
    quantity: float
    batch_number: Optional[str] = None


class CorrectionOut(BaseSchema):
    id: str
    correction_number: str
    warehouse_id: str
    reason: Optional[str] = None
    status: str = "draft"


class CorrectionLineOut(BaseSchema):
    id: str
    correction_id: str
    article_id: str
    old_quantity: float
    new_quantity: float
    difference: float


class CorrectionCreate(BaseModel):
    correction_number: str
    warehouse_id: str
    reason: Optional[str] = None


class CorrectionLineCreate(BaseModel):
    article_id: str
    old_quantity: float
    new_quantity: float


class BinLocationOut(BaseSchema):
    id: str
    code: str
    warehouse_id: str
    zone: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None

