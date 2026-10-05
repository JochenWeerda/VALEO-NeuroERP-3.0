"""Response-Schemas fuer Portal-APIs (SPEC-P1-06 Welle 13).

Ersetzt schwache ``response_model`` in:
- ``portal_intelligence.py``
- ``portal_interessent.py``
- ``portal_lohndienst.py``
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── Intelligence / Cross-Sell ───────────────────────────────────────────────


class PortalEmpfehlungOut(BaseSchema):
    empfehlung_id: Optional[str] = None
    tenant_id: Optional[str] = None
    kunden_nr: Optional[str] = None
    typ: Optional[str] = None
    prioritaet: Optional[str] = None
    titel: Optional[str] = None
    beschreibung: Optional[str] = None
    cta_label: Optional[str] = None
    cta_ziel: Optional[str] = None
    kontext_schluessel: Optional[str] = None
    kontext_wert: Optional[str] = None
    artikel_id: Optional[str] = None
    betrag_indikativ: Optional[float] = None
    gueltig_bis: Optional[str] = None
    gesehen: Optional[bool] = None
    erstellt_am: Optional[str] = None


class PortalEmpfehlungListOut(BaseSchema):
    items: list[PortalEmpfehlungOut] = Field(default_factory=list)
    count: Optional[int] = None


class PortalEmpfehlungSummaryOut(BaseSchema):
    kunden_nr: Optional[str] = None
    gesamt: Optional[int] = None
    ungesehen: Optional[int] = None
    nach_typ: dict[str, int] = Field(default_factory=dict)


class PortalEmpfehlungAckOut(BaseSchema):
    ok: Optional[bool] = None


class PortalEmpfehlungGeneratedOut(BaseSchema):
    neue_empfehlungen: list[PortalEmpfehlungOut] = Field(default_factory=list)
    count: Optional[int] = None


# ── Interessenten ───────────────────────────────────────────────────────────


class PortalInteressentOut(BaseSchema):
    interessent_id: Optional[str] = None
    tenant_id: Optional[str] = None
    status: Optional[str] = None
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    vollname: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    betrieb_name: Optional[str] = None
    betrieb_typ: Optional[str] = None
    flaeche_ha: Optional[float] = None
    hauptkulturen: list[str] = Field(default_factory=list)
    tiere_anzahl: Optional[int] = None
    tierart: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    interesse_themen: list[str] = Field(default_factory=list)
    anmerkung: Optional[str] = None
    zugewiesen_an: Optional[str] = None
    kunden_nr: Optional[str] = None
    qualifiziert_am: Optional[str] = None
    konvertiert_am: Optional[str] = None
    erstellt_am: Optional[str] = None
    aktualisiert_am: Optional[str] = None


class PortalInteressentListOut(BaseSchema):
    items: list[PortalInteressentOut] = Field(default_factory=list)
    count: Optional[int] = None


# ── Lohndienst ──────────────────────────────────────────────────────────────


class PortalLohndienstAuftragOut(BaseSchema):
    auftrag_id: Optional[str] = None
    tenant_id: Optional[str] = None
    kunden_nr: Optional[str] = None
    typ: Optional[str] = None
    typ_bezeichnung: Optional[str] = None
    status: Optional[str] = None
    schlag_ids: list[str] = Field(default_factory=list)
    schlag_beschreibung: Optional[str] = None
    flaeche_ha: Optional[float] = None
    wunsch_datum: Optional[str] = None
    geplant_datum: Optional[str] = None
    getreide_art: Optional[str] = None
    menge_dt: Optional[float] = None
    tierart: Optional[str] = None
    tiere_anzahl: Optional[int] = None
    psm_mittel: list[str] = Field(default_factory=list)
    kultur: Optional[str] = None
    anmerkung: Optional[str] = None
    innendienst_notiz: Optional[str] = None
    preis_indikativ_eur: Optional[float] = None
    erstellt_am: Optional[str] = None
    aktualisiert_am: Optional[str] = None
    abgeschlossen: Optional[bool] = None


class PortalLohndienstListOut(BaseSchema):
    items: list[PortalLohndienstAuftragOut] = Field(default_factory=list)
    count: Optional[int] = None
