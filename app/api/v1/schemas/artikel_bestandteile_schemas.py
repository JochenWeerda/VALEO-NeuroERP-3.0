"""Pydantic schemas for the artikel bestandteile domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class BestandteilDefCreate(BaseModel):
    bestandteil_nr: str = Field(..., max_length=20)
    bezeichnung: str
    einheit: Optional[str] = Field(None, max_length=20,
                                   description="z.B. %, mg/kg, g/kg")
    grenzwert_min: Optional[Decimal] = None
    grenzwert_max: Optional[Decimal] = None
    nutzung: Optional[str] = Field(None,
        description="egal, qualitaetsdaten, ackerschlagkartei, partieartikelanalyse")
    typ_schad_naehr: Optional[str] = Field(None,
        description="beides, schadstoff, naehrstoff, keins")
    waage_qualitaet_nr: Optional[int] = Field(None,
        description="Feldnummer für Waagenqualitäts-Übernahme")


class BestandteilDefOut(BaseModel):
    id: str
    bestandteil_nr: str
    bezeichnung: str
    einheit: Optional[str]
    grenzwert_min: Optional[Decimal]
    grenzwert_max: Optional[Decimal]
    nutzung: Optional[str]
    typ_schad_naehr: Optional[str]
    waage_qualitaet_nr: Optional[int]
    aktiv: bool
    created_at: datetime


class BestandteilZuordnungCreate(BaseModel):
    bestandteil_nr: str
    sollwert: Optional[Decimal] = None


class BestandteilZuordnungOut(BaseModel):
    id: str
    artikel_nr: str
    bestandteil_nr: str
    sollwert: Optional[Decimal]
    created_at: datetime

