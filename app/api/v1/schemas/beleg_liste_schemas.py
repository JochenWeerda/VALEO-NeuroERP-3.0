"""Zeilenform der Belegliste (Familie ``beleg-liste``): eine Zeile je DocFlow-Beleg, Betraege nur mit Preisrecht."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class BelegListenZeile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    beleg_id: str
    belegart: str
    bezeichnung: str
    beleg_nr: str
    status: str
    belegdatum: Optional[str] = None
    buchungsdatum: Optional[str] = None
    partner_nr: Optional[str] = None
    partner_nummer: Optional[str] = None
    partner_name: Optional[str] = None
    referenz: Optional[str] = None
    version: int = 1
    netto: Optional[float] = None
    steuer: Optional[float] = None
    brutto: Optional[float] = None
    waehrung: Optional[str] = None


class BelegListe(BaseModel):
    items: list[BelegListenZeile]
    total: int
