"""
Self-Billing Service für Ernte-Annahme.

Verwaltet Self-Billing Gutschriften, E-Rechnung-Erstellung und Dispute-Handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Protocol, Literal, List
from app.core.uuid7 import uuid7


InvoiceStatus = Literal["draft", "issued", "paid", "disputed", "cancelled"]
DisputeStatus = Literal["none", "raised", "resolved", "rejected"]
DisputeType = Literal["amount", "quality", "quantity", "other"]


@dataclass
class SelfBillingInvoice:
    """Self-Billing Gutschrift-Datenstruktur."""
    id: str
    tenant_id: str
    invoice_number: str
    total_net_amount_eur: Decimal
    total_vat_amount_eur: Decimal
    total_gross_amount_eur: Decimal
    vat_rate_percent: Decimal
    harvest_acceptance_id: Optional[str] = None
    provisional_invoice_number: Optional[str] = None
    status: InvoiceStatus = "draft"
    dispute_status: DisputeStatus = "none"
    dispute_reason: Optional[str] = None
    dispute_date: Optional[datetime] = None
    dispute_user_id: Optional[str] = None
    einvoice_xml: Optional[str] = None
    einvoice_pdf: Optional[bytes] = None
    einvoice_sent_at: Optional[datetime] = None
    einvoice_received_at: Optional[datetime] = None
    
    # Pflichttexte
    mandatory_texts: Optional[list[dict]] = None  # JSONB: [{"type": "...", "text": "..."}]
    
    # Audit
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


@dataclass
class CreditNoteCreate:
    """Input für Gutschrift-Erstellung."""
    tenant_id: str
    harvest_acceptance_id: str
    total_net_amount_eur: Decimal
    total_vat_amount_eur: Decimal
    total_gross_amount_eur: Decimal
    vat_rate_percent: Decimal
    invoice_number: Optional[str] = None
    provisional_invoice_number: Optional[str] = None
    mandatory_texts: Optional[list[dict]] = None
    created_by: Optional[str] = None


@dataclass
class DisputeCreate:
    """Input für Dispute-Erstellung."""
    invoice_id: str
    dispute_type: DisputeType
    dispute_reason: str
    disputed_amount_eur: Optional[Decimal] = None
    created_by: Optional[str] = None


@dataclass
class DisputeRecord:
    """Dispute-Record-Datenstruktur."""
    id: str
    tenant_id: str
    invoice_id: str
    
    # Dispute-Details
    dispute_type: DisputeType
    dispute_reason: str
    disputed_amount_eur: Optional[Decimal] = None
    
    # Status
    status: Literal["raised", "resolved", "rejected"] = "raised"
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Audit
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class SelfBillingRepository(Protocol):
    """Protocol für Self-Billing Repository."""
    
    def create_invoice(self, invoice: SelfBillingInvoice) -> SelfBillingInvoice:
        """Erstellt eine neue Gutschrift."""
        ...
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[SelfBillingInvoice]:
        """Ruft eine Gutschrift anhand der ID ab."""
        ...
    
    def get_invoice_by_harvest_acceptance(self, harvest_acceptance_id: str) -> Optional[SelfBillingInvoice]:
        """Ruft die Gutschrift für eine Ernte-Annahme ab."""
        ...
    
    def update_invoice(self, invoice_id: str, updates: dict) -> SelfBillingInvoice:
        """Aktualisiert eine Gutschrift."""
        ...
    
    def create_dispute(self, dispute: DisputeRecord) -> DisputeRecord:
        """Erstellt einen Dispute-Record."""
        ...
    
    def get_disputes_by_invoice(self, invoice_id: str) -> List[DisputeRecord]:
        """Ruft alle Disputes für eine Gutschrift ab."""
        ...


def _generate_invoice_number(tenant_id: str, harvest_acceptance_id: Optional[str] = None) -> str:
    """Generiert eine Gutschrifts-Nummer."""
    prefix = "GS"  # Gutschrift
    year = datetime.now().strftime("%Y")
    sequence = uuid7().replace("-", "")[:8].upper()
    
    if harvest_acceptance_id:
        return f"{prefix}-{year}-{harvest_acceptance_id[:8]}-{sequence}"
    return f"{prefix}-{year}-{sequence}"


def _get_mandatory_texts_for_taxation(taxation_type: str, vat_rate_percent: Decimal) -> list[dict]:
    """
    Generiert Pflichttexte basierend auf Besteuerungsart.
    
    Für §24-Pauschalierung: Spezielle Texte erforderlich.
    """
    texts = []
    
    if taxation_type == "ustg24_flat_rate":
        texts.append({
            "type": "taxation_notice",
            "text": "Rechnung nach §24 UStG (Pauschalierung)",
            "position": "header"
        })
        texts.append({
            "type": "vat_rate",
            "text": f"MwSt-Satz: {vat_rate_percent}% (Durchschnittssatz nach §24 UStG)",
            "position": "footer"
        })
    elif taxation_type == "small_business":
        texts.append({
            "type": "taxation_notice",
            "text": "Kleinunternehmerregelung nach §19 UStG",
            "position": "header"
        })
        texts.append({
            "type": "vat_rate",
            "text": "MwSt-Satz: 0% (Kleinunternehmer)",
            "position": "footer"
        })
    else:
        texts.append({
            "type": "vat_rate",
            "text": f"MwSt-Satz: {vat_rate_percent}%",
            "position": "footer"
        })
    
    # Self-Billing Pflichttext
    texts.append({
        "type": "self_billing_notice",
        "text": "Diese Rechnung wurde im Rahmen des Self-Billing-Verfahrens erstellt.",
        "position": "footer"
    })
    
    return texts


def create_credit_note(
    repo: SelfBillingRepository,
    create_input: CreditNoteCreate,
    taxation_type: str = "regular",
) -> SelfBillingInvoice:
    """
    Erstellt eine Self-Billing Gutschrift.
    
    Die Gutschrift wird im Status "draft" erstellt und muss explizit auf "issued" gesetzt werden.
    """
    # Generiere Rechnungsnummer falls nicht vorhanden
    invoice_number = create_input.invoice_number
    if not invoice_number:
        invoice_number = _generate_invoice_number(create_input.tenant_id, create_input.harvest_acceptance_id)
    
    # Generiere Pflichttexte falls nicht vorhanden
    mandatory_texts = create_input.mandatory_texts
    if not mandatory_texts:
        mandatory_texts = _get_mandatory_texts_for_taxation(taxation_type, create_input.vat_rate_percent)
    
    invoice = SelfBillingInvoice(
        id=f"sb_{uuid7().replace('-', '')[:16]}",
        tenant_id=create_input.tenant_id,
        harvest_acceptance_id=create_input.harvest_acceptance_id,
        invoice_number=invoice_number,
        provisional_invoice_number=create_input.provisional_invoice_number,
        status="draft",
        dispute_status="none",
        total_net_amount_eur=create_input.total_net_amount_eur,
        total_vat_amount_eur=create_input.total_vat_amount_eur,
        total_gross_amount_eur=create_input.total_gross_amount_eur,
        vat_rate_percent=create_input.vat_rate_percent,
        mandatory_texts=mandatory_texts,
        created_at=datetime.now(),
        created_by=create_input.created_by,
    )
    
    return repo.create_invoice(invoice)


def issue_invoice(
    repo: SelfBillingRepository,
    invoice_id: str,
    updated_by: Optional[str] = None,
) -> SelfBillingInvoice:
    """
    Gibt eine Gutschrift aus (Status: draft → issued).
    
    Nach Ausgabe kann die Gutschrift nicht mehr geändert werden (außer via Dispute).
    """
    invoice = repo.get_invoice_by_id(invoice_id)
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")
    
    if invoice.status != "draft":
        raise ValueError(f"Invoice {invoice_id} is not in draft status")
    
    return repo.update_invoice(invoice_id, {
        "status": "issued",
        "updated_by": updated_by,
        "updated_at": datetime.now(),
    })


def generate_einvoice_xrechnung(
    invoice: SelfBillingInvoice,
    supplier_data: dict,
    customer_data: dict,
    line_items: list[dict],
) -> str:
    """
    Generiert XRechnung XML für eine Gutschrift.
    
    XRechnung ist der deutsche Standard für strukturierte E-Rechnungen (EN16931).
    
    Args:
        invoice: Self-Billing Gutschrift
        supplier_data: Lieferantendaten (Name, Adresse, USt-ID, etc.)
        customer_data: Kundendaten (Name, Adresse, USt-ID, etc.)
        line_items: Rechnungspositionen
    
    Returns:
        XRechnung XML als String
    """
    # TODO: Vollständige XRechnung-Implementierung
    # Dies ist eine vereinfachte Version - in Produktion sollte eine Bibliothek wie
    # python-xrechnung oder ähnliches verwendet werden
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:ID>{invoice.invoice_number}</cbc:ID>
    <cbc:IssueDate>{invoice.created_at.strftime('%Y-%m-%d') if invoice.created_at else date.today().isoformat()}</cbc:IssueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
    
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>{supplier_data.get('name', '')}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{supplier_data.get('street', '')}</cbc:StreetName>
                <cbc:CityName>{supplier_data.get('city', '')}</cbc:CityName>
                <cbc:PostalZone>{supplier_data.get('postal_code', '')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>{supplier_data.get('country_code', 'DE')}</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>{supplier_data.get('vat_id', '')}</cbc:CompanyID>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>{customer_data.get('name', '')}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{customer_data.get('street', '')}</cbc:StreetName>
                <cbc:CityName>{customer_data.get('city', '')}</cbc:CityName>
                <cbc:PostalZone>{customer_data.get('postal_code', '')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>{customer_data.get('country_code', 'DE')}</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>{customer_data.get('vat_id', '')}</cbc:CompanyID>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingCustomerParty>
    
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="EUR">{invoice.total_vat_amount_eur}</cbc:TaxAmount>
    </cac:TaxTotal>
    
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="EUR">{invoice.total_net_amount_eur}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="EUR">{invoice.total_net_amount_eur}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="EUR">{invoice.total_gross_amount_eur}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="EUR">{invoice.total_gross_amount_eur}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
</Invoice>"""
    
    return xml


def generate_einvoice(
    repo: SelfBillingRepository,
    invoice_id: str,
    supplier_data: dict,
    customer_data: dict,
    line_items: list[dict],
    format: Literal["xrechnung", "zugferd"] = "xrechnung",
) -> SelfBillingInvoice:
    """
    Generiert E-Rechnung (XRechnung oder ZUGFeRD) für eine Gutschrift.
    
    Die E-Rechnung wird im invoice gespeichert und kann anschließend versendet werden.
    """
    invoice = repo.get_invoice_by_id(invoice_id)
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")
    
    if invoice.status not in ["draft", "issued"]:
        raise ValueError(f"Invoice {invoice_id} cannot be modified in status {invoice.status}")
    
    # Generiere XML
    if format == "xrechnung":
        einvoice_xml = generate_einvoice_xrechnung(invoice, supplier_data, customer_data, line_items)
    else:
        # TODO: ZUGFeRD-Implementierung
        raise NotImplementedError("ZUGFeRD format not yet implemented")
    
    return repo.update_invoice(invoice_id, {
        "einvoice_xml": einvoice_xml,
        "updated_by": None,  # TODO: Aus Request holen
        "updated_at": datetime.now(),
    })


def send_einvoice(
    repo: SelfBillingRepository,
    invoice_id: str,
    recipient_email: Optional[str] = None,
) -> SelfBillingInvoice:
    """
    Versendet E-Rechnung an den Empfänger.
    
    TODO: Integration mit E-Mail-Service oder E-Rechnung-Portal.
    """
    invoice = repo.get_invoice_by_id(invoice_id)
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")
    
    if not invoice.einvoice_xml:
        raise ValueError(f"Invoice {invoice_id} has no E-Rechnung XML")
    
    if invoice.status != "issued":
        raise ValueError(f"Invoice {invoice_id} must be in 'issued' status")
    
    # TODO: E-Mail-Versand oder Portal-Upload
    # Hier nur Status-Update
    
    return repo.update_invoice(invoice_id, {
        "einvoice_sent_at": datetime.now(),
        "updated_at": datetime.now(),
    })


def create_dispute(
    repo: SelfBillingRepository,
    dispute_input: DisputeCreate,
) -> tuple[SelfBillingInvoice, DisputeRecord]:
    """
    Erstellt einen Dispute-Record für eine Gutschrift.
    
    Bei Dispute wird die Gutschrift gesperrt (OP-Zahlung stoppen, USt/Vorsteuer-Status prüfen).
    """
    invoice = repo.get_invoice_by_id(dispute_input.invoice_id)
    if not invoice:
        raise ValueError(f"Invoice {dispute_input.invoice_id} not found")
    
    if invoice.status not in ["issued", "paid"]:
        raise ValueError(f"Invoice {dispute_input.invoice_id} cannot be disputed in status {invoice.status}")
    
    # Erstelle Dispute-Record
    dispute = DisputeRecord(
        id=f"dispute_{uuid7().replace('-', '')[:16]}",
        tenant_id=invoice.tenant_id,
        invoice_id=dispute_input.invoice_id,
        dispute_type=dispute_input.dispute_type,
        dispute_reason=dispute_input.dispute_reason,
        disputed_amount_eur=dispute_input.disputed_amount_eur,
        status="raised",
        created_at=datetime.now(),
        created_by=dispute_input.created_by,
    )
    
    dispute_record = repo.create_dispute(dispute)
    
    # Update Invoice Status
    updated_invoice = repo.update_invoice(dispute_input.invoice_id, {
        "status": "disputed",
        "dispute_status": "raised",
        "dispute_reason": dispute_input.dispute_reason,
        "dispute_date": datetime.now(),
        "dispute_user_id": dispute_input.created_by,
        "updated_at": datetime.now(),
    })
    
    return updated_invoice, dispute_record


def resolve_dispute(
    repo: SelfBillingRepository,
    dispute_id: str,
    resolution_notes: str,
    resolved_by: str,
    resolution_status: Literal["resolved", "rejected"] = "resolved",
) -> tuple[SelfBillingInvoice, DisputeRecord]:
    """
    Löst einen Dispute auf.
    
    Bei "resolved": Dispute wird akzeptiert, Gutschrift bleibt bestehen
    Bei "rejected": Dispute wird abgelehnt, Gutschrift bleibt bestehen
    """
    # TODO: Dispute-Record aus Repository holen
    # Hier vereinfacht - in Produktion sollte DisputeRepository verwendet werden
    
    # Update Invoice Status
    # TODO: Invoice-ID aus Dispute holen
    # updated_invoice = repo.update_invoice(invoice_id, {...})
    
    raise NotImplementedError("Dispute resolution not yet fully implemented")


