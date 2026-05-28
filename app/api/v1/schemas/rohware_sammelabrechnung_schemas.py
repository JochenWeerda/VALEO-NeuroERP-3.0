"""Pydantic schemas for the rohware sammelabrechnung domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class RohwareSammelabrechnungOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class SammelabrechnungCreate(BaseModel):
    bezeichnung: str
    abrechnungsperiode: str  # e.g. "2026-08"
    harvest_acceptance_ids: list[str] = Field(..., min_length=2)
    abrechnungsschema_id: Optional[str] = None
    sammeldatum: Optional[str] = None  # ISO date, default today


class SammelabrechnungPositionOut(BaseModel):
    harvest_acceptance_id: str
    lieferant_id: Optional[str] = None
    artikel_nr: Optional[str] = None
    menge_kg: float = 0.0
    qualitaet_feuchte: Optional[float] = None
    qualitaet_besatz: Optional[float] = None
    abrechnungspreis_eur_t: float = 0.0
    abrechnungsbetrag_eur: float = 0.0


class SammelabrechnungOut(BaseModel):
    id: str
    bezeichnung: str
    abrechnungsperiode: str
    status: str  # ENTWURF / BERECHNET / GEBUCHT
    positionen: list[SammelabrechnungPositionOut] = []
    summe_menge_kg: float = 0.0
    summe_betrag_eur: float = 0.0
    erstellt_am: str

