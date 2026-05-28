"""Pydantic schemas for the agrar maschinen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AgrarMaschinenOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class MaschineCreate(BaseModel):
    name: str
    typ: str                         # Traktor | Mähdrescher | Anhänger | Spritze | Grubber | Sonstiges
    hersteller: Optional[str] = None
    modell: Optional[str] = None
    baujahr: Optional[int] = None
    kennzeichen: Optional[str] = None
    fahrgestellnummer: Optional[str] = None
    leistung_kw: Optional[float] = None
    betriebsstunden: float = 0.0
    naechste_wartung_stunden: Optional[float] = None
    naechste_wartung_datum: Optional[datetime] = None
    status: str = "verfuegbar"       # verfuegbar | im-einsatz | werkstatt | stillgelegt
    standort: Optional[str] = None
    customer_id: Optional[str] = None  # None = eigene Maschine des Landhandels
    notiz: Optional[str] = None


class MaschineUpdate(BaseModel):
    name: Optional[str] = None
    typ: Optional[str] = None
    hersteller: Optional[str] = None
    modell: Optional[str] = None
    baujahr: Optional[int] = None
    kennzeichen: Optional[str] = None
    fahrgestellnummer: Optional[str] = None
    leistung_kw: Optional[float] = None
    naechste_wartung_stunden: Optional[float] = None
    naechste_wartung_datum: Optional[datetime] = None
    standort: Optional[str] = None
    customer_id: Optional[str] = None
    notiz: Optional[str] = None

