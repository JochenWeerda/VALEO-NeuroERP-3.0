"""Pydantic schemas for the vertreterstamm domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class VertreterCreate(BaseModel):
    vertreter_nr: str = Field(..., max_length=20)
    name: str
    vorname: Optional[str] = None
    kuerzel: Optional[str] = Field(None, max_length=10)
    telefon: Optional[str] = None
    email: Optional[str] = None
    vertretergruppe_nr: Optional[str] = None
    provisionsgruppe_nr: Optional[str] = None
    gebiet: Optional[str] = None


class VertreterOut(BaseModel):
    id: str
    vertreter_nr: str
    name: str
    vorname: Optional[str]
    kuerzel: Optional[str]
    telefon: Optional[str]
    email: Optional[str]
    vertretergruppe_nr: Optional[str]
    provisionsgruppe_nr: Optional[str]
    gebiet: Optional[str]
    aktiv: bool
    created_at: datetime
    updated_at: datetime


class VertretergruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str


class VertretergruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    aktiv: bool
    created_at: datetime

