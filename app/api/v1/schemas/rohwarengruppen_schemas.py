from __future__ import annotations

from typing import Any, List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.api.v1.schemas.base import BaseSchema

class RohwarengruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    artikel_nr: Optional[str] = None
    ek_aktiv: bool = True
    vk_aktiv: bool = False
    waehrung: str = Field(default="EUR", max_length=3)
    mengeneinheit: Optional[str] = None


class RohwarengruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    artikel_nr: Optional[str]
    ek_aktiv: bool
    vk_aktiv: bool
    waehrung: str
    mengeneinheit: Optional[str]
    aktiv: bool
    created_at: datetime


class AbrechnungsschemaCreate(BaseModel):
    schema_nr: str = Field(..., max_length=20)
    bezeichnung: str
    gruppe_id: str
    artikel_nr: Optional[str] = None


class AbrechnungsschemaOut(BaseModel):
    id: str
    schema_nr: str
    bezeichnung: str
    gruppe_id: str
    artikel_nr: Optional[str]
    aktiv: bool
    created_at: datetime


class RohwareQualitaetCreate(BaseModel):
    qualitaet_nr: str = Field(..., max_length=20)
    bezeichnung: str
    gruppe_id: str
    schema_id: Optional[str] = None
    basis_wert: Optional[Decimal] = None
    basis_wert_bis: Optional[Decimal] = None
    einheit: Optional[str] = None
    position_typ: str = Field(default="qualitaet")


class RohwareQualitaetOut(BaseModel):
    id: str
    qualitaet_nr: str
    bezeichnung: str
    gruppe_id: str
    schema_id: Optional[str]
    basis_wert: Optional[Decimal]
    basis_wert_bis: Optional[Decimal]
    einheit: Optional[str]
    position_typ: str
    aktiv: bool
    created_at: datetime


class StaffelZeileCreate(BaseModel):
    zeile_nr: int
    bis_wert: Decimal
    umrechnungsfaktor: Decimal = Field(..., description="Faktor für dieses Intervall")


class StaffelZeileOut(BaseModel):
    id: str
    zeile_nr: int
    bis_wert: Decimal
    umrechnungsfaktor: Decimal


class ZaStaffelOut(BaseModel):
    id: str
    staffel_nr: str
    bezeichnung: str
    gruppe_id: str
    qualitaet_id: Optional[str]
    ergebnis_typ: str
    abrechnung_typ: str
    basiserweiterung: Decimal
    aktiv: bool
    created_at: datetime
    zeilen: list[StaffelZeileOut] = []

