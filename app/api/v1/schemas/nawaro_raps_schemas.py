"""Pydantic schemas for the nawaro raps domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
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


class RapsProfileIn(BaseModel):
    article_id: str | None = Field(default=None, max_length=64)
    article_number: str | None = Field(default=None, max_length=80)
    article_name: str = Field(default='Raps', min_length=2, max_length=255)
    harvest_year: int = Field(..., ge=2000, le=2100)
    usage_food_pct: str = Field(default='0')
    usage_feed_pct: str = Field(default='0')
    usage_energy_pct: str = Field(default='0')
    usage_material_pct: str = Field(default='0')
    thg_gco2eq_mj: str | None = None
    yield_dt_per_ha: str | None = None
    notes: str | None = None
    certificates: list[RapsCertificateIn] = Field(default_factory=list)
    balances: list[RapsBalanceIn] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_usage_sum(self):
        parts = [
            _to_decimal(self.usage_food_pct) or Decimal('0'),
            _to_decimal(self.usage_feed_pct) or Decimal('0'),
            _to_decimal(self.usage_energy_pct) or Decimal('0'),
            _to_decimal(self.usage_material_pct) or Decimal('0'),
        ]
        total = sum(parts)
        if total != Decimal('100'):
            raise ValueError(f'Usage split must total 100.00%, got {total}')
        return self


class RapsProfileOut(RapsProfileIn):
    id: str
    certificates: list[RapsCertificateOut]
    balances: list[RapsBalanceOut]
    created_at: str | None = None
    updated_at: str | None = None


class RapsDeriveOut(BaseModel):
    profile: RapsProfileOut
    period: str
    source_tickets_kg: str
    source_settlements_kg: str
    source_input_tons: str
    plausibility_messages: list[str] = Field(default_factory=list)

