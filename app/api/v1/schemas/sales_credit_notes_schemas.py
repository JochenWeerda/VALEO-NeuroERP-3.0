"""Schemas der Ausgangsgutschrift (aus ``app/api/v1/endpoints/sales_credit_notes.py`` ausgelagert, CI-GRUEN 14.10.2026;
Namen und Felder unveraendert, damit der OpenAPI-Vertrag gleich bleibt)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CreditNoteLineInput(BaseModel):
    article_number: Optional[str] = None
    description: str
    quantity: Decimal = Field(ge=Decimal("0"))
    unit_price: Decimal = Field(ge=Decimal("0"))
    # Steuerschluessel der Position (``tax_keys.code`` des Mandanten). Ohne ihn wird nicht gebucht.
    tax_code: Optional[str] = None
    # Kein Vorgabewert: Ein Satz, den niemand angegeben hat, ist keine Angabe.
    tax_rate: Optional[Decimal] = None


class CreditNoteLineOut(CreditNoteLineInput):
    id: str
    line_total: Decimal


class CreditNoteBase(BaseModel):
    credit_note_number: str = Field(..., min_length=1, max_length=64)
    customer_id: str
    customer_name: Optional[str] = None
    invoice_reference: Optional[str] = None
    reason: str = Field(..., min_length=1, max_length=500)
    # Brutto. Netto und Umsatzsteuer stehen daneben, sobald sie sich aus den Positionen ergeben.
    total_amount: Decimal = Decimal("0")
    net_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    # Kaufmaennische Rechnungskorrektur (Erloesminderung) oder Gutschrift nach Paragraf 14 UStG
    # (Abrechnung durch den Leistungsempfaenger — keine Erloesminderung).
    correction_type: Literal["rechnungskorrektur", "gutschrift_14_ustg"] = "rechnungskorrektur"
    currency: str = "EUR"
    status: str = "draft"
    notes: Optional[str] = None
    lines: List[CreditNoteLineInput] = Field(default_factory=list)


class CreditNoteCreate(CreditNoteBase):
    tenant_id: Optional[str] = None


class CreditNoteOut(CreditNoteBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class SteuerVorschauIn(BaseModel):
    lines: List[CreditNoteLineInput] = Field(default_factory=list)


class SteuerVorschauGruppe(BaseModel):
    tax_code: str
    satz: Decimal
    netto: Decimal
    steuer: Decimal
    brutto: Decimal


class SteuerVorschauOut(BaseModel):
    """Was die Buchung aus den Positionen machen wuerde — oder warum sie nicht bucht."""

    geklaert: bool
    pruefgrund: Optional[str] = None
    netto: Decimal
    steuer: Optional[Decimal] = None
    brutto: Optional[Decimal] = None
    gruppen: List[SteuerVorschauGruppe] = Field(default_factory=list)


class CreditNoteDetailOut(CreditNoteOut):
    lines: List[CreditNoteLineOut] = Field(default_factory=list)  # type: ignore[assignment]
