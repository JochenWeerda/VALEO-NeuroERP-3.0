from __future__ import annotations

from typing import Any, List, Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.api.v1.schemas.base import BaseSchema

class RapsCertificateIn(BaseModel):
    scheme: str = Field(..., min_length=2, max_length=80)
    certificate_number: str = Field(..., min_length=2, max_length=120)
    chain_stage: str | None = Field(default=None, max_length=80)
    valid_from: date | None = None
    valid_until: date | None = None
    issuer: str | None = Field(default=None, max_length=120)
    status: str = Field(default='valid', max_length=40)


class RapsCertificateOut(RapsCertificateIn):
    id: str


class RapsBalanceIn(BaseModel):
    booking_period: str | None = Field(default=None, max_length=20)
    input_seed_tons: str = Field(default='0')
    output_oil_tons: str = Field(default='0')
    output_meal_tons: str = Field(default='0')
    output_other_tons: str = Field(default='0')
    allocation_oil_pct: str | None = None
    allocation_meal_pct: str | None = None
    heap_location: str | None = Field(default=None, max_length=255)
    logistics_note: str | None = None


class RapsBalanceOut(RapsBalanceIn):
    id: str



class RapsDeriveOut(BaseModel):
    profile: RapsProfileOut
    period: str
    source_tickets_kg: str
    source_settlements_kg: str
    source_input_tons: str
    plausibility_messages: list[str] = Field(default_factory=list)

