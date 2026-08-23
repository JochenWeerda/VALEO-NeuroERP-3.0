"""Response-Schemas fuer Kontrakt-Lebenszyklus, Fixing und Settlement.

SPEC-P1-06 Welle 4: ersetzt ``response_model=Dict[str, Any]`` in
``app/api/v1/endpoints/kontrakt_actions.py``.

Feldlisten aus der Migration ``kontrakt_lifecycle_fixing_20260623``
(``domain_kontrakte.kontrakt_lifecycle``, ``kontrakt_fixings``,
``kontrakt_settlements``) sowie der Aufbereitung in
``kontrakt_fixing_service.get_fixing_summary``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class KontraktLifecycleOut(BaseSchema):
    """Zeile aus ``domain_kontrakte.kontrakt_lifecycle``."""

    id: Optional[str] = None
    kontrakt_id: Optional[str] = None
    tenant_id: Optional[str] = None
    kontrakt_nr: Optional[str] = None
    artikel_id: Optional[str] = None
    menge_t: Optional[float] = None
    preis_eur_t: Optional[float] = None
    lieferant_id: Optional[str] = None
    periode: Optional[str] = None
    status: Optional[str] = Field(default=None, description="ENTWURF und Folgestatus")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KontraktFixingOut(BaseSchema):
    """Zeile aus ``domain_kontrakte.kontrakt_fixings``."""

    id: Optional[str] = None
    kontrakt_id: Optional[str] = None
    tenant_id: Optional[str] = None
    fixing_datum: Optional[str] = None
    fixing_preis_eur_t: Optional[float] = None
    menge_t: Optional[float] = None
    markt: Optional[str] = Field(default=None, description="KASSA und weitere Maerkte")
    referenz: Optional[str] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None


class KontraktFixingSummaryOut(BaseSchema):
    """``GET /fixing/{kontrakt_id}/summary`` — Fixierungsstand des Kontrakts."""

    kontrakt_id: Optional[str] = None
    gefixte_menge_t: Optional[float] = None
    offene_menge_t: Optional[float] = None
    avg_fixing_preis_eur_t: Optional[float] = Field(
        default=None, description="Mengengewichteter Durchschnittspreis"
    )
    anzahl_fixings: Optional[int] = None
    vollstaendig_gefixt: Optional[bool] = None


class KontraktSettlementOut(BaseSchema):
    """Zeile aus ``domain_kontrakte.kontrakt_settlements``."""

    id: Optional[str] = None
    kontrakt_id: Optional[str] = None
    tenant_id: Optional[str] = None
    lieferung_datum: Optional[str] = None
    gelieferte_menge_t: Optional[float] = None
    abrechnungspreis_eur_t: Optional[float] = None
    netto_eur: Optional[float] = None
    referenz: Optional[str] = None
    status: Optional[str] = Field(default=None, description="OFFEN und Folgestatus")
    storno_grund: Optional[str] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
