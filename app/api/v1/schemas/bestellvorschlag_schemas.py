"""Zeilenformen der Bestellvorschlag-Wege (Familie ``bestellvorschlag``, 09.11.2026)."""
from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict as _ConfigDict

from app.api.v1.schemas.base import BaseSchema


class VorschlagsZeileOut(BaseSchema):
    """Eine Zeile der Vorschlagsrechnung (Lager, Verkauf, Rohware); dieselbe Grundform fuer alle drei Wege."""

    model_config = _ConfigDict(extra="allow")

    article_id: str
    artikel_nr: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    artikel_gruppe: Optional[str] = None
    einheit: Optional[str] = None
    ist_bestand: float = 0.0
    mindestbestand: float = 0.0
    maximalbestand: float = 0.0
    meldebestand: Optional[float] = None
    offene_auftraege: float = 0.0
    bedarf: float = 0.0
    vorschlag_menge: float = 0.0
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    letzter_preis: Optional[float] = None
    preis_einheit: Optional[str] = None
    letzter_kauf_datum: Optional[str] = None
    wiederbeschaffungs_tage: Optional[int] = None
    reichweite_tage: Optional[float] = None


class GespeicherterVorschlagOut(BaseSchema):
    """Ein gespeicherter Bestellvorschlag (Kopf)."""

    model_config = _ConfigDict(extra="allow")

    id: str
    bezeichnung: Optional[str] = None
    vorschlag_typ: Optional[str] = None
    status: Optional[str] = None
    datum: Optional[str] = None
    created_at: Optional[str] = None
    erstellt_von: Optional[str] = None
    niederlassung_id: Optional[str] = None
    positionen_anz: int = 0
