"""Pydantic schemas for the erloeskennziffern domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ErloeskennzifferCreate(BaseModel):
    ekz_nr: str = Field(..., max_length=20)
    bezeichnung: str


class ErloeskennzifferOut(BaseModel):
    id: str
    ekz_nr: str
    bezeichnung: str
    aktiv: bool
    created_at: datetime


class ErloeskontenzuordnungCreate(BaseModel):
    ekz_id: str
    gueltig_ab: date
    steuerschluessel: Optional[str] = None
    erlösklasse: Optional[str] = None
    steuergruppe: Optional[str] = None
    buchungsklasse: Optional[str] = None
    konto_erloese: Optional[str] = None
    konto_aufwand: Optional[str] = None
    konto_umsatzsteuer: Optional[str] = None
    konto_vorsteuer: Optional[str] = None


class ErloeskontenzuordnungOut(BaseModel):
    id: str
    ekz_id: str
    gueltig_ab: date
    steuerschluessel: Optional[str]
    erlösklasse: Optional[str]
    steuergruppe: Optional[str]
    buchungsklasse: Optional[str]
    konto_erloese: Optional[str]
    konto_aufwand: Optional[str]
    konto_umsatzsteuer: Optional[str]
    konto_vorsteuer: Optional[str]
    created_at: datetime

