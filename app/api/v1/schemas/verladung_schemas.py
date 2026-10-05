"""Auto-generated domain schemas for verladung.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from typing import Optional

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict, Field


class VerladungOut(BaseSchema):
    """Verladung führt Fahrzeug, Ware, Menge und Orte. Der Frachtbrief wird daraus erzeugt."""

    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    kennzeichen: Optional[str] = Field(default=None, description="Zugmaschine")
    fahrer: Optional[str] = None
    artikel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    ladeort: Optional[str] = Field(default=None, description="Übernahmeort")
    zielort: Optional[str] = Field(default=None, description="Ablieferstelle")
    kunde: Optional[str] = Field(default=None, description="Empfänger der Beförderung")
    lieferschein_nr: Optional[str] = Field(default=None, description="Referenz auf den Warenbeleg")
    datum: Optional[str] = None
    status: Optional[str] = None
