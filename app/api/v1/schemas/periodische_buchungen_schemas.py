"""Pydantic schemas for the periodische buchungen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class PeriodischeBuchungCreate(BaseModel):
    bezeichnung: str
    vorgangsklasse: str = "ZA"
    konto: str
    gegenkonto: str
    buchungstext: Optional[str] = None
    betrag: Decimal = Field(..., gt=0)
    turnus: str = "monatlich"
    gueltig_ab: date
    gueltig_bis: Optional[date] = None
    gesperrt: bool = False
    kostenstelle: Optional[str] = None

    def model_post_init(self, __context):
        if self.turnus not in GUELTIGE_TURNUS:
            raise ValueError(f"Ungültiger Turnus: {self.turnus}")
        if self.vorgangsklasse not in GUELTIGE_VORGANGSKLASSEN:
            raise ValueError(f"Ungültige Vorgangsklasse: {self.vorgangsklasse}")


class PeriodischeBuchungOut(BaseModel):
    id: str
    bezeichnung: str
    vorgangsklasse: str
    konto: str
    gegenkonto: str
    buchungstext: Optional[str]
    betrag: Decimal
    turnus: str
    gueltig_ab: date
    gueltig_bis: Optional[date]
    gesperrt: bool
    kostenstelle: Optional[str]
    aktiv: bool
    created_at: datetime


class FaelligBelegOut(BaseModel):
    id: str
    bezeichnung: str
    konto: str
    gegenkonto: str
    betrag: Decimal
    vorgangsklasse: str
    turnus: str
    gueltig_ab: date

