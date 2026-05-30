"""Pydantic schemas for the produktion mischfutter domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class RezeptKomponenteOut(BaseModel):
    komponente_name: str
    anteil: float
    einzelfutter_id: Optional[str] = None


class RezeptOut(BaseModel):
    id: str
    name: str
    rezept_code: str
    tierart: str
    protein_ziel: Optional[float] = None
    energie_ziel: Optional[float] = None
    komponenten: list[RezeptKomponenteOut] = []


class ProduktionsauftragIn(BaseModel):
    rezept_id: str = Field(..., min_length=1)
    menge_t: float = Field(..., gt=0)
    chargen_id: str = ""
    bemerkung: str = ""


class ProduktionsauftragOut(BaseModel):
    id: str
    chargen_id: str
    rezept_id: Optional[str]
    rezept_name: str
    menge_t: float
    status: str
    bestands_abzug_erfolgt: bool
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProduktionsauftragStatusIn(BaseModel):
    status: str = Field(..., pattern="^(freigegeben|in_produktion|fertig|storniert)$")
    freigegeben_von: Optional[str] = None

