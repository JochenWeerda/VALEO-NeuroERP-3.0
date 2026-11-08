"""Typisierte Antworten der Kontrakt-Familie (Masken-Familien ``kontrakt`` und ``kontrakt-liste``, 08.11.2026).

Jede Zeile traegt ``id`` (die Zeilenkennung der Maske, Ziel von ``{entity_id}`` in Zeilenaktionen). Mengen stehen in
der Kontrakteinheit (``einheit``); die Masken zeigen Masse in dt (``app/core/agrar_units.py``).
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class _Zeile(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ── Listen (Familie kontrakt-liste) ────────────────────────────────────────────

class KontraktUebersichtZeile(_Zeile):
    id: str
    contract_no: Optional[str] = None
    contract_type: Optional[str] = None
    party_id: Optional[str] = None
    partner_name: Optional[str] = None
    contract_date: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    total_quantity: float = 0
    rest_quantity: float = 0
    unit: Optional[str] = None
    status: Optional[str] = None
    pricing_model: Optional[str] = None
    artikel: Optional[str] = None
    preis: Optional[float] = None
    alarme: int = 0


class KontraktErfuellungZeile(_Zeile):
    id: str
    contract_no: Optional[str] = None
    typ: Optional[str] = None
    party_id: Optional[str] = None
    partner_name: Optional[str] = None
    einheit: Optional[str] = None
    status: Optional[str] = None
    valid_to: Optional[str] = None
    menge_kontrakt: Optional[float] = None
    abgerufen: Optional[float] = None
    offen: Optional[float] = None
    erfuellung_pct: float = 0
    erfuellung_status: Optional[str] = None
    ueberfaellig: bool = False


class KontraktMahnkandidatZeile(_Zeile):
    id: str
    contract_no: Optional[str] = None
    typ: Optional[str] = None
    party_id: Optional[str] = None
    partner_name: Optional[str] = None
    einheit: Optional[str] = None
    valid_to: Optional[str] = None
    tage_ueberfaellig: Optional[int] = None
    offen: float = 0
    letzte_mahnstufe: Optional[int] = None
    naechste_mahnstufe: int = 1


class EngagementArtikelZeile(_Zeile):
    id: str
    artikel: str
    einkauf_offen: float = 0
    verkauf_offen: float = 0
    netto: float = 0
    kontrakte: int = 0


class EngagementParteiZeile(_Zeile):
    id: str
    party_id: str
    partner_name: Optional[str] = None
    offen: float = 0
    kontrakte: int = 0


class KontraktAlarmZeile(_Zeile):
    id: str
    kontrakt_id: str
    contract_no: Optional[str] = None
    partner_name: Optional[str] = None
    alarm: str
    prioritaet: int
    text: str
    tage_bis_ablauf: Optional[int] = None
    valid_to: Optional[str] = None
    rest_quantity: float = 0
    unit: Optional[str] = None


class KontraktUebersichtListe(BaseModel):
    items: list[KontraktUebersichtZeile]
    total: int


class KontraktErfuellungListe(BaseModel):
    items: list[KontraktErfuellungZeile]
    total: int


class KontraktMahnkandidatListe(BaseModel):
    items: list[KontraktMahnkandidatZeile]
    total: int


class EngagementArtikelListe(BaseModel):
    items: list[EngagementArtikelZeile]
    total: int


class EngagementParteiListe(BaseModel):
    items: list[EngagementParteiZeile]
    total: int


class KontraktAlarmListe(BaseModel):
    items: list[KontraktAlarmZeile]
    total: int


# ── Vorgang je Kontrakt (Familie kontrakt) ─────────────────────────────────────

class KontraktVorgangKopf(BaseModel):
    """Ein Kopf fuer alle Vorgangsvarianten: Erfuellung, Fixierung, Abrechnung."""

    model_config = ConfigDict(extra="forbid")

    id: str
    contract_no: str
    contract_type: Optional[str] = None
    party_id: Optional[str] = None
    partner_name: Optional[str] = None
    status: Optional[str] = None
    einheit: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    ueberfaellig: bool = False
    preismodell: Optional[str] = None
    praemie_typ: Optional[str] = None
    praemie_wert: Optional[float] = None
    mindestpreis: Optional[float] = None
    basis: Optional[str] = None
    # Erfuellung
    menge_kontrakt: float = 0
    abgerufen: float = 0
    offen: float = 0
    erfuellung_pct: float = 0
    erfuellung_status: Optional[str] = None
    offene_luecken: int = 0
    # Fixierung
    fixiert: float = 0
    offen_zu_fixieren: float = 0
    fixierungsgrad_pct: float = 0
    bewertbar: bool = False
    bewertung_fixiert_eur: Optional[float] = None
    marktwert_offen_eur: Optional[float] = None
    # Abrechnung
    abgerechnet: float = 0
    offen_abruf: float = 0
    fixiert_aktiv: float = 0


class KontraktPositionZeile(_Zeile):
    id: str
    position_no: int
    artikel: Optional[str] = None
    bezeichnung: Optional[str] = None
    is_matif: bool = False
    menge_kontrakt: Optional[float] = None
    abgerufen: Optional[float] = None
    offen: Optional[float] = None
    erfuellung_status: Optional[str] = None
    erfuellung_pct: float = 0
    abweichung: bool = False
    fixiert: Optional[float] = None
    offen_zu_fixieren: Optional[float] = None
    fixierungsgrad_pct: float = 0
    avg_fixpreis_effektiv: Optional[float] = None
    symbol: Optional[str] = None
    notierung_preis: Optional[float] = None
    notierung_datum: Optional[str] = None
    markt_effektiv: Optional[float] = None
    bewertung_fixiert_eur: Optional[float] = None
    marktwert_offen_eur: Optional[float] = None
    einheit: Optional[str] = None


class KontraktLueckeZeile(_Zeile):
    id: str
    schwere: str
    text: str


class KontraktFixierungZeile(_Zeile):
    id: str
    fixing_no: int
    position_no: Optional[int] = None
    menge: Optional[float] = None
    matif_price: Optional[float] = None
    praemie: Optional[float] = None
    effektiv_preis: Optional[float] = None
    datum: Optional[str] = None
    referenz: Optional[str] = None
    notiz: Optional[str] = None
    bediener: Optional[str] = None
    status: str = "aktiv"
    storno_grund: Optional[str] = None
    einheit: Optional[str] = None


class KontraktBewegungZeile(_Zeile):
    id: str
    menge: Optional[float] = None
    datum: Optional[str] = None
    status: str
    invoice_no: Optional[str] = None
    settled_at: Optional[str] = None
    storno_grund: Optional[str] = None
    einheit: Optional[str] = None


class KontraktMahnungZeile(_Zeile):
    id: str
    mahnstufe: int
    offen: Optional[float] = None
    text: Optional[str] = None
    bediener: Optional[str] = None
    datum: Optional[str] = None


class KontraktPositionListe(BaseModel):
    items: list[KontraktPositionZeile]
    total: int


class KontraktLueckeListe(BaseModel):
    items: list[KontraktLueckeZeile]
    total: int


class KontraktFixierungListe(BaseModel):
    items: list[KontraktFixierungZeile]
    total: int


class KontraktBewegungListe(BaseModel):
    items: list[KontraktBewegungZeile]
    total: int


class KontraktMahnungListe(BaseModel):
    items: list[KontraktMahnungZeile]
    total: int
