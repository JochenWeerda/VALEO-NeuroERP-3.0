"""Response-Schemas fuer SEPA, Ratenzahlung und Mahnstufen.

SPEC-P1-06 Welle 5: ersetzt ``response_model=dict[str, Any]`` bei den sieben
Aktions-Endpunkten in ``app/api/v1/endpoints/finance_actions.py``.

Feldlisten aus der Migration ``finance_sepa_ratenzahlung_20260623`` und den
Rueckgaben von ``finance_sepa_service``, ``finance_ratenzahlung_service`` und
``finance_mahnstufe_service``. Mehrere Endpunkte haben einen Idempotenzpfad,
der die gespeicherte Zeile spreizt — die Schemas fuehren deshalb die
Vereinigung aus Tabellenspalten und konstruierten Feldern.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class SepaMandatOut(BaseSchema):
    """SEPA-Mandat — Anlage und Widerruf.

    Der Widerruf spreizt die gespeicherte Zeile aus
    ``domain_finance.finance_sepa_mandate`` und ergaenzt ``idempotent``.
    """

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    mandat_ref: Optional[str] = None
    glaeubiger_id: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    typ: Optional[str] = Field(default=None, description="CORE oder B2B")
    status: Optional[str] = Field(default=None, description="AKTIV | WIDERRUFEN")
    erteilung_am: Optional[date] = None
    widerruf_am: Optional[date] = None
    created_at: Optional[datetime] = None
    idempotent: Optional[bool] = Field(
        default=None, description="True, wenn das Mandat bereits widerrufen war"
    )


class SepaBatchOut(BaseSchema):
    """``POST /sepa/batches`` — erzeugter Lastschrift-Stapel."""

    id: Optional[str] = None
    faellig_am: Optional[str] = None
    gesamt_eur: Optional[float] = None
    anzahl_eintraege: Optional[int] = None
    status: Optional[str] = None
    xml_payload: Optional[str] = Field(default=None, description="pain.008-Nutzlast")


class RatenzahlungsplanOut(BaseSchema):
    """``POST /ratenzahlung/plaene``.

    Der Idempotenzpfad liefert die gespeicherte Planzeile, der Neuanlagepfad
    zusaetzlich ``rate_ids``.
    """

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    op_id: Optional[str] = Field(default=None, description="Offener Posten")
    gesamt_eur: Optional[float] = None
    anzahl_raten: Optional[int] = None
    restbetrag_eur: Optional[float] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    rate_ids: list[str] = Field(default_factory=list, description="IDs der angelegten Raten")
    idempotent: Optional[bool] = None


class RateOut(BaseSchema):
    """``POST /ratenzahlung/raten/{id}/buchen``.

    Zeile aus ``domain_finance.finance_raten`` plus der Planfortschreibung.
    """

    id: Optional[str] = None
    plan_id: Optional[str] = None
    tenant_id: Optional[str] = None
    rate_nr: Optional[int] = None
    betrag_eur: Optional[float] = None
    faellig_am: Optional[date] = None
    bezahlt_am: Optional[date] = None
    status: Optional[str] = Field(default=None, description="OFFEN | BEZAHLT")
    created_at: Optional[datetime] = None
    plan_restbetrag_eur: Optional[float] = Field(
        default=None, description="Restbetrag des Plans nach dieser Buchung"
    )
    plan_status: Optional[str] = None
    idempotent: Optional[bool] = None


class MahnstufeOut(BaseSchema):
    """``POST /mahnstufe/{rechnungsnr}/eskalieren``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    rechnungsnr: Optional[str] = None
    stufe: Optional[str] = None
    vorherige_stufe: Optional[str] = None
    bearbeitungsgebuehr_eur: Optional[float] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None


class MahnstufenTrailOut(BaseSchema):
    """``GET /mahnstufe/{rechnungsnr}/trail`` — chronologischer Verlauf."""

    rechnungsnr: Optional[str] = None
    trail: list[MahnstufeOut] = Field(default_factory=list)
    count: Optional[int] = None
