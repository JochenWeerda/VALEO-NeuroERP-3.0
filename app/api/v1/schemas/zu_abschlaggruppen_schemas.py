"""Pydantic schemas for the zu abschlaggruppen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ZuAbschlaggruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    richtung: str = "vk"

    def model_post_init(self, __context):
        if self.richtung not in GUELTIGE_RICHTUNG:
            raise ValueError(f"Ungültige Richtung: {self.richtung}")


class ZuAbschlaggruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    richtung: str
    aktiv: bool
    created_at: datetime


class ZuAbschlagklasseCreate(BaseModel):
    klasse_nr: str = Field(..., max_length=20)
    bezeichnung: str
    richtung: str = "vk"

    def model_post_init(self, __context):
        if self.richtung not in GUELTIGE_RICHTUNG:
            raise ValueError(f"Ungültige Richtung: {self.richtung}")


class ZuAbschlagklasseOut(BaseModel):
    id: str
    klasse_nr: str
    bezeichnung: str
    richtung: str
    aktiv: bool
    created_at: datetime


class ZuAbschlagKonditionCreate(BaseModel):
    gruppe_id: str
    klasse_id: str
    kondition_typ: str = "prozent"
    wert: Decimal = Field(..., description="Prozentsatz oder Betrag (negativ = Abschlag)")
    gueltig_ab: date
    gueltig_bis: Optional[date] = None
    beschreibung: Optional[str] = None

    def model_post_init(self, __context):
        if self.kondition_typ not in GUELTIGE_KONDITION_TYP:
            raise ValueError(f"Ungültiger kondition_typ: {self.kondition_typ}")


class ZuAbschlagKonditionOut(BaseModel):
    id: str
    gruppe_id: str
    klasse_id: str
    kondition_typ: str
    wert: Decimal
    gueltig_ab: date
    gueltig_bis: Optional[date]
    beschreibung: Optional[str]
    aktiv: bool
    created_at: datetime

