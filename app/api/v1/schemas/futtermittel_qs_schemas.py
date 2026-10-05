"""Response-Schemas fuer Futtermittel-QS (FEED-QS-001).

SPEC-P1-06 Welle 2: ersetzt ``response_model=dict[str, Any]`` bzw.
``list[dict[str, Any]]`` in ``app/api/v1/endpoints/futtermittel_qs.py``.

Die Lese-Endpunkte liefern ``SELECT *`` ueber drei Tabellen in
``domain_shared``. Die Feldlisten entsprechen exakt der Migration
``feed_qs_wf_cockpit_repair_20260626``; spaetere ALTERs auf diese Tabellen
existieren nicht. Wird das DDL erweitert, muessen diese Schemas mitwachsen —
sonst filtert FastAPI die neuen Spalten still aus der Antwort.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class HaccpPlanOut(BaseSchema):
    """Zeile aus ``domain_shared.futtermittel_haccp_plaene``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    bezeichnung: Optional[str] = None
    gueltigkeit_von: Optional[date] = None
    gueltigkeit_bis: Optional[date] = None
    gefahrenanalyse: list[Any] = Field(default_factory=list, description="Gefahrenanalyse (JSONB)")
    ccp_liste: list[Any] = Field(default_factory=list, description="Kritische Lenkungspunkte (JSONB)")
    ueberwachung: list[Any] = Field(default_factory=list, description="Ueberwachungsmassnahmen (JSONB)")
    korrekturen: list[Any] = Field(default_factory=list, description="Korrekturmassnahmen (JSONB)")
    verifizierung: dict[str, Any] = Field(default_factory=dict, description="Verifizierung (JSONB)")
    aktiv: Optional[bool] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None


class VlogMeldungOut(BaseSchema):
    """Zeile aus ``domain_shared.futtermittel_vlog_meldungen``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    rezeptur_id: Optional[str] = None
    meldedatum: Optional[date] = None
    menge_kg: Optional[float] = None
    rohstoff_liste: list[Any] = Field(default_factory=list, description="Rohstoffe (JSONB)")
    gvo_frei: Optional[bool] = None
    zertifikat_nr: Optional[str] = None
    status: Optional[str] = Field(
        default=None, description="erstellt | gesendet | bestaetigt | abgelehnt"
    )
    notiz: Optional[str] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None


class QsPruefpunktOut(BaseSchema):
    """Zeile aus ``domain_shared.futtermittel_qs_pruefpunkte``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    periode: Optional[str] = Field(default=None, description="YYYY-MM oder YYYY")
    kategorie: Optional[str] = None
    punkt_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    anforderung: Optional[str] = None
    bestaetigt: Optional[bool] = None
    abweichung: Optional[str] = None
    massnahme: Optional[str] = None
    bestaetigt_am: Optional[datetime] = None
    bestaetigt_von: Optional[str] = None
    erstellt_am: Optional[datetime] = None


class QsAnlageOut(BaseSchema):
    """Bestaetigung einer Neuanlage oder Aktualisierung."""

    id: str = Field(description="ID des angelegten oder geaenderten Datensatzes")
    ok: bool = Field(default=True, description="True bei erfolgreicher Persistierung")


class VlogStatusOut(BaseSchema):
    """``PATCH /futtermittel/qs/vlog-meldungen/{id}/status``"""

    id: str
    status: str = Field(description="Gesetzter Status")


class PruefpunktBestaetigtOut(BaseSchema):
    """``POST /futtermittel/qs/leitfaden-pruefpunkte/{id}/bestaetigen``"""

    id: str
    bestaetigt: bool = Field(default=True)
