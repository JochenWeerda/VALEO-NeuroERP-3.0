"""Eingabeschemas des Portal-Feldbuchs (aus ``app/api/v1/endpoints/portal_feldbuch.py`` ausgelagert)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class _SchlagDuevFields(BaseModel):
    # AS-W2 (DüV): N-Düngebedarf-Grundlagen
    n_sollwert_kg_ha: Optional[float] = None
    ertragsniveau_dt_ha: Optional[float] = None
    # AS-W5 (DüV): Nmin + Bodenuntersuchung
    nmin_fruehjahr_kg_ha: Optional[float] = None
    nmin_in_bedarf: Optional[bool] = None
    boden_p2o5_mg: Optional[float] = None
    boden_k2o_mg: Optional[float] = None
    boden_mgo_mg: Optional[float] = None
    boden_ph: Optional[float] = None
    boden_datum: Optional[datetime] = None
    versorgungsstufe: Optional[str] = None


class PortalSchlagCreate(_SchlagDuevFields):
    name: str
    flik: Optional[str] = None
    flaeche: float
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: str = "aktiv"
    wirtschaftsjahr: Optional[int] = None


class PortalSchlagUpdate(_SchlagDuevFields):
    name: Optional[str] = None
    flik: Optional[str] = None
    flaeche: Optional[float] = None
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: Optional[str] = None
    wirtschaftsjahr: Optional[int] = None


# Nicht-Spalten-Eingaben (nur zur Berechnung), werden vor dem Persistieren entfernt.
_NUTRIENT_INPUT_KEYS = ("n_gehalt", "p2o5_gehalt", "k2o_gehalt", "mgo_gehalt", "s_gehalt", "preis_je_einheit")


class PortalMassnahmeBase(BaseModel):
    # AS-W1: Düngung — Reinnährstoffe werden aus Gehalten (% des Produkts) berechnet
    n_gehalt: Optional[float] = None
    p2o5_gehalt: Optional[float] = None
    k2o_gehalt: Optional[float] = None
    mgo_gehalt: Optional[float] = None
    s_gehalt: Optional[float] = None
    preis_je_einheit: Optional[float] = None   # €/kg bzw. €/l Produkt → kosten_eur
    duenger_form: Optional[str] = None         # 'M' | 'O'
    # AS-W4: Pflanzenschutz
    wirkungsbereich: Optional[str] = None
    begruendung: Optional[str] = None
    sachkunde_nummer: Optional[str] = None
    sachkunde_gueltig_bis: Optional[datetime] = None
    # AS-W6: Ernte
    ertrag_dt_ha: Optional[float] = None
    qualitaet: Optional[str] = None
    erloes_eur: Optional[float] = None
    nebenleistung_eur: Optional[float] = None
    kosten_eur: Optional[float] = None
    # Open-Gaps
    sorte: Optional[str] = None
    wassermenge_mm: Optional[float] = None
    aum_code: Optional[str] = None
    register_daten: Optional[dict[str, Any]] = None
    lager_artikel_id: Optional[str] = None
    lager_charge: Optional[str] = None
    lager_verbrauch: Optional[float] = None
    client_ref: Optional[str] = None
    mittel_id: Optional[str] = None
    mittel_typ: Optional[str] = None


class PortalMassnahmeCreate(PortalMassnahmeBase):
    schlag_id: Optional[str] = None
    datum: datetime
    uhrzeit: Optional[str] = None
    typ: str
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    bemerkung: Optional[str] = None


class PortalMassnahmeUpdate(PortalMassnahmeBase):
    schlag_id: Optional[str] = None
    datum: Optional[datetime] = None
    uhrzeit: Optional[str] = None
    typ: Optional[str] = None
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    bemerkung: Optional[str] = None
