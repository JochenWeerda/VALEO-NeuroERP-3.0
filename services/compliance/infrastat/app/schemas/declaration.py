"""Pydantic-Schemas für InfraStat-Entitäten."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DeclarationLineBase(BaseModel):
    sequence_no: int = Field(ge=1, description="Fortlaufende Position")
    commodity_code: str = Field(..., min_length=8, max_length=10)
    country_of_origin: str = Field(..., min_length=2, max_length=2)
    country_of_destination: str = Field(..., min_length=2, max_length=2)
    net_mass_kg: float = Field(..., gt=0)
    supplementary_units: Optional[float] = Field(default=None, gt=0)
    invoice_value_eur: float = Field(..., gt=0)
    statistical_value_eur: Optional[float] = Field(default=None, gt=0)
    nature_of_transaction: str = Field(..., min_length=1, max_length=2)
    transport_mode: str = Field(..., min_length=1, max_length=1)
    delivery_terms: Optional[str] = Field(default=None, min_length=3, max_length=3)
    line_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("commodity_code")
    @classmethod
    def _strip_spaces(cls, value: str) -> str:
        return value.replace(" ", "")


class DeclarationLineCreate(DeclarationLineBase):
    pass


class DeclarationLine(DeclarationLineBase):
    id: UUID
    batch_id: UUID
    created_at: datetime


class DeclarationBatchBase(BaseModel):
    tenant_id: str = Field(..., min_length=1, max_length=64)
    flow_type: str = Field(..., pattern=r"^(arrival|dispatch)$")
    reference_period: date
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeclarationBatchCreate(DeclarationBatchBase):
    lines: List[DeclarationLineCreate] = Field(default_factory=list)


class DeclarationBatch(DeclarationBatchBase):
    id: UUID
    status: str
    total_value_eur: Optional[float] = None
    total_weight_kg: Optional[float] = None
    item_count: int
    created_at: datetime
    updated_at: datetime
    lines: List[DeclarationLine] = Field(default_factory=list)


class ETLJobResult(BaseModel):
    batch_id: UUID
    tenant_id: str
    ingested_lines: int
    skipped_lines: int
    validation_error_count: int
    duration_seconds: float
    warnings: List[str] = Field(default_factory=list)

