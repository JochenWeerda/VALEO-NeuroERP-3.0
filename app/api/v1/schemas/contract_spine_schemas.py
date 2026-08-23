"""Response-Schemas fuer den Kontrakt-Spine (DOM-CON-004).

SPEC-P1-06 Welle 6: ersetzt ``response_model=dict[str, Any]`` in den drei
Endpoint-Dateien ``contract_fixing.py``, ``contract_engagement.py`` und
``contract_settlement.py``.

Bewusst ein gemeinsames Modul statt drei: die Dateien bilden eine Fachkette
(Fixierung -> Engagement -> Settlement) und teilen sich Bausteine. ``FixingOut``
etwa erscheint in ``GET /fixing/list``, verschachtelt im Fixierungs-Arbeitsraum
und in reduzierter Form im Settlement-Status — als ein Schema bleibt die
Bedeutung ueber die Kette hinweg dieselbe.

Feldlisten aus ``contract_fixing_service``, ``contract_engagement_service`` und
``contract_settlement_service``.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── Gemeinsame Bausteine ────────────────────────────────────────────────────


class FixingOut(BaseSchema):
    """Eine Teilfixierung.

    ``GET /fixing/list`` und der Arbeitsraum liefern die volle Form; der
    Settlement-Status eine reduzierte mit ``fixing_id`` und ``status``.
    """

    fixing_no: Optional[int] = None
    fixing_id: Optional[str] = None
    line_id: Optional[str] = None
    menge: Optional[float] = None
    matif_price: Optional[float] = None
    praemie: Optional[float] = None
    effektiv_preis: Optional[float] = Field(
        default=None, description="MATIF-Preis plus Praemie"
    )
    datum: Optional[str] = None
    referenz: Optional[str] = Field(default=None, description="MATIF-Referenz")
    notiz: Optional[str] = None
    bediener: Optional[str] = None
    status: Optional[str] = Field(default=None, description="aktiv | storniert")
    storno_grund: Optional[str] = None


class QuoteOut(BaseSchema):
    """Marktnotierung als Bewertungsbasis."""

    preis: Optional[float] = None
    datum: Optional[str] = None
    markt_effektiv: Optional[float] = Field(
        default=None, description="Notierung plus Praemie"
    )
    quelle: Optional[str] = None


# ── Fixierungs-Arbeitsraum ──────────────────────────────────────────────────


class FixingPositionOut(BaseSchema):
    """Kontraktposition im Fixierungs-Arbeitsraum."""

    position_no: Optional[int] = None
    line_id: Optional[str] = None
    artikel: Optional[str] = None
    bezeichnung: Optional[str] = None
    is_matif: Optional[bool] = None
    menge_kontrakt: Optional[float] = None
    fixiert: Optional[float] = None
    offen_zu_fixieren: Optional[float] = None
    fixierungsgrad_pct: Optional[float] = None
    avg_fixpreis_effektiv: Optional[float] = None
    symbol: Optional[str] = None
    notierung: Optional[QuoteOut] = None
    bewertung_fixiert_eur: Optional[float] = None
    marktwert_offen_eur: Optional[float] = None
    fixings: list[FixingOut] = Field(default_factory=list)


class FixingPricingOut(BaseSchema):
    """Preismodell des Kontrakts."""

    modell: Optional[str] = None
    praemie_typ: Optional[str] = None
    praemie_wert: Optional[float] = None
    basis: Optional[str] = Field(default=None, description="Basis-/MATIF-Referenz")


class FixingSummaryOut(BaseSchema):
    """Kopfkennzahlen des Arbeitsraums."""

    menge_kontrakt: Optional[float] = None
    fixiert: Optional[float] = None
    offen_zu_fixieren: Optional[float] = None
    fixierungsgrad_pct: Optional[float] = None
    bewertbar: Optional[bool] = Field(
        default=None, description="False ohne Marktnotierung"
    )
    bewertung_fixiert_eur: Optional[float] = None
    marktwert_offen_eur: Optional[float] = None


class FixingWorkspaceOut(BaseSchema):
    """``GET /contracts/fixing/workspace``.

    Im Nichttrefferfall sind nur ``found=false`` und ``detail`` gesetzt.
    """

    found: bool = Field(default=False)
    detail: Optional[str] = None
    contract_no: Optional[str] = None
    contract_type: Optional[str] = None
    party_id: Optional[str] = None
    einheit: Optional[str] = None
    status: Optional[str] = None
    pricing: Optional[FixingPricingOut] = None
    positionen: list[FixingPositionOut] = Field(default_factory=list)
    summary: Optional[FixingSummaryOut] = None


class FixingListOut(BaseSchema):
    """``GET /contracts/fixing/list``"""

    items: list[FixingOut] = Field(default_factory=list)


class FixingCreatedOut(BaseSchema):
    """``POST /contracts/fixing`` — angelegte Teilfixierung."""

    ok: bool = Field(default=True)
    fixing_id: Optional[str] = None
    fixing_no: Optional[int] = None
    contract_no: Optional[str] = None
    position_no: Optional[int] = None
    menge: Optional[float] = None
    matif_price: Optional[float] = None
    praemie: Optional[float] = None
    effektiv_preis: Optional[float] = None
    offen_nach: Optional[float] = Field(
        default=None, description="Restmenge zur Fixierung nach dieser Buchung"
    )


class QuoteUpsertOut(BaseSchema):
    """``POST /contracts/matif-quote``"""

    ok: bool = Field(default=True)
    symbol: Optional[str] = None
    quote_date: Optional[str] = None
    price: Optional[float] = None


# ── Engagement und Kontraktmahnung ──────────────────────────────────────────


class EngagementArticleOut(BaseSchema):
    """Offene Menge je Artikel mit Nettoposition."""

    artikel: Optional[str] = None
    einkauf_offen: Optional[float] = None
    verkauf_offen: Optional[float] = None
    netto: Optional[float] = Field(
        default=None, description="Einkauf minus Verkauf — die Nettoposition"
    )
    kontrakte: Optional[int] = None


class EngagementPartyOut(BaseSchema):
    """Offene Menge je Vertragspartei."""

    party_id: Optional[str] = None
    offen: Optional[float] = None
    kontrakte: Optional[int] = None


class EngagementSummaryOut(BaseSchema):
    """Gesamtposition ueber alle Kontrakte."""

    einkauf_offen: Optional[float] = None
    verkauf_offen: Optional[float] = None
    netto: Optional[float] = None
    artikel_anzahl: Optional[int] = None
    parteien_anzahl: Optional[int] = None


class EngagementOut(BaseSchema):
    """``GET /contracts/engagement``"""

    by_article: list[EngagementArticleOut] = Field(default_factory=list)
    by_party: list[EngagementPartyOut] = Field(default_factory=list)
    summary: Optional[EngagementSummaryOut] = None


class DunningCandidateOut(BaseSchema):
    """Ueberfaelliger, untererfuellter Kontrakt."""

    contract_no: Optional[str] = None
    typ: Optional[str] = None
    party_id: Optional[str] = None
    einheit: Optional[str] = None
    valid_to: Optional[str] = None
    tage_ueberfaellig: Optional[int] = None
    offen: Optional[float] = None
    letzte_mahnstufe: Optional[int] = None
    naechste_mahnstufe: Optional[int] = None


class DunningCandidateListOut(BaseSchema):
    """``GET /contracts/dunning/candidates``"""

    items: list[DunningCandidateOut] = Field(default_factory=list)


class ReminderOut(BaseSchema):
    """Erfasste Kontraktmahnung (append-only)."""

    mahnstufe: Optional[int] = None
    offen: Optional[float] = None
    text: Optional[str] = None
    bediener: Optional[str] = None
    datum: Optional[str] = None


class ReminderListOut(BaseSchema):
    """``GET /contracts/dunning/list``"""

    items: list[ReminderOut] = Field(default_factory=list)


class ReminderCreatedOut(BaseSchema):
    """``POST /contracts/dunning``"""

    ok: bool = Field(default=True)
    reminder_id: Optional[str] = None
    contract_no: Optional[str] = None
    mahnstufe: Optional[int] = None
    offen: Optional[float] = None


# ── Settlement ──────────────────────────────────────────────────────────────


class MovementOut(BaseSchema):
    """Abruf-Bewegung am Kontrakt."""

    movement_id: Optional[str] = None
    menge: Optional[float] = None
    datum: Optional[str] = None
    status: Optional[str] = Field(
        default=None, description="offen | abgerechnet | storniert"
    )
    invoice_no: Optional[str] = None
    settled_at: Optional[str] = None
    storno_grund: Optional[str] = None


class SettlementSummaryOut(BaseSchema):
    """Abruf- und Abrechnungsstand des Kontrakts."""

    abgerufen: Optional[float] = None
    abgerechnet: Optional[float] = None
    offen_abruf: Optional[float] = None
    fixiert_aktiv: Optional[float] = None


class SettlementStatusOut(BaseSchema):
    """``GET /contracts/settlement/status``"""

    found: bool = Field(default=False)
    detail: Optional[str] = None
    contract_no: Optional[str] = None
    einheit: Optional[str] = None
    bewegungen: list[MovementOut] = Field(default_factory=list)
    fixierungen: list[FixingOut] = Field(default_factory=list)
    summary: Optional[SettlementSummaryOut] = None


class HandoverMovementOut(BaseSchema):
    """Uebergebene Bewegung mit vergebener Rechnungsnummer."""

    movement_id: Optional[str] = None
    menge: Optional[float] = None
    invoice_no: Optional[str] = None


class HandoverOut(BaseSchema):
    """``POST /contracts/settlement`` — Uebergabe an die Abrechnung."""

    ok: bool = Field(default=True)
    contract_no: Optional[str] = None
    uebergeben: Optional[int] = None
    bewegungen: list[HandoverMovementOut] = Field(default_factory=list)


class StornoOut(BaseSchema):
    """Storno einer Bewegung oder Fixierung.

    ``movement_id`` bzw. ``fixing_id`` ist je nach Endpunkt gesetzt;
    ``frei_menge`` ist die wieder verfuegbare Menge.
    """

    ok: bool = Field(default=True)
    movement_id: Optional[str] = None
    fixing_id: Optional[str] = None
    frei_menge: Optional[float] = None
    status: Optional[str] = None
