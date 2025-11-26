"""Pydantic schemas for Quotes."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class QuoteLineItemBase(BaseModel):
    """Base quote line item schema."""
    product_id: Optional[str] = Field(None, max_length=64)
    product_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    quantity: float = Field(1.0, ge=0)
    unit_price: float = Field(0.0, ge=0)
    discount_percent: float = Field(0.0, ge=0, le=100)


class QuoteLineItemCreate(QuoteLineItemBase):
    """Schema for creating quote line items."""
    pass


class QuoteLineItemUpdate(BaseModel):
    """Schema for updating quote line items."""
    product_id: Optional[str] = Field(None, max_length=64)
    product_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    quantity: Optional[float] = Field(None, ge=0)
    unit_price: Optional[float] = Field(None, ge=0)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)


class QuoteLineItem(QuoteLineItemBase):
    """Full quote line item schema."""
    id: UUID
    quote_id: UUID
    line_total: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuoteBase(BaseModel):
    """Base quote schema."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    opportunity_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    valid_until: Optional[datetime] = None
    status: str = "draft"
    assigned_to: Optional[str] = Field(None, max_length=64)


class QuoteCreate(QuoteBase):
    """Schema for creating quotes."""
    tenant_id: str = Field(..., max_length=64)
    line_items: List[QuoteLineItemCreate] = Field(default_factory=list)


class QuoteUpdate(BaseModel):
    """Schema for updating quotes."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    opportunity_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    valid_until: Optional[datetime] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = Field(None, max_length=64)


class Quote(QuoteBase):
    """Full quote schema."""
    id: UUID
    tenant_id: str
    quote_number: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    line_items: List[QuoteLineItem] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True