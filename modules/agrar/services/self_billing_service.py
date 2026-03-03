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


# Optional: Externer XRechnung-Generator für volle EN16931/Schematron-Konformität.
# Setze z. B. aus einem Modul, das zugpferd-xrechnung-peppol-generator o. ä. nutzt:
#   from modules.agrar.services.self_billing_service import set_xrechnung_generator
#   set_xrechnung_generator(my_lib.generate_ubl_invoice)
_xrechnung_generator: Optional[object] = None  # Callable[[invoice, supplier_data, customer_data, line_items], str] | None


def set_xrechnung_generator(callable_or_none: Optional[object]) -> None:
    """Setzt optionalen Generator für XRechnung-XML (UBL 2.1). Bei gesetzt wird er in generate_einvoice_xrechnung verwendet."""
    global _xrechnung_generator
    _xrechnung_generator = callable_or_none


def generate_einvoice_xrechnung(
    invoice: SelfBillingInvoice,
    supplier_data: dict,
    customer_data: dict,
    line_items: list[dict],
) -> str:
    """
    Generiert XRechnung XML für eine Gutschrift.
    
    XRechnung ist der deutsche Standard für strukturierte E-Rechnungen (EN16931).
    Wenn ein optionaler Generator gesetzt ist (set_xrechnung_generator), wird dieser
    aufgerufen; sonst wird eine vereinfachte UBL-Struktur erzeugt. Für volle
    Schematron-Konformität: zugpferd-xrechnung-peppol-generator o. ä. einbinden.
    
    Args:
        invoice: Self-Billing Gutschrift
        supplier_data: Lieferantendaten (Name, Adresse, USt-ID, etc.)
        customer_data: Kundendaten (Name, Adresse, USt-ID, etc.)
        line_items: Rechnungspositionen
    
    Returns:
        XRechnung XML als String
    """
    if _xrechnung_generator is not None and callable(_xrechnung_generator):
        try:
            return _xrechnung_generator(invoice, supplier_data, customer_data, line_items)
        except Exception:
            pass  # Fallback auf Standard-UBL
    # Vereinfachte XRechnung-UBL-Struktur
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
    
    # Generiere XML / PDF
    if format == "xrechnung":
        einvoice_xml = generate_einvoice_xrechnung(invoice, supplier_data, customer_data, line_items)
        return repo.update_invoice(invoice_id, {
            "einvoice_xml": einvoice_xml,
            "updated_at": datetime.now(),
        })
    else:
        pdf_bytes = generate_einvoice_zugferd(invoice, supplier_data, customer_data, line_items)
        import base64
        einvoice_xml = generate_einvoice_xrechnung(invoice, supplier_data, customer_data, line_items)
        return repo.update_invoice(invoice_id, {
            "einvoice_xml": einvoice_xml,
            "einvoice_pdf": base64.b64encode(pdf_bytes).decode("ascii"),
            "updated_at": datetime.now(),
        })


def _send_email_einvoice(
    recipient_email: str,
    invoice_number: str,
    xml_content: str,
    pdf_content_base64: Optional[str] = None,
) -> None:
    """
    Versendet E-Rechnung per E-Mail (SMTP).
    Nutzt app.core.config.settings: EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_USERNAME, EMAIL_PASSWORD.
    Bei fehlender SMTP-Konfiguration wird keine E-Mail versendet (stiller No-Op).
    """
    try:
        from app.core.config import settings
        if not settings.EMAIL_SMTP_SERVER or not recipient_email:
            return
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        msg = MIMEMultipart()
        msg["Subject"] = f"E-Rechnung {invoice_number}"
        msg["From"] = settings.EMAIL_USERNAME or "noreply@valeo-erp.local"
        msg["To"] = recipient_email
        msg.attach(MIMEText("Anbei die E-Rechnung im XRechnung-Format.", "plain", "utf-8"))

        part = MIMEBase("application", "xml")
        part.set_payload(xml_content.encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=f"invoice_{invoice_number}.xml")
        msg.attach(part)

        if pdf_content_base64:
            import base64
            part_pdf = MIMEBase("application", "pdf")
            part_pdf.set_payload(base64.b64decode(pdf_content_base64))
            encoders.encode_base64(part_pdf)
            part_pdf.add_header("Content-Disposition", "attachment", filename=f"invoice_{invoice_number}.pdf")
            msg.attach(part_pdf)

        with smtplib.SMTP(settings.EMAIL_SMTP_SERVER, settings.EMAIL_SMTP_PORT or 587) as smtp:
            if settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
                smtp.starttls()
                smtp.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception:
        pass  # Log in Produktion; hier kein Abhängigkeit auf logging


def send_einvoice(
    repo: SelfBillingRepository,
    invoice_id: str,
    recipient_email: Optional[str] = None,
) -> SelfBillingInvoice:
    """
    Versendet E-Rechnung an den Empfänger.
    Bei gesetzter SMTP-Konfiguration (EMAIL_SMTP_*) und recipient_email wird die E-Mail
    mit XML-Anhang (und optional PDF) versendet. Zusätzlich: E-Rechnung-Portale
    (z. B. E-Rechnung.gv.at, Peppol) können über einen separaten Adapter angebunden werden.
    """
    invoice = repo.get_invoice_by_id(invoice_id)
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")
    
    if not invoice.einvoice_xml:
        raise ValueError(f"Invoice {invoice_id} has no E-Rechnung XML")
    
    if invoice.status != "issued":
        raise ValueError(f"Invoice {invoice_id} must be in 'issued' status")
    
    if recipient_email:
        _send_email_einvoice(
            recipient_email=recipient_email,
            invoice_number=invoice.invoice_number,
            xml_content=invoice.einvoice_xml,
            pdf_content_base64=invoice.einvoice_pdf,
        )
    
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
    dispute = repo.get_dispute_by_id(dispute_id)
    if not dispute:
        raise ValueError(f"Dispute {dispute_id} not found")
    if dispute.status != "raised":
        raise ValueError(f"Dispute {dispute_id} is already in status '{dispute.status}', cannot resolve")

    resolved_dispute = repo.update_dispute(dispute_id, {
        "status": resolution_status,
        "resolution_notes": resolution_notes,
        "resolved_by": resolved_by,
        "resolved_at": datetime.now(),
        "updated_at": datetime.now(),
        "updated_by": resolved_by,
    })

    invoice_dispute_status = "resolved" if resolution_status == "resolved" else "rejected"
    updated_invoice = repo.update_invoice(dispute.invoice_id, {
        "dispute_status": invoice_dispute_status,
        "updated_at": datetime.now(),
        "updated_by": resolved_by,
    })

    return updated_invoice, resolved_dispute


def _build_zugferd_story(invoice: SelfBillingInvoice, supplier_data: dict, customer_data: dict) -> list:
    """Erstellt die reportlab-Story für das ZUGFeRD-Basis-PDF."""
    from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"Gutschrift {invoice.invoice_number}", styles["Heading1"]),
        Spacer(1, 8),
        Paragraph(f"Lieferant: {supplier_data.get('name', '')}", styles["Normal"]),
        Paragraph(f"Empfänger: {customer_data.get('name', '')}", styles["Normal"]),
        Spacer(1, 8),
        Paragraph(
            f"Nettobetrag: {invoice.total_net_amount_eur} EUR", styles["Normal"]
        ),
        Paragraph(
            f"MwSt ({invoice.vat_rate_percent}%): {invoice.total_vat_amount_eur} EUR",
            styles["Normal"],
        ),
        Paragraph(
            f"Bruttobetrag: {invoice.total_gross_amount_eur} EUR", styles["Normal"]
        ),
        Spacer(1, 8),
        Paragraph(
            "Diese Rechnung wurde im Rahmen des Self-Billing-Verfahrens erstellt.",
            styles["Normal"],
        ),
    ]
    return story


def generate_einvoice_zugferd(
    invoice: SelfBillingInvoice,
    supplier_data: dict,
    customer_data: dict,
    line_items: list[dict],
) -> bytes:
    """
    Generiert ZUGFeRD PDF/A-3 mit eingebettetem EN16931-XML.

    1. XML via generate_einvoice_xrechnung erstellen
    2. Basis-PDF via reportlab bauen
    3. XML in PDF/A-3 einbetten via factur-x
    """
    import base64
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import A4

    # 1. EN16931-XML erzeugen
    xml_str = generate_einvoice_xrechnung(invoice, supplier_data, customer_data, line_items)

    # 2. Basis-PDF via reportlab
    pdf_buf = BytesIO()
    story = _build_zugferd_story(invoice, supplier_data, customer_data)
    SimpleDocTemplate(pdf_buf, pagesize=A4).build(story)
    pdf_bytes = pdf_buf.getvalue()

    # 3. XML in PDF/A-3 einbetten (factur-x)
    try:
        from facturx import generate_facturx_from_file

        out_buf = BytesIO()
        generate_facturx_from_file(
            BytesIO(pdf_bytes),
            xml_str.encode("utf-8"),
            "EN 16931",
            out_buf,
        )
        return out_buf.getvalue()
    except Exception:
        # Fallback: normales PDF zurückgeben (ohne eingebettetes XML)
        return pdf_bytes


