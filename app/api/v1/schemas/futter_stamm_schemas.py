"""Pydantic schemas for the futter stamm domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class EinzelfuttermittelIn(BaseModel):
    artikel_nummer: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    art: str = Field(..., min_length=1, max_length=100)
    herkunft: Optional[str] = None
    lieferant: Optional[str] = None
    protein: Optional[float] = None
    energie: Optional[float] = None
    faser: Optional[float] = None
    fett: Optional[float] = None
    asche: Optional[float] = None
    trockensubstanz: Optional[float] = None
    gvo_status: Optional[str] = None
    qs_milch: bool = False
    gmp_plus: bool = False
    bio_zertifiziert: bool = False
    verfuegbar_t: float = 0
    einheit: str = "t"
    min_bestand_t: Optional[float] = None
    preis_pro_t: Optional[float] = None


class EinzelfuttermittelOut(EinzelfuttermittelIn):
    id: str
    aktiv: bool = True

    model_config = ConfigDict(from_attributes=True)


class MischfuttermittelIn(BaseModel):
    produkt_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    tierart: str = Field(..., min_length=1, max_length=100)
    leistungsstufe: Optional[str] = None
    protein: Optional[float] = None
    energie: Optional[float] = None
    beschreibung: Optional[str] = None


class MischfuttermittelOut(MischfuttermittelIn):
    id: str
    aktiv: bool = True

    model_config = ConfigDict(from_attributes=True)


class RezeptKomponenteIn(BaseModel):
    einzelfutter_id: Optional[str] = None
    komponente_name: str = Field(..., min_length=1)
    anteil: float = Field(..., gt=0, le=1)
    min_anteil: Optional[float] = None
    max_anteil: Optional[float] = None
    sortierung: int = 0


class RezeptKomponenteOut(RezeptKomponenteIn):
    id: str

    model_config = ConfigDict(from_attributes=True)


class RezeptIn(BaseModel):
    rezept_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    tierart: str = Field(..., min_length=1, max_length=100)
    mischfutter_id: Optional[str] = None
    protein_ziel: Optional[float] = None
    energie_ziel: Optional[float] = None
    bemerkung: Optional[str] = None
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None
    komponenten: list[RezeptKomponenteIn] = []


class RezeptOut(BaseModel):
    id: str
    rezept_code: str
    name: str
    tierart: str
    mischfutter_id: Optional[str] = None
    version: int = 1
    protein_ziel: Optional[float] = None
    energie_ziel: Optional[float] = None
    bemerkung: Optional[str] = None
    aktiv: bool = True
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None
    komponenten: list[RezeptKomponenteOut] = []

    model_config = ConfigDict(from_attributes=True)

