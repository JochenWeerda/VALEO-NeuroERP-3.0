"""Pydantic schemas for the exchange rates domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ExchangeRateOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class ExchangeRateCreate(BaseModel):
    """Schema for creating an exchange rate"""
    from_currency: str = Field(..., min_length=3, max_length=3, description="Source currency (ISO 4217)")
    to_currency: str = Field(..., min_length=3, max_length=3, description="Target currency (ISO 4217)")
    rate: Decimal = Field(..., gt=0, description="Exchange rate")
    rate_date: date = Field(..., description="Date for which this rate is valid")
    rate_type: str = Field(default="SPOT", description="Rate type: SPOT, FORWARD, AVERAGE")
    source: Optional[str] = Field(None, max_length=50, description="Rate source (e.g., ECB, MANUAL)")
    active: bool = Field(default=True, description="Active status")


class ExchangeRateUpdate(BaseModel):
    """Schema for updating an exchange rate"""
    rate: Optional[Decimal] = Field(None, gt=0)
    rate_type: Optional[str] = None
    source: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None


class ExchangeRateResponse(BaseModel):
    """Response schema for exchange rate"""
    id: str
    from_currency: str
    to_currency: str
    rate: Decimal
    rate_date: date
    rate_type: str
    source: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime


class CurrencyConversionRequest(BaseModel):
    """Request for currency conversion"""
    amount: Decimal = Field(..., ge=0)
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    conversion_date: Optional[date] = None
    rate_type: str = Field(default="SPOT", description="Rate type to use")


class CurrencyConversionResponse(BaseModel):
    """Response for currency conversion"""
    original_amount: Decimal
    converted_amount: Decimal
    from_currency: str
    to_currency: str
    exchange_rate: Decimal
    rate_date: date
    rate_type: str

