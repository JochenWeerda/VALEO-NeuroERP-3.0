"""Feldvertrag der Bruecken-Masken: deklarierte Kopffelder, extra erlaubt.

Die Maske fragt nach diesen Schluesseln. Ein GET mit ``TypedObjectOut`` /
``EinkaufDocOut`` (extra=allow, nur ``id``) sagt OpenAPI nichts — das Gate
ist dann blind. Diese Modelle nennen die Kopffelder; zusaetzliche Schluessel
bleiben erlaubt.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import ConfigDict

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
    lieferant_name: Optional[str] = None
    bestelldatum: Optional[str] = None
    lieferdatum_wunsch: Optional[str] = None
    lieferdatum_zugesagt: Optional[str] = None
    netto_summe: Optional[float] = None
    brutto_summe: Optional[float] = None
    unsere_referenz: Optional[str] = None
    status: Optional[str] = None


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
