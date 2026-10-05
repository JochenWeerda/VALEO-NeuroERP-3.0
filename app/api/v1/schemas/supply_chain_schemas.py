"""Response-Schemas fuer die Lieferketten-Rueckverfolgbarkeit (DOM-SUPPLY-004).

SPEC-P1-06 Welle 3: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/supply_chain.py``.

Rueckgrat der Kette ist der Wiegeschein. Die Kettenknoten sind bewusst
heterogen — Wiegung, Annahme, Lager und Abrechnung teilen den Kopf
(stage/label/ref/status/menge_kg/zeitpunkt), fuehren aber je Stufe andere
``facts``. ``facts`` bleibt darum ein offenes ``dict`` als *Feldtyp*: das ist
etwas anderes als ein schwaches ``response_model``, denn Kopf und Struktur der
Antwort sind vollstaendig typisiert.

Feldlisten stammen aus ``supply_chain_trace_service``,
``supply_chain_event_service`` (Konstante ``_COLS``) und
``supply_chain_lot_service``.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class ChainNodeOut(BaseSchema):
    """Eine Stufe der Lieferkette."""

    stage: Optional[str] = Field(
        default=None, description="wiegung | annahme | lager | abrechnung"
    )
    label: Optional[str] = Field(default=None, description="Anzeigename der Stufe")
    ref: Optional[str] = Field(default=None, description="Belegnummer der Stufe")
    ref_id: Optional[str] = None
    status: Optional[str] = None
    menge_kg: Optional[float] = None
    zeitpunkt: Optional[str] = Field(default=None, description="ISO-Zeitstempel der Stufe")
    facts: dict[str, Any] = Field(
        default_factory=dict,
        description="Stufenspezifische Detailwerte — je Stufe unterschiedlich belegt",
    )


class MengenCheckOut(BaseSchema):
    """Mengenvergleich zweier benachbarter Stufen (Schwund-/Differenzpruefung)."""

    von: Optional[str] = None
    nach: Optional[str] = None
    menge_von_kg: Optional[float] = None
    menge_nach_kg: Optional[float] = None
    differenz_kg: Optional[float] = None
    differenz_pct: Optional[float] = None
    abweichung: Optional[bool] = Field(
        default=None, description="True, wenn die Differenz die Toleranz ueberschreitet"
    )
    hinweis: Optional[str] = None


class ChainLueckeOut(BaseSchema):
    """Fehlendes oder nicht freigegebenes Folgeobjekt in der Kette."""

    stufe: Optional[str] = None
    schwere: Optional[str] = Field(default=None, description="info | warnung")
    text: Optional[str] = None


class ChainEventOut(BaseSchema):
    """Zeile aus ``domain_inventory.supply_chain_events``.

    Feldliste = Konstante ``_COLS`` im Event-Service (ohne ``tenant_id``).
    """

    id: Optional[str] = None
    ticket_id: Optional[str] = None
    stage: Optional[str] = None
    ref_type: Optional[str] = Field(
        default=None,
        description="weighing_ticket | harvest_acceptance | silo_lot | settlement",
    )
    ref_id: Optional[str] = None
    ref_label: Optional[str] = None
    event_type: Optional[str] = Field(
        default=None,
        description=(
            "erfasst | freigegeben | eingelagert | abgerechnet | abweichung | "
            "korrektur | storniert | notiz"
        ),
    )
    status_from: Optional[str] = None
    status_to: Optional[str] = None
    menge_kg: Optional[float] = None
    abweichung_grund: Optional[str] = None
    payload: Optional[Any] = Field(default=None, description="Freies JSONB-Nutzlastfeld")
    bediener: Optional[str] = None
    source: Optional[str] = Field(default=None, description="backfill | auto | manual")
    occurred_at: Optional[str] = None
    created_at: Optional[str] = None


class KanonStatusOut(BaseSchema):
    """Kanonischer Uebergabestatus der Kette, abgeleitet aus dem Ereignis-Log."""

    status: Optional[str] = None
    rang: Optional[int] = Field(default=None, description="Rang zur Statusableitung, 0 = storniert/offen")


class ChainSummaryOut(BaseSchema):
    """Kopfkennzahlen der Kettensicht."""

    stufen: Optional[int] = None
    vollstaendig: Optional[bool] = None
    hat_mengen_abweichung: Optional[bool] = None
    offene_luecken: Optional[int] = None
    status: Optional[str] = None


class TraceabilityOut(BaseSchema):
    """``GET /supply-chain/traceability``.

    Im Nichttrefferfall sind nur ``found=false`` und ``detail`` gesetzt.
    """

    found: bool = Field(default=False)
    detail: Optional[str] = Field(default=None, description="Begruendung im Nichttrefferfall")
    ticket_id: Optional[str] = None
    ticket_nr: Optional[str] = None
    kette: list[ChainNodeOut] = Field(default_factory=list)
    mengen_konsistenz: list[MengenCheckOut] = Field(default_factory=list)
    luecken: list[ChainLueckeOut] = Field(default_factory=list)
    ereignisse: list[ChainEventOut] = Field(default_factory=list)
    kanon_status: Optional[KanonStatusOut] = None
    summary: Optional[ChainSummaryOut] = None


class TicketOverviewItemOut(BaseSchema):
    """Wiegeschein in der Ketten-Uebersicht (Picker)."""

    ticket_id: Optional[str] = None
    ticket_nr: Optional[str] = None
    datum: Optional[str] = None
    menge_kg: Optional[float] = None
    status: Optional[str] = None
    allokation: Optional[str] = None
    hat_annahme: Optional[bool] = None
    hat_lager: Optional[bool] = None
    hat_abrechnung: Optional[bool] = None
    vollstaendig: Optional[bool] = None


class TicketOverviewOut(BaseSchema):
    """``GET /supply-chain/traceability/tickets``"""

    items: list[TicketOverviewItemOut] = Field(default_factory=list)


class ChainSyncOut(BaseSchema):
    """``POST /supply-chain/traceability/sync`` — idempotenter Backfill."""

    synced: Optional[int] = Field(default=None, description="Neu geschriebene Ereignisse")
    total: Optional[int] = Field(default=None, description="Ereignisse nach dem Lauf")
    ticket_id: Optional[str] = None
    detail: Optional[str] = Field(default=None, description="Begruendung, wenn nichts lief")


class ChainEventAckOut(BaseSchema):
    """``POST /supply-chain/events``"""

    ok: bool = Field(default=False)
    detail: Optional[str] = Field(default=None, description="Begruendung, wenn ok=false")
    event: Optional[ChainEventOut] = None


class LotActionOut(BaseSchema):
    """Antwort der Lot-Folgeaktionen Sperre / QS-Freigabe / Schwund.

    ``bestand_kg`` liefert nur die Schwundbuchung.
    """

    ok: bool = Field(default=True)
    lot: Optional[str] = Field(default=None, description="Virtuelle Lot-Nummer")
    status: Optional[str] = None
    bestand_kg: Optional[float] = Field(
        default=None, description="Restbestand nach Schwundbuchung"
    )
    event: Optional[ChainEventOut] = None


class ChainCancelOut(BaseSchema):
    """``POST /supply-chain/traceability/cancel`` — durchgaengiger Ketten-Storno."""

    ok: bool = Field(default=True)
    ticket_id: Optional[str] = None
    ticket_nr: Optional[str] = None
    stornierte_lots: list[str] = Field(default_factory=list)
    status: Optional[str] = None
    event: Optional[ChainEventOut] = None
