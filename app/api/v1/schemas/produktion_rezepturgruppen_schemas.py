"""Pydantic schemas for the produktion rezepturgruppen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class RezepturGruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    tierart: Optional[str] = None
    nutzungsrichtung: Optional[str] = None


class RezepturGruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    tierart: Optional[str]
    nutzungsrichtung: Optional[str]
    aktiv: bool
    created_at: datetime


class SchnellerfassungCreate(BaseModel):
    bezeichnung: str
    rezept_id: Optional[str] = None
    rezept_name: Optional[str] = None
    standard_menge_t: Optional[Decimal] = None
    ziel_lager_id: Optional[str] = None
    abteilung: Optional[str] = None


class SchnellerfassungOut(BaseModel):
    id: str
    bezeichnung: str
    rezept_id: Optional[str]
    rezept_name: Optional[str]
    standard_menge_t: Optional[Decimal]
    ziel_lager_id: Optional[str]
    abteilung: Optional[str]
    letzter_einsatz: Optional[datetime]
    anzahl_auftraege: int
    aktiv: bool
    created_at: datetime


class SchnellerfassungBuchenPayload(BaseModel):
    menge_t: Decimal = Field(..., gt=0)
    chargen_id: Optional[str] = None
    bemerkung: Optional[str] = None

