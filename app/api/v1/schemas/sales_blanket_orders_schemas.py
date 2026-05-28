"""Auto-generated domain schemas for sales blanket orders.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class SalesBlanketOrdersOut(BaseSchema):
    """Response schema for sales blanket orders endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class BlanketOrderCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    article_id: str = Field(..., min_length=1)
    total_quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    valid_from: datetime
    valid_to: datetime


class BlanketOrderUpdate(BaseModel):
    unit_price: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class BlanketOrderOut(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    article_id: str
    total_quantity: float
    unit_price: float
    valid_from: datetime
    valid_to: datetime
    status: str
    created_at: Optional[datetime] = None


class ReleaseCreate(BaseModel):
    quantity: float = Field(..., gt=0)
    requested_delivery_date: datetime


class ReleaseOut(BaseModel):
    id: str
    blanket_order_id: str
    release_quantity: float
    release_date: datetime
    sales_order_ref: Optional[str] = None
    status: str


class RemainingOut(BaseModel):
    blanket_order_id: str
    total_quantity: float
    released_quantity: float
    remaining_quantity: float
    unit_price: float
    remaining_amount: float

