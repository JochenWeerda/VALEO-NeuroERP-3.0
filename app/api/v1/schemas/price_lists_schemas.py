"""Pydantic schemas for the price lists domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class PriceListItemOut(PriceListItemInput):
    id: str
    price_list_id: str


class PriceListCreate(PriceListBase):
    tenant_id: Optional[str] = None


class PriceListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: Optional[bool] = None
    items: Optional[List[PriceListItemInput]] = None

