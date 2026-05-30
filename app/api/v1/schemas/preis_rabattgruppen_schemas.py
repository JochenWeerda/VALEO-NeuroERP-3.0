"""Pydantic schemas for the preis rabattgruppen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class RabattgruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    richtung: str = Field(..., description="EK oder VK")

    def model_post_init(self, __context):
        if self.richtung not in RICHTUNGEN:
            raise ValueError(f"richtung muss EK oder VK sein, nicht '{self.richtung}'")


class RabattgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    richtung: str
    aktiv: bool
    created_at: datetime


class RabattklasseCreate(BaseModel):
    klasse_nr: str = Field(..., max_length=20)
    bezeichnung: str
    richtung: str = Field(..., description="EK oder VK")

    def model_post_init(self, __context):
        if self.richtung not in RICHTUNGEN:
            raise ValueError(f"richtung muss EK oder VK sein, nicht '{self.richtung}'")


class RabattklasseOut(BaseModel):
    id: str
    klasse_nr: str
    bezeichnung: str
    richtung: str
    aktiv: bool
    created_at: datetime


class RabattsatzCreate(BaseModel):
    rabattgruppe_nr: str
    rabattklasse_nr: str
    richtung: str = Field(..., description="EK oder VK")
    rabatt_prozent: Decimal = Field(..., ge=0, le=100)
    ab_menge: Optional[Decimal] = Field(None, ge=0, description="Staffelmenge")
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None


class RabattsatzOut(BaseModel):
    id: str
    rabattgruppe_nr: str
    rabattklasse_nr: str
    richtung: str
    rabatt_prozent: Decimal
    ab_menge: Optional[Decimal]
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    created_at: datetime

