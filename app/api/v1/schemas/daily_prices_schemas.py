"""Pydantic schemas for the daily prices domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class DailyPriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Output-Model für Tagespreis."""
    id: str
    tenant_id: str
    article_id: Optional[str] = None
    warengruppe: Optional[str] = None
    crop_code: Optional[str] = None
    price_eur_per_ton: float
    currency: str
    price_date: date
    valid_from: datetime
    valid_to: Optional[datetime] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class DailyPriceCreateIn(BaseModel):
    """Input-Model für Preis-Erstellung."""
    article_id: Optional[str] = None
    warengruppe: Optional[str] = None
    crop_code: Optional[str] = None
    price_eur_per_ton: float = Field(..., gt=0)
    currency: str = "EUR"
    price_date: date
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    source_type: str = "manual"
    source_id: Optional[str] = None
    source_name: Optional[str] = None


class DailyPriceBulkCreateIn(BaseModel):
    """Input-Model für Bulk-Import."""
    prices: list[DailyPriceCreateIn] = Field(..., min_length=1)


class PriceRuleEvaluateIn(BaseModel):
    quality_values: dict = Field(..., description="z.B. moisture_pct, hl_weight, impurity_pct")
    base_price_eur_per_ton: float = Field(..., gt=0)
    commodity: Optional[str] = None
    warengruppe: Optional[str] = None


class PriceRuleEvaluateOut(BaseModel):
    base_price_eur_per_ton: float
    adjustments: list[dict]
    final_price_eur_per_ton: float

