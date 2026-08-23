"""Response-Schemas fuer den Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

SPEC-P1-06 Welle 1: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/procurement_match.py`` durch echte Pydantic-Schemas.

Die Feldlisten sind aus den tatsaechlichen Rueckgabe-Dicts von
``app/services/procurement_match_service.py``,
``proc_wareneingang_service.py`` und ``proc_rechnungspruefung_service.py``
abgeleitet — FastAPI filtert die Antwort gegen das ``response_model``, jedes
fehlende Feld waere ein stiller Feldverlust.

Alle Felder sind optional mit Default, weil die Match-Endpunkte zwei Zweige
haben: den Trefferfall und ``{"found": false, "detail": ...}``.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ---------------------------------------------------------------------------
# Bausteine
# ---------------------------------------------------------------------------


class MatchPositionOut(BaseSchema):
    """Positionszeile aus ``match_position()`` plus Beleg-/Preiskontext."""

    pos_nr: Optional[Any] = Field(default=None, description="Positionsnummer am Beleg")
    artikel_nr: Optional[str] = Field(default=None, description="Artikelnummer")
    bezeichnung: Optional[str] = Field(default=None, description="Artikelbezeichnung")
    einheit: Optional[str] = Field(default=None, description="Mengeneinheit")
    einzelpreis: Optional[float] = Field(default=None, description="Einzelpreis netto")
    wert_offen: Optional[float] = Field(default=None, description="Offener Wert (offen x Einzelpreis)")
    bestellt: Optional[float] = Field(default=None, description="Bestellte Menge")
    geliefert: Optional[float] = Field(default=None, description="Gelieferte Menge")
    offen: Optional[float] = Field(default=None, description="Differenz bestellt minus geliefert")
    status: Optional[str] = Field(
        default=None,
        description="offen | teilgeliefert | vollstaendig | ueberliefert | ohne_menge",
    )
    abweichung_pct: Optional[float] = Field(default=None, description="Mengenabweichung in Prozent")
    abweichung: Optional[bool] = Field(default=None, description="True bei teil-/ueberliefert")


class GoodsReceiptOut(BaseSchema):
    """Wareneingangskopf zur Bestellung."""

    id: Optional[str] = None
    gr_number: Optional[str] = Field(default=None, description="Wareneingangsnummer")
    datum: Optional[str] = Field(default=None, description="Eingangsdatum (ISO)")
    status: Optional[str] = None
    lieferschein: Optional[str] = Field(default=None, description="Lieferscheinnummer")


class InvoiceOut(BaseSchema):
    """Eingangsrechnung, die der Bestellung zugeordnet ist."""

    id: Optional[str] = None
    rechnungsnummer: Optional[str] = None
    datum: Optional[str] = Field(default=None, description="Rechnungsdatum (ISO)")
    gesamt_netto: Optional[float] = None
    gesamt_brutto: Optional[float] = None
    zugeordneter_auftrag: Optional[str] = None
    zugeordneter_lieferschein: Optional[str] = None
    status: Optional[str] = None


class MatchHinweisOut(BaseSchema):
    """Luecke oder Ausnahme aus dem Abgleich.

    ``luecken`` fuehren ``pos_nr``/``schwere``/``text``; ``ausnahmen`` fuehren
    zusaetzlich einen ``code``.
    """

    pos_nr: Optional[Any] = None
    schwere: Optional[str] = Field(default=None, description="info | warnung | blocker")
    code: Optional[str] = Field(default=None, description="Ausnahme-Code, z. B. keine_rechnung")
    text: Optional[str] = None


class MatchSummaryOut(BaseSchema):
    """Kopfkennzahlen des Abgleichs.

    Die drei letzten Felder liefert nur der 3-Wege-Match.
    """

    positionen: Optional[int] = None
    wareneingaenge: Optional[int] = None
    vollstaendig_geliefert: Optional[bool] = None
    hat_abweichung: Optional[bool] = None
    offene_luecken: Optional[int] = None
    rechnungen: Optional[int] = None
    drei_wege_abgeglichen: Optional[bool] = None
    hat_ausnahme: Optional[bool] = None


class ThreeWayValueOut(BaseSchema):
    """Wertabgleich gelieferter Bezug vs. fakturierter Betrag."""

    bestellt_wert: Optional[float] = None
    geliefert_wert: Optional[float] = None
    fakturiert_netto: Optional[float] = None
    bezug: Optional[float] = None
    fakturiert: Optional[float] = None
    differenz: Optional[float] = None
    abweichung_pct: Optional[float] = None
    status: Optional[str] = Field(
        default=None,
        description="abgeglichen | wertabweichung | ohne_bezug | rechnung_ohne_bezug",
    )
    abweichung: Optional[bool] = None
    drei_wege_abgeglichen: Optional[bool] = None


class ErsPreviewLineOut(BaseSchema):
    """Zeile der ERS-Gutschriftvorschau.

    Zwei Auspraegungen: ``ueberlieferung`` (mit Position/Menge/Preis) und
    ``rechnungsueberzahlung`` (mit Bezug/Fakturiert).
    """

    typ: Optional[str] = Field(default=None, description="ueberlieferung | rechnungsueberzahlung")
    pos_nr: Optional[Any] = None
    artikel_nr: Optional[str] = None
    menge: Optional[float] = None
    einzelpreis: Optional[float] = None
    betrag_netto: Optional[float] = None
    bezug: Optional[float] = None
    fakturiert: Optional[float] = None


class ErsPreviewOut(BaseSchema):
    """Berechnete ERS-Gutschrift (rein rechnerisch, nicht persistiert)."""

    betrag_netto: Optional[float] = None
    positionen: list[ErsPreviewLineOut] = Field(default_factory=list)
    berechtigt: Optional[bool] = None
    anzahl_zeilen: Optional[int] = None


class FollowUpOut(BaseSchema):
    """Append-only Folgeaktion zu einer Bestellung."""

    id: Optional[str] = None
    action_type: Optional[str] = Field(
        default=None,
        description="nachforderung | reklamation | eskalation | freigabe",
    )
    ausnahme_code: Optional[str] = None
    grund: Optional[str] = None
    eskalationsstufe: Optional[int] = None
    created_at: Optional[str] = Field(default=None, description="ISO-Zeitstempel")
    created_by: Optional[str] = None


class ErsCreditOut(BaseSchema):
    """Persistierte ERS-Gutschrift."""

    id: Optional[str] = None
    gutschrift_nummer: Optional[str] = None
    betrag_netto: Optional[float] = None
    grund: Optional[str] = None
    ausnahme_code: Optional[str] = None
    status: Optional[str] = None
    positionen: list[ErsPreviewLineOut] = Field(default_factory=list)
    created_at: Optional[str] = None
    created_by: Optional[str] = None


class OrderPickerItemOut(BaseSchema):
    """Bestellung in der Auswahlliste des Match-Pickers."""

    bestellnummer: Optional[str] = None
    datum: Optional[str] = Field(default=None, description="Bestelldatum (ISO)")
    status: Optional[str] = None
    netto_summe: Optional[float] = None
    positionen: Optional[int] = Field(default=None, description="Anzahl Positionen")
    hat_wareneingang: Optional[bool] = None


# ---------------------------------------------------------------------------
# Endpunkt-Antworten
# ---------------------------------------------------------------------------


class OrderPickerListOut(BaseSchema):
    """``GET /procurement/match/orders``"""

    items: list[OrderPickerItemOut] = Field(default_factory=list)


class MatchOut(BaseSchema):
    """``GET /procurement/match`` — Bestellung vs. Wareneingang.

    Im Nichttrefferfall sind nur ``found=false`` und ``detail`` gesetzt.
    """

    found: bool = Field(default=False, description="False, wenn die Bestellung nicht aufloesbar ist")
    detail: Optional[str] = Field(default=None, description="Begruendung im Nichttrefferfall")
    bestellnummer: Optional[str] = None
    status: Optional[str] = None
    lieferant_id: Optional[str] = None
    netto_summe: Optional[float] = None
    positionen: list[MatchPositionOut] = Field(default_factory=list)
    wareneingaenge: list[GoodsReceiptOut] = Field(default_factory=list)
    luecken: list[MatchHinweisOut] = Field(default_factory=list)
    summary: Optional[MatchSummaryOut] = None


class ThreeWayMatchOut(MatchOut):
    """``GET /procurement/match/three-way`` und ``.../match/ers/preview``.

    Erweitert den Basis-Match um Rechnungsstufe, Folgeaktionen und ERS.
    """

    rechnungen: list[InvoiceOut] = Field(default_factory=list)
    three_way: Optional[ThreeWayValueOut] = None
    ausnahmen: list[MatchHinweisOut] = Field(default_factory=list)
    follow_ups: list[FollowUpOut] = Field(default_factory=list)
    ers_preview: Optional[ErsPreviewOut] = None
    ers_credits: list[ErsCreditOut] = Field(default_factory=list)


class FollowUpListOut(BaseSchema):
    """``GET /procurement/match/follow-up``"""

    items: list[FollowUpOut] = Field(default_factory=list)


class ErsCreditListOut(BaseSchema):
    """``GET /procurement/match/ers``"""

    items: list[ErsCreditOut] = Field(default_factory=list)


class ToleranceCheckOut(BaseSchema):
    """Toleranzauswertung des automatischen 3-Wege-Matches."""

    qty_delta_pct: Optional[float] = None
    qty_tolerance_pct: Optional[float] = None
    qty_ok: Optional[bool] = None
    value_delta_pct: Optional[float] = None
    price_tolerance_pct: Optional[float] = None
    value_ok: Optional[bool] = None
    missing_context: list[str] = Field(
        default_factory=list,
        description="Fehlende Belegstufen, z. B. Wareneingang / Eingangsrechnung",
    )


class AutoMatchOut(BaseSchema):
    """``POST /procurement/match/auto`` (PROC-3WM-001)."""

    match_id: Optional[str] = None
    match_status: Optional[str] = Field(
        default=None, description="MATCH_OK | MISMATCH | PENDING | CANCELLED"
    )
    drei_wege_abgeglichen: Optional[bool] = None
    discrepancy_reason: Optional[str] = None
    tolerance_check: Optional[ToleranceCheckOut] = None
    detail: Optional[ThreeWayMatchOut] = Field(
        default=None, description="Vollstaendiges Match-Ergebnis zur Nachvollziehbarkeit"
    )


class MatchResultRowOut(BaseSchema):
    """Zeile aus ``domain_procurement.procurement_match_results``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    po_id: Optional[str] = None
    gr_id: Optional[str] = None
    ap_invoice_id: Optional[str] = None
    match_status: Optional[str] = None
    qty_po: Optional[float] = None
    qty_gr: Optional[float] = None
    qty_ap: Optional[float] = None
    price_po: Optional[float] = None
    price_ap: Optional[float] = None
    qty_tolerance_pct: Optional[float] = None
    price_tolerance_pct: Optional[float] = None
    discrepancy_reason: Optional[str] = None
    matched_by: Optional[str] = None
    matched_at: Optional[Any] = Field(default=None, description="Zeitpunkt des Matches")
    created_at: Optional[Any] = None


class MatchResultListOut(BaseSchema):
    """``GET /procurement/match/results``"""

    items: list[MatchResultRowOut] = Field(default_factory=list)


class WareneingangOut(BaseSchema):
    """``POST /procurement/bestellungen/{id}/wareneingang`` und
    ``POST /procurement/wareneingaenge/{id}/qs``.

    Felder entsprechen ``domain_procurement.proc_wareneingaenge``; ``idempotent``
    kennzeichnet den Wiederholfall.
    """

    id: Optional[str] = None
    bestellung_id: Optional[str] = None
    tenant_id: Optional[str] = None
    menge_erhalten: Optional[float] = None
    einheit: Optional[str] = None
    lager_id: Optional[str] = None
    qs_status: Optional[str] = None
    gebucht_am: Optional[Any] = None
    operator: Optional[str] = None
    created_at: Optional[Any] = None
    idempotent: Optional[bool] = Field(
        default=None, description="True, wenn der Wareneingang bereits gebucht war"
    )


class RechnungspruefungOut(BaseSchema):
    """``POST /procurement/bestellungen/{id}/rechnungspruefung`` und
    ``POST /procurement/rechnungspruefungen/{id}/freigabe``.

    Felder entsprechen ``domain_procurement.proc_rechnungspruefungen``;
    ``soll_betrag_eur`` liefert zusaetzlich der Neuanlagepfad.
    """

    id: Optional[str] = None
    bestellung_id: Optional[str] = None
    tenant_id: Optional[str] = None
    rechnungs_nr: Optional[str] = None
    bestell_wert_eur: Optional[float] = None
    soll_betrag_eur: Optional[float] = Field(
        default=None, description="Errechneter Sollbetrag (Bestellpreis x WE-Menge)"
    )
    we_menge: Optional[float] = None
    rechnungs_betrag_eur: Optional[float] = None
    abweichung_pct: Optional[float] = None
    status: Optional[str] = Field(default=None, description="FREIGEGEBEN | GESPERRT")
    freigabe_operator: Optional[str] = None
    freigabe_grund: Optional[str] = None
    created_at: Optional[Any] = None
    idempotent: Optional[bool] = Field(
        default=None, description="True, wenn die Pruefung bereits existierte"
    )
