"""Pydantic schemas for the rfq domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class RfqOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class RfqCreate(BaseModel):
    article_id: str
    quantity: float
    needed_by_date: Optional[date] = None
    notes: Optional[str] = None


class QuoteCreate(BaseModel):
    supplier_id: str
    unit_price: float
    delivery_days: Optional[int] = None
    notes: Optional[str] = None


class SendRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None

