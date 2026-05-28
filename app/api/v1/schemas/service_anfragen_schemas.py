"""Auto-generated domain schemas for service anfragen.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class ServiceAnfragenOut(BaseSchema):
    """Response schema for service anfragen endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class ServiceAnfrageCreate(BaseModel):
    nummer: str | None = None
    kunde: str
    betreff: str
    beschreibung: str | None = None
    prioritaet: str = "normal"  # hoch | normal | niedrig
    kategorie: str | None = None


class ServiceAnfrageUpdate(BaseModel):
    kunde: str | None = None
    betreff: str | None = None
    beschreibung: str | None = None
    prioritaet: str | None = None
    kategorie: str | None = None
    status: str | None = None


class RueckmeldungCreate(BaseModel):
    anfrage_id: str
    text: str
    bewertet_von: str | None = None
    bewertung: int | None = None  # 1-5


class AbschlussCreate(BaseModel):
    anfrage_id: str
    abschluss_grund: str | None = None
    notiz: str | None = None

