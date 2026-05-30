"""Pydantic schemas for the dauerauftraege domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class DauerauftragPositionCreate(BaseModel):
    pos_nr: int
    artikel_nr: str
    menge: Decimal = Field(..., gt=0)
    mengeneinheit: Optional[str] = None
    preis_eur: Optional[Decimal] = Field(None, ge=0)


class DauerauftragCreate(BaseModel):
    da_nr: Optional[str] = None
    kunden_nr: str
    bezeichnung: Optional[str] = None
    da_anfang: date
    da_naechster: date
    da_ende: Optional[date] = None
    perioden_typ: str = Field(default="monatlich")
    perioden_wert: int = Field(default=1, ge=1, le=12)
    positionen: list[DauerauftragPositionCreate] = []


class DauerauftragPositionOut(BaseModel):
    id: str
    pos_nr: int
    artikel_nr: str
    menge: Decimal
    mengeneinheit: Optional[str]
    preis_eur: Optional[Decimal]


class DauerauftragOut(BaseModel):
    id: str
    da_nr: str
    kunden_nr: str
    bezeichnung: Optional[str]
    da_anfang: date
    da_naechster: date
    da_ende: Optional[date]
    perioden_typ: str
    perioden_wert: int
    aktiv: bool
    letzter_lauf: Optional[datetime]
    created_at: datetime
    positionen: list[DauerauftragPositionOut] = []


class AusfuehrungOut(BaseModel):
    id: str
    dauerauftrag_id: str
    ausfuehrungs_datum: date
    belegnummer: Optional[str]
    status: str
    created_at: datetime

