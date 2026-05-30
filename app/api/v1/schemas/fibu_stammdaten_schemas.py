"""Pydantic schemas for the fibu stammdaten domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ZahlungsformularCreate(BaseModel):
    formular_nr: str = Field(..., max_length=20)
    bezeichnung: str
    formularklasse: str
    bank_blz: Optional[str] = None
    bank_iban: Optional[str] = None
    formulareinrichtung: Optional[str] = None

    def model_post_init(self, __context):
        if self.formularklasse not in GUELTIGE_FORMULARKLASSEN:
            raise ValueError(f"Ungültige Formularklasse: {self.formularklasse}")


class ZahlungsformularOut(BaseModel):
    id: str
    formular_nr: str
    bezeichnung: str
    formularklasse: str
    bank_blz: Optional[str]
    bank_iban: Optional[str]
    formulareinrichtung: Optional[str]
    aktiv: bool
    created_at: datetime


class ZinsgruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    zinssatz: Decimal = Field(..., ge=0, le=100)
    zinsmethode: str = "act_360"
    schwellwert_tage: int = Field(0, ge=0)
    konto_zinsen: Optional[str] = None
    konto_zinsabschlagsteuer: Optional[str] = None

    def model_post_init(self, __context):
        if self.zinsmethode not in GUELTIGE_ZINSMETHODEN:
            raise ValueError(f"Ungültige Zinsmethode: {self.zinsmethode}")


class ZinsgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    zinssatz: Decimal
    zinsmethode: str
    schwellwert_tage: int
    konto_zinsen: Optional[str]
    konto_zinsabschlagsteuer: Optional[str]
    aktiv: bool
    created_at: datetime


class LeergutArtCreate(BaseModel):
    art_nr: str = Field(..., max_length=20)
    bezeichnung: str
    leergut_typ: str = "palette"
    pfandwert: Optional[Decimal] = Field(None, ge=0)
    konto_leergut: Optional[str] = None

    def model_post_init(self, __context):
        if self.leergut_typ not in GUELTIGE_LEERGUT_ARTEN:
            raise ValueError(f"Ungültiger Leergut-Typ: {self.leergut_typ}")


class LeergutArtOut(BaseModel):
    id: str
    art_nr: str
    bezeichnung: str
    leergut_typ: str
    pfandwert: Optional[Decimal]
    konto_leergut: Optional[str]
    aktiv: bool
    created_at: datetime

