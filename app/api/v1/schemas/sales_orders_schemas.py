"""Pydantic schemas for the sales orders domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class SalesOrderCreate(SalesOrderBase):
    tenant_id: Optional[str] = None


class SalesOrderUpdate(BaseModel):
    order_number: Optional[str] = None
    customer_id: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    contact_person: Optional[str] = None
    delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    shipping_method: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[list["SalesOrderItemInput"]] = None


class SalesOrderItemOut(SalesOrderItemInput):
    id: str
    line_number: int
    line_total: float

