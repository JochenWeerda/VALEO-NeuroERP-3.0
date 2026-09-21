"""Feldvertrag der Bruecken-Masken: deklarierte Kopffelder, extra erlaubt.

Die Maske fragt nach diesen Schluesseln. Ein GET mit ``TypedObjectOut`` /
``EinkaufDocOut`` (extra=allow, nur ``id``) sagt OpenAPI nichts — das Gate
ist dann blind. Diese Modelle nennen die Kopffelder; zusaetzliche Schluessel
bleiben erlaubt.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import ConfigDict, Field

from app.api.v1.schemas.base import BaseSchema


class _MaskEntityOut(BaseSchema):
    model_config = ConfigDict(extra="allow", from_attributes=True)


class EinkaufAnfrageOut(_MaskEntityOut):
    id: Optional[str] = None
    anfrageNummer: Optional[str] = None
    anforderer: Optional[str] = None
    artikel: Optional[str] = None
    menge: Optional[float] = None
    faelligkeit: Optional[str] = None
    status: Optional[str] = None


class EinkaufAngebotOut(_MaskEntityOut):
    id: Optional[str] = None
    angebotNummer: Optional[str] = None
    lieferant: Optional[str] = None
    artikel: Optional[str] = None
    gueltigBis: Optional[str] = None
    preis: Optional[float] = None
    status: Optional[str] = None


class EinkaufAnlieferavisOut(_MaskEntityOut):
    id: Optional[str] = None
    avisNummer: Optional[str] = None
    lieferant: Optional[str] = None
    geplantesAnlieferDatum: Optional[str] = None
    bestellung: Optional[str] = None
    kennzeichen: Optional[str] = None
    status: Optional[str] = None


class EinkaufAuftragsbestaetigungOut(_MaskEntityOut):
    id: Optional[str] = None
    bestaetigungsNummer: Optional[str] = None
    bestellung: Optional[str] = None
    lieferant: Optional[str] = None
    createdAt: Optional[str] = None
    status: Optional[str] = None


class EinkaufLieferantOut(_MaskEntityOut):
    id: Optional[Any] = None
    lieferantennummer: Optional[str] = None
    firmenname: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    lieferzeit_tage: Optional[int] = None
    aktiv: Optional[bool] = None


class EinkaufBestellungOut(_MaskEntityOut):
    id: Optional[str] = None
    bestellnummer: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    bestelldatum: Optional[str] = None
    lieferdatum_wunsch: Optional[str] = None
    lieferdatum_zugesagt: Optional[str] = None
    lieferdatum_ist: Optional[str] = None
    netto_summe: Optional[float] = None
    mwst_betrag: Optional[float] = None
    brutto_summe: Optional[float] = None
    waehrung: Optional[str] = None
    unsere_referenz: Optional[str] = None
    ihre_referenz: Optional[str] = None
    status: Optional[str] = None
    versand_art: Optional[str] = None
    niederlassung_id: Optional[str] = None
    kontrakt_id: Optional[str] = None
    zahlungsziel_tage: Optional[int] = None
    skonto_prozent: Optional[float] = None
    skonto_frist_tage: Optional[int] = None
    freitext_kopf: Optional[str] = None
    freitext_fuss: Optional[str] = None
    notiz: Optional[str] = None
    erstellt_von: Optional[str] = None
    bestellfall: Optional[str] = None
    ansprechpartner: Optional[str] = None
    kreditor_konto: Optional[str] = None
    lieferant_nr: Optional[str] = None
    kostenstelle: Optional[str] = None
    kommission: Optional[str] = None
    ladetermin: Optional[str] = None
    ladetermin_ab: Optional[str] = None
    lade_datum: Optional[str] = None
    incoterms: Optional[str] = None
    lieferadresse: Optional[str] = None
    zahlungsbedingung: Optional[str] = None
    skonto1_tage: Optional[int] = None
    skonto1_prozent: Optional[float] = None
    skonto2_tage: Optional[int] = None
    skonto2_prozent: Optional[float] = None
    netto_tage: Optional[int] = None
    fremdwaehrung: Optional[str] = None
    umrechnungsfaktor: Optional[float] = None
    anfrage_nr: Optional[str] = None
    angebot_nr: Optional[str] = None
    auftrag_nr: Optional[str] = None
    abverkauf_horizont: Optional[str] = None
    bedarfsmenge: Optional[float] = None
    mindestbestellmenge: Optional[float] = None
    maximalbestellmenge: Optional[float] = None
    artikelgruppe: Optional[str] = None
    lagerplatz_opt: Optional[bool] = None
    fracht_opt: Optional[bool] = None
    opportunitaetskostensatz: Optional[float] = None
    palettenstellplatz_kosten: Optional[float] = None
    lagerkosten_satz: Optional[float] = None
    verkaufsbeleg_id: Optional[str] = None
    kunden_id: Optional[str] = None
    direktlieferung: Optional[bool] = None
    ueberschlag_lager: Optional[bool] = None
    neuer_artikel: Optional[bool] = None
    innovationshinweis: Optional[str] = None


class FinanceDebitorOut(_MaskEntityOut):
    id: Optional[str] = None
    debitoren_nr: Optional[str] = None
    name: Optional[str] = None
    kreditlimit: Optional[float] = None
    zahlungsbedingungen: Optional[str] = None
    steuernummer: Optional[str] = None
    ust_id: Optional[str] = None
    status: Optional[str] = None


class FinanceKreditorOut(_MaskEntityOut):
    id: Optional[str] = None
    kreditoren_nr: Optional[str] = None
    name: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    steuernummer: Optional[str] = None
    ust_id: Optional[str] = None
    status: Optional[str] = None


class FinanceBankkontoOut(_MaskEntityOut):
    id: Optional[str] = None
    bank: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    waehrung: Optional[str] = None
    saldo: Optional[float] = None
    status: Optional[str] = None


class FinanceApInvoiceOut(_MaskEntityOut):
    """Englische Belegfelder plus deutsche Masken-Aliase."""

    id: Optional[str] = None
    number: Optional[str] = None
    beleg_nr: Optional[str] = None
    kreditor: Optional[str] = None
    datum: Optional[Any] = None
    faellig_am: Optional[Any] = None
    brutto: Optional[float] = None
    mwst: Optional[float] = None
    status: Optional[str] = None


class QualitaetReklamationOut(_MaskEntityOut):
    reklamation_id: Optional[str] = None
    typ: Optional[str] = None
    lieferant_id: Optional[str] = None
    kontrakt_id: Optional[str] = None
    erstellt_am: Optional[str] = None
    frist_datum: Optional[str] = None
    sla_status: Optional[str] = None
    zustaendiger: Optional[str] = None
    status: Optional[str] = None


class _MaskRowOut(_MaskEntityOut):
    """Eine Tabellenzeile: zugesagte Spalten, zusaetzliche Schluessel erlaubt."""


class MaskTabOut(BaseSchema):
    """Eine Registerseite des Builders."""

    tab_key: str
    table_key: str
    page: int
    limit: int
    total: int


class PurchaseOrderPositionRowOut(_MaskRowOut):
    pos_nr: Optional[Any] = None
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    lieferanten_artnr: Optional[str] = None
    menge: Optional[float] = None
    menge_geliefert: Optional[float] = None
    menge_offen: Optional[float] = None
    einheit: Optional[str] = None
    einzelpreis: Optional[float] = None
    preis_einheit: Optional[str] = None
    betrag: Optional[float] = None
    gebinde_menge: Optional[float] = None
    gebinde_einheit: Optional[str] = None
    gewicht_kg: Optional[float] = None
    kontrakt_nr: Optional[str] = None
    lager: Optional[str] = None
    lagerort: Optional[str] = None
    lagerhalle: Optional[str] = None
    lagerfach: Optional[str] = None
    mindestmenge: Optional[float] = None
    maximalmenge: Optional[float] = None


class PurchaseOrderCommRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    empfaenger: Optional[str] = None
    status: Optional[str] = None


class SupplierOrderRowOut(_MaskRowOut):
    bestell_nr: Optional[str] = None
    datum: Optional[Any] = None
    status: Optional[str] = None
    betrag: Optional[float] = None


class SupplierContactRowOut(_MaskRowOut):
    name: Optional[str] = None
    funktion: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None


class ApInvoicePositionRowOut(_MaskRowOut):
    pos_nr: Optional[Any] = None
    bezeichnung: Optional[str] = None
    menge: Optional[float] = None
    betrag: Optional[float] = None


class ApInvoiceFreigabeRowOut(BaseSchema):
    """Zwei Felder, extra verboten — sonst gilt die Zeile als Platzhalter."""

    feld: Optional[str] = None
    wert: Optional[str] = None


class PurchaseOrderPositionTabOut(MaskTabOut):
    items: list[PurchaseOrderPositionRowOut] = Field(default_factory=list)


class PurchaseOrderCommTabOut(MaskTabOut):
    items: list[PurchaseOrderCommRowOut] = Field(default_factory=list)


class SupplierOrderTabOut(MaskTabOut):
    items: list[SupplierOrderRowOut] = Field(default_factory=list)


class SupplierContactTabOut(MaskTabOut):
    items: list[SupplierContactRowOut] = Field(default_factory=list)


class ApInvoicePositionTabOut(MaskTabOut):
    items: list[ApInvoicePositionRowOut] = Field(default_factory=list)


class ApInvoiceFreigabeTabOut(MaskTabOut):
    items: list[ApInvoiceFreigabeRowOut] = Field(default_factory=list)


class EinkaufAnfragePositionRowOut(_MaskRowOut):
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None


class EinkaufAngebotPositionRowOut(_MaskRowOut):
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    menge: Optional[float] = None
    einzelpreis: Optional[float] = None
    betrag: Optional[float] = None


class EinkaufAnlieferavisPositionRowOut(_MaskRowOut):
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    charge: Optional[str] = None


class EinkaufAbPositionRowOut(_MaskRowOut):
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    einzelpreis: Optional[float] = None


class FinanceBankkontoBuchungRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    verwendungszweck: Optional[str] = None
    betrag: Optional[float] = None
    gegenpartei: Optional[str] = None


class FinanceOffenePostenRowOut(_MaskRowOut):
    beleg_nr: Optional[str] = None
    datum: Optional[Any] = None
    faellig: Optional[Any] = None
    betrag: Optional[float] = None
    status: Optional[str] = None


class FinanceDebitorUmsatzRowOut(_MaskRowOut):
    periode: Optional[str] = None
    umsatz: Optional[float] = None
    anzahl_belege: Optional[int] = None


class FinanceKreditorBestellungRowOut(_MaskRowOut):
    bestell_nr: Optional[str] = None
    datum: Optional[Any] = None
    betrag: Optional[float] = None
    status: Optional[str] = None


class MischfuttermittelRezepturRowOut(_MaskRowOut):
    futtermittel: Optional[str] = None
    anteil_pct: Optional[float] = None
    menge_je_t: Optional[float] = None


class MischfuttermittelNaehrstoffRowOut(_MaskRowOut):
    naehrstoff: Optional[str] = None
    gehalt: Optional[float] = None
    einheit: Optional[str] = None


class ReklamationMassnahmeRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    beschreibung: Optional[str] = None
    verantwortlich: Optional[str] = None
    status: Optional[str] = None


class ReklamationDokumentRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    bezeichnung: Optional[str] = None


class EinkaufAnfragePositionTabOut(MaskTabOut):
    items: list[EinkaufAnfragePositionRowOut] = Field(default_factory=list)


class EinkaufAngebotPositionTabOut(MaskTabOut):
    items: list[EinkaufAngebotPositionRowOut] = Field(default_factory=list)


class EinkaufAnlieferavisPositionTabOut(MaskTabOut):
    items: list[EinkaufAnlieferavisPositionRowOut] = Field(default_factory=list)


class EinkaufAbPositionTabOut(MaskTabOut):
    items: list[EinkaufAbPositionRowOut] = Field(default_factory=list)


class FinanceBankkontoBuchungTabOut(MaskTabOut):
    items: list[FinanceBankkontoBuchungRowOut] = Field(default_factory=list)


class FinanceOffenePostenTabOut(MaskTabOut):
    items: list[FinanceOffenePostenRowOut] = Field(default_factory=list)


class FinanceDebitorUmsatzTabOut(MaskTabOut):
    items: list[FinanceDebitorUmsatzRowOut] = Field(default_factory=list)


class FinanceKreditorBestellungTabOut(MaskTabOut):
    items: list[FinanceKreditorBestellungRowOut] = Field(default_factory=list)


class MischfuttermittelRezepturTabOut(MaskTabOut):
    items: list[MischfuttermittelRezepturRowOut] = Field(default_factory=list)


class MischfuttermittelNaehrstoffTabOut(MaskTabOut):
    items: list[MischfuttermittelNaehrstoffRowOut] = Field(default_factory=list)


class ReklamationMassnahmeTabOut(MaskTabOut):
    items: list[ReklamationMassnahmeRowOut] = Field(default_factory=list)


class ReklamationDokumentTabOut(MaskTabOut):
    items: list[ReklamationDokumentRowOut] = Field(default_factory=list)


class DuengerVerwendungRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    flaeche: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None


class DuengerPreisRowOut(_MaskRowOut):
    gueltig_ab: Optional[Any] = None
    preis: Optional[float] = None
    lieferant: Optional[str] = None


class SaatgutLagerbestandRowOut(_MaskRowOut):
    lagerort: Optional[str] = None
    menge: Optional[float] = None
    charge: Optional[str] = None
    lager_datum: Optional[Any] = None


class SaatgutVertragRowOut(_MaskRowOut):
    vertrag_nr: Optional[str] = None
    erzeuger: Optional[str] = None
    menge: Optional[float] = None
    ernte_jahr: Optional[Any] = None


class LeadAktivitaetRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    betreff: Optional[str] = None
    benutzer: Optional[str] = None


class LeadAufgabeRowOut(_MaskRowOut):
    faellig: Optional[Any] = None
    titel: Optional[str] = None
    prioritaet: Optional[str] = None
    status: Optional[str] = None


class OpportunityAktivitaetRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    betreff: Optional[str] = None
    verantwortlich: Optional[str] = None
    status: Optional[str] = None


class OpportunityAngebotRowOut(_MaskRowOut):
    angebot_nr: Optional[str] = None
    datum: Optional[Any] = None
    wert: Optional[float] = None
    waehrung: Optional[str] = None
    status: Optional[str] = None


class ArticleStockBestandRowOut(_MaskRowOut):
    lagerort_nr: Optional[str] = None
    lagerort_bezeichnung: Optional[str] = None
    bestand_menge: Optional[float] = None
    einheit: Optional[str] = None
    reserviert: Optional[float] = None
    mindestbestand: Optional[float] = None


class ArticleStockBewegungRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    beleg_nr: Optional[str] = None
    movement_id: Optional[str] = None


class DeliveryNotePositionRowOut(_MaskRowOut):
    pos_nr: Optional[Any] = None
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    charge: Optional[str] = None


class DeliveryNoteDokumentRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    bezeichnung: Optional[str] = None
    benutzer: Optional[str] = None


class ArOpenItemAusgleichRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    betrag: Optional[float] = None
    zahlungsart: Optional[str] = None
    bank_ref: Optional[str] = None


class StockMovementDetailRowOut(_MaskRowOut):
    datum: Optional[Any] = None
    typ: Optional[str] = None
    beleg_nr: Optional[str] = None
    lagerort: Optional[str] = None
    status: Optional[str] = None


class HarvestSettlementPositionRowOut(_MaskRowOut):
    lieferschein_nr: Optional[str] = None
    datum: Optional[Any] = None
    sorte: Optional[str] = None
    feuchtigkeit: Optional[float] = None
    menge: Optional[float] = None


class HarvestSettlementAbzugRowOut(_MaskRowOut):
    abzug_art: Optional[str] = None
    beschreibung: Optional[str] = None
    menge: Optional[float] = None
    betrag: Optional[float] = None


class PaymentRunZahlungRowOut(_MaskRowOut):
    kreditoren_nr: Optional[str] = None
    name: Optional[str] = None
    betrag: Optional[float] = None
    bank: Optional[str] = None
    status: Optional[str] = None


class DuengerVerwendungTabOut(MaskTabOut):
    items: list[DuengerVerwendungRowOut] = Field(default_factory=list)


class DuengerPreisTabOut(MaskTabOut):
    items: list[DuengerPreisRowOut] = Field(default_factory=list)


class SaatgutLagerbestandTabOut(MaskTabOut):
    items: list[SaatgutLagerbestandRowOut] = Field(default_factory=list)


class SaatgutVertragTabOut(MaskTabOut):
    items: list[SaatgutVertragRowOut] = Field(default_factory=list)


class LeadAktivitaetTabOut(MaskTabOut):
    items: list[LeadAktivitaetRowOut] = Field(default_factory=list)


class LeadAufgabeTabOut(MaskTabOut):
    items: list[LeadAufgabeRowOut] = Field(default_factory=list)


class OpportunityAktivitaetTabOut(MaskTabOut):
    items: list[OpportunityAktivitaetRowOut] = Field(default_factory=list)


class OpportunityAngebotTabOut(MaskTabOut):
    items: list[OpportunityAngebotRowOut] = Field(default_factory=list)


class ArticleStockBestandTabOut(MaskTabOut):
    items: list[ArticleStockBestandRowOut] = Field(default_factory=list)


class ArticleStockBewegungTabOut(MaskTabOut):
    items: list[ArticleStockBewegungRowOut] = Field(default_factory=list)


class DeliveryNotePositionTabOut(MaskTabOut):
    items: list[DeliveryNotePositionRowOut] = Field(default_factory=list)


class DeliveryNoteDokumentTabOut(MaskTabOut):
    items: list[DeliveryNoteDokumentRowOut] = Field(default_factory=list)


class ArOpenItemAusgleichTabOut(MaskTabOut):
    items: list[ArOpenItemAusgleichRowOut] = Field(default_factory=list)


class StockMovementDetailTabOut(MaskTabOut):
    items: list[StockMovementDetailRowOut] = Field(default_factory=list)


class HarvestSettlementPositionTabOut(MaskTabOut):
    items: list[HarvestSettlementPositionRowOut] = Field(default_factory=list)


class HarvestSettlementAbzugTabOut(MaskTabOut):
    items: list[HarvestSettlementAbzugRowOut] = Field(default_factory=list)


class PaymentRunZahlungTabOut(MaskTabOut):
    items: list[PaymentRunZahlungRowOut] = Field(default_factory=list)


def opportunity_activity_aliases(row: dict[str, Any]) -> dict[str, Any]:
    """Aktivitaet: Typ, Betreff und Faelligkeit, kein erfundener Verantwortlicher."""
    out = dict(row)
    out.setdefault("typ", row.get("activity_type") or row.get("type"))
    out.setdefault("betreff", row.get("subject"))
    out.setdefault("datum", row.get("due_date") or row.get("date"))
    out.setdefault("verantwortlich", row.get("assigned_to"))
    return out


def opportunity_quote_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("angebot_nr", row.get("quote_number"))
    out.setdefault("datum", row.get("valid_until") or row.get("quote_date"))
    if out.get("wert") is None and row.get("total_amount") is not None:
        out["wert"] = float(row["total_amount"])
    return out


def delivery_note_position_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("pos_nr", row.get("position_no") or row.get("position"))
    out.setdefault("artikel_nr", row.get("article_id") or row.get("artikel_id"))
    out.setdefault("bezeichnung", row.get("description"))
    if out.get("menge") is None and row.get("quantity") is not None:
        out["menge"] = float(row["quantity"])
    out.setdefault("einheit", row.get("unit"))
    return out


def delivery_note_document_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("typ", row.get("document_type"))
    out.setdefault("bezeichnung", row.get("reference") or row.get("title"))
    out.setdefault("benutzer", row.get("created_by") or row.get("user"))
    out.setdefault("datum", row.get("created_at") or row.get("date"))
    return out


def ar_open_item_ausgleich_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("datum", row.get("buchungs_datum"))
    out.setdefault("bank_ref", row.get("referenz"))
    out.setdefault("zahlungsart", row.get("zahlungsart") or row.get("payment_method"))
    if out.get("betrag") is None and row.get("betrag") is not None:
        out["betrag"] = float(row["betrag"])
    return out


def harvest_settlement_abzug_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("abzug_art", row.get("deduction_type"))
    out.setdefault("beschreibung", row.get("reason"))
    if out.get("betrag") is None and row.get("amount") is not None:
        out["betrag"] = float(row["amount"])
    if out.get("menge") is None and row.get("quantity") is not None:
        out["menge"] = float(row["quantity"])
    return out


def payment_run_zahlung_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("name", row.get("creditor_name"))
    out.setdefault("kreditoren_nr", row.get("creditor_number") or row.get("kreditor_nr"))
    out.setdefault("bank", row.get("bank_name") or row.get("bank"))
    if out.get("betrag") is None and row.get("amount") is not None:
        out["betrag"] = float(row["amount"])
    return out


def purchase_order_position_aliases(row: dict[str, Any]) -> dict[str, Any]:
    """Spalten der Bestellposition, wie die Maske sie liest."""
    out = dict(row)
    out.setdefault("pos_nr", row.get("position_nr") or row.get("pos_nr"))
    out.setdefault("bezeichnung", row.get("artikel_bezeichnung") or row.get("bezeichnung"))
    out.setdefault("lager", row.get("lagerort") or row.get("lager"))
    out.setdefault("lagerort", row.get("lagerort") or row.get("lager"))
    if out.get("betrag") is None:
        raw = row.get("gesamtpreis")
        if raw is None:
            raw = row.get("netto_betrag")
        if raw is not None:
            out["betrag"] = float(raw)
    if out.get("menge_offen") is None:
        menge = row.get("menge")
        geliefert = row.get("menge_geliefert")
        if menge is not None:
            out["menge_offen"] = float(menge) - float(geliefert or 0)
    return out


def purchase_order_comm_aliases(row: dict[str, Any]) -> dict[str, Any]:
    """Kommunikation: Kanal und Versandzeit, nicht erfundene Betreffzeilen."""
    out = dict(row)
    out.setdefault("typ", row.get("kanal"))
    out.setdefault("datum", row.get("versendet_am"))
    return out


def supplier_order_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("datum", row.get("bestelldatum"))
    if out.get("betrag") is None and row.get("gesamtbetrag") is not None:
        out["betrag"] = float(row["gesamtbetrag"])
    return out


def supplier_contact_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("funktion", row.get("rolle"))
    return out


def ap_invoice_position_aliases(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.setdefault("pos_nr", row.get("position"))
    out.setdefault("bezeichnung", row.get("description") or row.get("itemDescription"))
    if out.get("menge") is None and row.get("quantity") is not None:
        out["menge"] = float(row["quantity"])
    if out.get("betrag") is None:
        raw = row.get("total") if row.get("total") is not None else row.get("lineTotal")
        if raw is not None:
            out["betrag"] = float(raw)
    return out


def ap_invoice_freigabe_zeilen(invoice: dict[str, Any]) -> list[dict[str, Any]]:
    """Zwei Zeilen Stand, keine erfundene Historie."""
    return [
        {
            "feld": "approval_status",
            "wert": str(invoice.get("approval_status") or invoice.get("status") or "-"),
        },
        {
            "feld": "semantic_status",
            "wert": str(invoice.get("semantic_status") or "-"),
        },
    ]


def ap_invoice_mask_aliases(invoice: dict[str, Any]) -> dict[str, Any]:
    """Haengt die Kopffelder der Maske finance/ap-invoice an den Beleg."""
    out = dict(invoice)
    out.setdefault("beleg_nr", invoice.get("number") or invoice.get("id"))
    out.setdefault(
        "kreditor",
        invoice.get("customerName")
        or invoice.get("supplierName")
        or invoice.get("customerId"),
    )
    out.setdefault("datum", invoice.get("date") or invoice.get("invoiceDate"))
    out.setdefault("faellig_am", invoice.get("dueDate"))
    gross = invoice.get("totalGross")
    if gross is not None:
        out.setdefault("brutto", float(gross))
    tax = invoice.get("totalTax")
    if tax is not None:
        out.setdefault("mwst", float(tax))
    return out
