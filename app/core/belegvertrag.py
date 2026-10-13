"""Belegvertrag: die eine Form, in der eine Belegmaske einen Beleg liest (BELEG-010).

Die Belegmaske kennt keinen Speicher. Jede belegfuehrende Domaene liefert ihre Belege in dieser Form; die
Variante je Belegart sagt, was die Form fuer diese Belegart enthaelt. Hier steht keine Fachlogik: keine
Steuerberechnung, keine Buchung, kein Statuswechsel.

Drei Dinge gehoeren zum Vertrag:

* die Form (``Beleg`` mit Kopf, Partner, Positionen, Summen, Buchungsstand, Kette, Dokumenten, Historie, Aktionen),
* die Varianten (``BELEGARTEN``): Bezeichnung, Partnerrolle, Steuerrichtung, mit oder ohne Preise, Folgebelege,
* die Abbildung der bisherigen Feldnamen der Beleg-ScreenDefinitions auf den Vertrag (``ABBILDUNG``).

Preise: Eine Variante ohne Preise (Lieferschein, Wareneingang) traegt weder Preisfelder noch Summen. Dasselbe
gilt fuer jeden Beleg, dessen Leser kein Preisrecht hat (``preise_sichtbar`` falsch) — der Server liefert die
Felder dann nicht aus, statt sie nur auszublenden (``ohne_preise``).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

VERTRAGSVERSION = "1.0"

STATUS: tuple[str, ...] = ("draft", "open", "released", "posted", "reversed", "cancelled")

# Felder einer Position, die nur mit Preisrecht und nur in Varianten mit Preisen ausgeliefert werden.
PREISFELDER: tuple[str, ...] = (
    "einzelpreis", "rabatt_prozent", "steuerschluessel", "steuersatz", "netto", "steuer", "brutto", "aufwandskonto",
)

# Fachliche Sonderteile: Bausteine, die eine Variante einhaengt. Sie gehoeren nicht zum Grundgeruest.
BAUSTEINE: dict[str, str] = {
    "lieferung": "Liefer- und Ladetermine, Versandart, Incoterms, Lieferadresse, Selbstabholung, Fahrzeug",
    "zahlung": "Zahlungsbedingung, Faelligkeit, Skonto, Fremdwaehrung",
    "texte": "Betreff, Kopf- und Fusstext, Notizen",
    "kontakt": "Ansprechpartner beim Partner",
    "organisation": "Niederlassung, Kostenstelle, Kommission, Bearbeiter",
    "referenzen": "Eigene und fremde Referenzangaben",
    "kontierung": "Kreditoren- bzw. Debitorenkonto des Partners",
    "gebinde": "Gebindemenge und -einheit, Preiseinheit, Gewicht",
    "lager": "Lager, Halle, Fach",
    "kontrakt": "Bezug auf einen Kontrakt",
    "bestellfall": "Bestellfall mit Bedarfs-, Mindest- und Hoechstmengen",
    "einkauf": "Artikelnummer des Lieferanten",
}


class _Teil(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Partner(_Teil):
    rolle: Literal["kunde", "lieferant"]
    nummer: str | None = None
    name: str | None = None


class Belegposition(_Teil):
    pos_nr: int
    artikel_nr: str
    bezeichnung: str | None = None
    menge: Decimal
    einheit: str | None = None
    charge: str | None = None
    # In Folgebelege uebernommene und noch offene Menge (nur Belegarten mit Folgebeleg).
    menge_uebernommen: Decimal | None = None
    menge_offen: Decimal | None = None
    # Preisfelder (siehe PREISFELDER).
    einzelpreis: Decimal | None = None
    rabatt_prozent: Decimal | None = None
    steuerschluessel: str | None = None
    steuersatz: Decimal | None = None
    netto: Decimal | None = None
    steuer: Decimal | None = None
    brutto: Decimal | None = None
    aufwandskonto: str | None = None
    bausteine: dict[str, dict[str, Any]] = Field(default_factory=dict)


class Steuergruppe(_Teil):
    steuerschluessel: str | None = None
    steuersatz: Decimal
    netto: Decimal
    steuer: Decimal


class Summen(_Teil):
    netto: Decimal
    steuer: Decimal
    brutto: Decimal
    steuergruppen: list[Steuergruppe] = Field(default_factory=list)


class Buchung(_Teil):
    """Buchungsstand, gespeist von Finance."""

    stand: Literal["nicht_gebucht", "gebucht", "storniert", "pruefen"] = "nicht_gebucht"
    journal_id: str | None = None
    grund: str | None = None


class Kettenglied(_Teil):
    richtung: Literal["vorgaenger", "nachfolger"]
    belegart: str
    beleg_id: str
    beleg_nr: str
    status: str | None = None
    menge: Decimal | None = None


class Belegdokument(_Teil):
    dokument_id: str
    bezeichnung: str
    art: str | None = None
    datum: datetime | None = None


class Historieneintrag(_Teil):
    zeitpunkt: datetime
    von_status: str | None = None
    nach_status: str
    kommando: str | None = None
    akteur: str | None = None
    grund: str | None = None


class Belegaktion(_Teil):
    """Was der Leser mit diesem Beleg jetzt tun darf — vom Server entschieden, nicht von der Maske."""

    key: str
    bezeichnung: str
    erlaubt: bool = True
    grund: str | None = None
    folgebelegart: str | None = None
    # Die Fachaktion dahinter. Maske, MCP-Werkzeug und Kommandozeile rufen dieselbe auf.
    kommando: str | None = None
    freigabe_noetig: bool = False


class Beleg(_Teil):
    vertragsversion: str = VERTRAGSVERSION
    beleg_id: str
    belegart: str
    beleg_nr: str
    status: str
    belegdatum: date
    buchungsdatum: date | None = None
    waehrung: str = "EUR"
    version: int = 1
    preise_sichtbar: bool = True
    partner: Partner | None = None
    positionen: list[Belegposition] = Field(default_factory=list)
    summen: Summen | None = None
    buchung: Buchung = Field(default_factory=Buchung)
    kette: list[Kettenglied] = Field(default_factory=list)
    dokumente: list[Belegdokument] = Field(default_factory=list)
    historie: list[Historieneintrag] = Field(default_factory=list)
    aktionen: list[Belegaktion] = Field(default_factory=list)
    bausteine: dict[str, dict[str, Any]] = Field(default_factory=dict)


@dataclass(frozen=True)
class Belegvariante:
    belegart: str
    bezeichnung: str
    partnerrolle: str
    richtung: str  # Steuerrichtung: "verkauf" oder "einkauf"
    mit_preisen: bool
    bucht: bool  # Finance bucht diese Belegart
    folgebelege: tuple[str, ...] = ()


BELEGARTEN: dict[str, Belegvariante] = {
    v.belegart: v
    for v in (
        Belegvariante("sales_offer", "Angebot", "kunde", "verkauf", True, False, ("sales_order",)),
        Belegvariante("sales_order", "Auftrag", "kunde", "verkauf", True, False, ("sales_delivery", "sales_invoice")),
        Belegvariante("sales_delivery", "Lieferschein", "kunde", "verkauf", False, False, ("sales_invoice",)),
        Belegvariante("sales_invoice", "Rechnung", "kunde", "verkauf", True, True, ("sales_credit_memo",)),
        Belegvariante("sales_credit_memo", "Gutschrift", "kunde", "verkauf", True, True),
        Belegvariante("purchase_order", "Bestellung", "lieferant", "einkauf", True, False,
                      ("goods_receipt", "purchase_invoice")),
        Belegvariante("goods_receipt", "Wareneingang", "lieferant", "einkauf", False, False, ("purchase_invoice",)),
        Belegvariante("purchase_invoice", "Eingangsrechnung", "lieferant", "einkauf", True, True,
                      ("purchase_credit_memo",)),
        Belegvariante("purchase_credit_memo", "Einkaufsgutschrift", "lieferant", "einkauf", True, True),
    )
}


def ohne_preise(beleg: Beleg) -> Beleg:
    """Derselbe Beleg ohne Preisfelder und Summen — fuer Leser ohne Preisrecht und Varianten ohne Preise."""
    leer = {feld: None for feld in PREISFELDER}
    return beleg.model_copy(update={
        "preise_sichtbar": False,
        "summen": None,
        "positionen": [p.model_copy(update=leer) for p in beleg.positionen],
    })


def pruefe(beleg: Beleg) -> list[str]:
    """Verstoesse eines Belegs gegen den Vertrag seiner Variante. Leere Liste = vertragsgerecht."""
    variante = BELEGARTEN.get(beleg.belegart)
    if variante is None:
        return [f"Belegart {beleg.belegart!r} hat keine Variante."]
    fehler: list[str] = []
    if beleg.status not in STATUS:
        fehler.append(f"Status {beleg.status!r} ist kein Belegstand.")
    if beleg.partner is not None and beleg.partner.rolle != variante.partnerrolle:
        fehler.append(f"{variante.bezeichnung} verlangt die Partnerrolle {variante.partnerrolle!r}.")
    nummern = [p.pos_nr for p in beleg.positionen]
    if len(nummern) != len(set(nummern)):
        fehler.append("Positionsnummern sind nicht eindeutig.")
    for name in list(beleg.bausteine) + [b for p in beleg.positionen for b in p.bausteine]:
        if name not in BAUSTEINE:
            fehler.append(f"Baustein {name!r} ist nicht bekannt.")

    if variante.mit_preisen and beleg.preise_sichtbar:
        fehler += _pruefe_preise(beleg)
    else:
        warum = "ohne Preisrecht" if variante.mit_preisen else f"in der Variante {variante.bezeichnung}"
        if beleg.summen is not None:
            fehler.append(f"Summen duerfen {warum} nicht ausgeliefert werden.")
        for p in beleg.positionen:
            gesetzt = [f for f in PREISFELDER if getattr(p, f) is not None]
            if gesetzt:
                fehler.append(f"Position {p.pos_nr}: {', '.join(gesetzt)} duerfen {warum} nicht ausgeliefert werden.")
        if not variante.mit_preisen and beleg.preise_sichtbar:
            fehler.append(f"{variante.bezeichnung} traegt keine Preise; preise_sichtbar muss falsch sein.")

    if not variante.bucht and beleg.buchung.stand != "nicht_gebucht":
        fehler.append(f"{variante.bezeichnung} wird nicht gebucht.")
    if beleg.buchung.stand in ("gebucht", "storniert") and not beleg.buchung.journal_id:
        fehler.append("Gebucht ohne Journalbezug.")
    if beleg.buchung.stand == "pruefen" and not beleg.buchung.grund:
        fehler.append("Pruefvermerk ohne Grund.")

    for glied in beleg.kette:
        if glied.richtung == "nachfolger" and glied.belegart not in variante.folgebelege:
            fehler.append(f"{glied.belegart!r} ist kein Folgebeleg von {variante.bezeichnung}.")
        if glied.richtung == "vorgaenger":
            vor = BELEGARTEN.get(glied.belegart)
            if vor is None or beleg.belegart not in vor.folgebelege:
                fehler.append(f"{glied.belegart!r} ist kein Vorgaenger von {variante.bezeichnung}.")
    for aktion in beleg.aktionen:
        if aktion.folgebelegart and aktion.folgebelegart not in variante.folgebelege:
            fehler.append(f"Aktion {aktion.key!r}: {aktion.folgebelegart!r} ist kein Folgebeleg von {variante.bezeichnung}.")
        if not aktion.erlaubt and not aktion.grund:
            fehler.append(f"Aktion {aktion.key!r} ist gesperrt, nennt aber keinen Grund.")
    return fehler


def _pruefe_preise(beleg: Beleg) -> list[str]:
    fehler: list[str] = []
    if beleg.summen is None:
        return ["Summen fehlen."]
    for p in beleg.positionen:
        fehlt = [f for f in ("einzelpreis", "netto", "steuer", "brutto") if getattr(p, f) is None]
        if fehlt:
            fehler.append(f"Position {p.pos_nr}: {', '.join(fehlt)} fehlt.")
    if fehler:
        return fehler
    for feld in ("netto", "steuer", "brutto"):
        aus_positionen = sum((getattr(p, feld) for p in beleg.positionen), Decimal("0"))
        if aus_positionen != getattr(beleg.summen, feld):
            fehler.append(f"Summe {feld} {getattr(beleg.summen, feld)} weicht von den Positionen ab ({aus_positionen}).")
    if beleg.summen.netto + beleg.summen.steuer != beleg.summen.brutto:
        fehler.append("Netto und Steuer ergeben nicht Brutto.")
    return fehler


# ── Abbildung der bisherigen Feldnamen ────────────────────────────────────────
# Je Beleg-ScreenDefinition: Feld im Reiter ``kopf`` bzw. Spalte der Tabelle ``positionen`` -> Ziel im Vertrag.
# Ziel ist ein Pfad im Vertrag (``partner.name``, ``positionen[].menge``, ``kette[].beleg_nr``) oder
# ``baustein:<name>`` fuer einen fachlichen Sonderteil.

_KUNDE = {"customer_name": "partner.name", "customer_number": "partner.nummer"}

ABBILDUNG: dict[str, dict[str, dict[str, str]]] = {
    "sales/sales-order": {
        "kopf": {
            "order_number": "beleg_nr", **_KUNDE, "status": "status", "currency": "waehrung",
            "total_amount": "summen.brutto", "subject": "baustein:texte", "notes": "baustein:texte",
            "delivery_date": "baustein:lieferung", "shipping_method": "baustein:lieferung",
            "delivery_address": "baustein:lieferung", "contact_person": "baustein:kontakt",
            "payment_terms": "baustein:zahlung",
        },
        "positionen": {
            "line_number": "positionen[].pos_nr", "article_number": "positionen[].artikel_nr",
            "description": "positionen[].bezeichnung", "quantity": "positionen[].menge",
            "discount_percent": "positionen[].rabatt_prozent", "unit_price": "positionen[].einzelpreis",
            "line_total": "positionen[].netto",
        },
    },
    "sales/delivery-note": {
        "kopf": {
            "delivery_note_number": "beleg_nr", **_KUNDE, "status": "status", "delivery_date": "belegdatum",
            "sales_order_number": "kette[].beleg_nr", "invoice_number": "kette[].beleg_nr",
            "is_self_pickup": "baustein:lieferung", "truck_number": "baustein:lieferung",
            "branch_name": "baustein:organisation",
        },
        "positionen": {
            "pos_nr": "positionen[].pos_nr", "artikel_nr": "positionen[].artikel_nr",
            "bezeichnung": "positionen[].bezeichnung", "menge": "positionen[].menge",
            "einheit": "positionen[].einheit", "charge": "positionen[].charge",
        },
    },
    "sales/invoice": {
        "kopf": {
            "invoice_number": "beleg_nr", **_KUNDE, "status": "status", "invoice_date": "belegdatum",
            "due_date": "baustein:zahlung", "net_amount": "summen.netto", "vat_amount": "summen.steuer",
            "gross_amount": "summen.brutto",
        },
        "positionen": {
            "line_no": "positionen[].pos_nr", "article_number": "positionen[].artikel_nr",
            "description": "positionen[].bezeichnung", "quantity": "positionen[].menge",
            "unit": "positionen[].einheit", "unit_price": "positionen[].einzelpreis",
            "net_amount": "positionen[].netto", "herkunft": "kette[].beleg_nr",
        },
    },
    "einkauf/purchase-order": {
        "kopf": {
            "bestellnummer": "beleg_nr", "status": "status", "lieferant_nr": "partner.nummer",
            "lieferant_name": "partner.name", "bestelldatum": "belegdatum", "waehrung": "waehrung",
            "netto_summe": "summen.netto", "brutto_summe": "summen.brutto",
            "bestellfall": "baustein:bestellfall", "kreditor_konto": "baustein:kontierung",
            "ansprechpartner": "baustein:kontakt", "niederlassung_name": "baustein:organisation",
            "kostenstelle": "baustein:organisation", "kommission": "baustein:organisation",
            "erstellt_von": "baustein:organisation", "lieferdatum_wunsch": "baustein:lieferung",
            "lieferdatum_zugesagt": "baustein:lieferung", "ladetermin_ab": "baustein:lieferung",
            "ladetermin": "baustein:lieferung", "lade_datum": "baustein:lieferung",
            "incoterms": "baustein:lieferung", "versand_art": "baustein:lieferung",
            "lieferadresse": "baustein:lieferung", "unsere_referenz": "baustein:referenzen",
            "ihre_referenz": "baustein:referenzen",
        },
        "positionen": {
            "pos_nr": "positionen[].pos_nr", "artikel_nr": "positionen[].artikel_nr",
            "bezeichnung": "positionen[].bezeichnung", "menge": "positionen[].menge",
            "menge_geliefert": "positionen[].menge_uebernommen", "menge_offen": "positionen[].menge_offen",
            "einheit": "positionen[].einheit", "einzelpreis": "positionen[].einzelpreis",
            "betrag": "positionen[].netto", "lieferanten_artnr": "baustein:einkauf",
            "gebinde_menge": "baustein:gebinde", "gebinde_einheit": "baustein:gebinde",
            "preis_einheit": "baustein:gebinde", "gewicht_kg": "baustein:gebinde",
            "kontrakt_nr": "baustein:kontrakt", "lager": "baustein:lager", "lagerhalle": "baustein:lager",
            "lagerfach": "baustein:lager", "mindestmenge": "baustein:bestellfall",
            "maximalmenge": "baustein:bestellfall",
        },
    },
    "finance/ap-invoice": {
        "kopf": {
            "beleg_nr": "beleg_nr", "kreditor": "partner.name", "datum": "belegdatum", "status": "status",
            "brutto": "summen.brutto", "mwst": "summen.steuer", "faellig_am": "baustein:zahlung",
        },
        "positionen": {
            "pos_nr": "positionen[].pos_nr", "bezeichnung": "positionen[].bezeichnung",
            "menge": "positionen[].menge", "betrag": "positionen[].netto",
        },
    },
}

_LISTEN: dict[str, type[BaseModel]] = {
    "positionen": Belegposition, "kette": Kettenglied, "dokumente": Belegdokument,
    "historie": Historieneintrag, "aktionen": Belegaktion,
}
_TEILE: dict[str, type[BaseModel]] = {"partner": Partner, "summen": Summen, "buchung": Buchung}


def ziel_ist_gueltig(ziel: str) -> bool:
    """Ob ein Ziel der Abbildung im Vertrag existiert."""
    if ziel.startswith("baustein:"):
        return ziel.split(":", 1)[1] in BAUSTEINE
    kopf, _, rest = ziel.partition(".")
    if kopf.endswith("[]"):
        modell = _LISTEN.get(kopf[:-2])
        return modell is not None and rest in modell.model_fields
    if rest:
        modell = _TEILE.get(kopf)
        return modell is not None and rest in modell.model_fields
    return kopf in Beleg.model_fields
