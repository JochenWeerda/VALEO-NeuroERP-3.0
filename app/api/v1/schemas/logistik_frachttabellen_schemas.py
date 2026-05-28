"""Pydantic schemas for the logistik frachttabellen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class FrachttabelleCreate(BaseModel):
    tabelle_nr: str = Field(..., max_length=20)
    bezeichnung: str
    einheit: Optional[str] = Field(None, max_length=20,
                                   description="t, km, Palette, Stück")
    waehrung: str = Field(default="EUR", max_length=3)


class FrachttabelleOut(BaseModel):
    id: str
    tabelle_nr: str
    bezeichnung: str
    einheit: Optional[str]
    waehrung: str
    aktiv: bool
    created_at: datetime


class FrachttabellePositionCreate(BaseModel):
    ab_menge: Decimal = Field(..., ge=0,
                              description="Menge ab der dieser Satz gilt")
    frachtsatz_eur: Decimal = Field(..., ge=0)
    mindestfracht_eur: Optional[Decimal] = None


class FrachttabellePositionOut(BaseModel):
    id: str
    tabelle_nr: str
    ab_menge: Decimal
    frachtsatz_eur: Decimal
    mindestfracht_eur: Optional[Decimal]
    created_at: datetime


class FrachttabelleZuordnungCreate(BaseModel):
    frachtklasse: str = Field(..., max_length=20)
    frachtgruppe: str = Field(..., max_length=20)
    versandart: Optional[str] = Field(None, max_length=30)
    tabelle_nr: str
    sperre: bool = False
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None


class FrachttabelleZuordnungOut(BaseModel):
    id: str
    frachtklasse: str
    frachtgruppe: str
    versandart: Optional[str]
    tabelle_nr: str
    sperre: bool
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    created_at: datetime

