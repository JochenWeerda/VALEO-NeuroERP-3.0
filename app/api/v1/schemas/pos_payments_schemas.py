"""Pydantic schemas for the pos payments domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class PosPaymentOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class SplitPaymentIn(BaseModel):
    cart_total: float
    payments: list[PaymentLine]
    cart_ref: Optional[str] = None


class PromotionIn(BaseModel):
    name: str
    promo_type: str  # PROZENT/BETRAG/BOGO/MENGENSTAFFEL
    article_id: Optional[str] = None
    article_group: Optional[str] = None
    discount_value: float
    min_quantity: float = 1.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class PromotionCheckIn(BaseModel):
    article_id: str
    quantity: float
    price: float

