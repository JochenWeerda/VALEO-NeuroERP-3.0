"""Pydantic schemas for the artikel mengeneinheiten domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class MengeneinheitCreate(BaseModel):
    einheit_kuerzel: str = Field(..., max_length=10)
    bezeichnung: str
    basis_einheit: Optional[str] = Field(None, max_length=10)
    umrechnungsfaktor: Optional[Decimal] = Field(None, gt=0)
    dezimalstellen: int = Field(default=3, ge=0, le=6)


class MengeneinheitOut(BaseModel):
    id: str
    einheit_kuerzel: str
    bezeichnung: str
    basis_einheit: Optional[str]
    umrechnungsfaktor: Optional[Decimal]
    dezimalstellen: int
    aktiv: bool
    created_at: datetime


class MengeneinheitengruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    bestand_einheit: str = Field(..., max_length=10)
    ek_einheit: Optional[str] = Field(None, max_length=10)
    vk_einheit: Optional[str] = Field(None, max_length=10)
    preis_einheit: Optional[str] = Field(None, max_length=10)


class MengeneinheitengruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    bestand_einheit: str
    ek_einheit: Optional[str]
    vk_einheit: Optional[str]
    preis_einheit: Optional[str]
    aktiv: bool
    created_at: datetime

