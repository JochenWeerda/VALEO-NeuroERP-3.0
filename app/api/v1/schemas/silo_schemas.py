"""Pydantic schemas for the silo domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class SiloOut(BaseSchema):
    """Typed response schema for SiloOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class SiloCreate(BaseModel):
    silo_number: str = Field(..., min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, max_length=120)
    article_id: Optional[str] = Field(default=None, max_length=64)
    capacity_tons: float = Field(..., gt=0)


class SiloLotCreate(BaseModel):
    virtual_lot_number: str = Field(..., min_length=1, max_length=64)
    source_ticket_id: Optional[str] = Field(default=None, max_length=64)
    source_partner_id: Optional[str] = Field(default=None, max_length=64)
    article_id: Optional[str] = Field(default=None, max_length=64)
    quantity_tons: float = Field(..., gt=0)
    moisture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    protein_pct: Optional[float] = Field(default=None, ge=0, le=100)
    impurities_pct: Optional[float] = Field(default=None, ge=0, le=100)
    hl_weight: Optional[float] = Field(default=None, ge=0)


class SiloLotMovementCreate(BaseModel):
    movement_type: str = Field(..., pattern="^(in|out|treatment)$")
    quantity_tons: float = Field(..., gt=0)
    note: Optional[str] = None


class LeermeldungCreate(BaseModel):
    wiegung_id: Optional[str] = None
    schwund_kg: float = Field(..., ge=0, description="Schwund in kg")
    grund: str = Field(..., min_length=1)
    bearbeiter: str = Field(..., min_length=1)

