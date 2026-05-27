"""
E-Rechnung XRechnung/ZUGFeRD Generator (EN 16931).

Datenmodell-neutraler Generator für strukturierte elektronische Rechnungen
nach EN 16931 (deutscher Standard: XRechnung 3.0, Hybrid: ZUGFeRD 2.x Profil EN 16931).

Schließt die gesetzliche Lücke aus dem Wachstumschancengesetz
(B2B-Pflicht-Empfang ab 01.01.2025, B2B-Pflicht-Versand ab 01.01.2027/2028).

Slice-006: Für reguläre B2B-Verkaufsrechnungen (SalesInvoice).
Der bestehende Self-Billing-Generator (modules/agrar/services/self_billing_service.py)
bleibt für Agrar-Gutschriften zuständig.

Optional kann ein externer Generator (z. B. zugpferd-xrechnung-peppol-generator) via
set_xrechnung_generator() registriert werden für volle Schematron-Konformität.
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable, Optional
from xml.sax.saxutils import escape as xml_escape

from typing_extensions import TypedDict

logger = logging.getLogger(__name__)

UBL_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
CAC_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
CBC_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"

XRECHNUNG_CUSTOMIZATION_ID = (
    "urn:cen.eu:en16931:2017"
    "#compliant#urn:xoev-de:kosit:standard:xrechnung_3.0"
)
XRECHNUNG_PROFILE_ID = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"

ZUGFERD_CII_NS = "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
ZUGFERD_RAM_NS = (
    "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
)
ZUGFERD_UDT_NS = "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
ZUGFERD_RSM_NS = "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
ZUGFERD_GUIDELINE_EN16931 = (
    "urn:cen.eu:en16931:2017"
)


class PartyAddress(TypedDict, total=False):
    name: str
    street: str
    postal_code: str
    city: str
    country_code: str
    vat_id: str
    email: str


class InvoiceLineDict(TypedDict, total=False):
    line_id: str
    article: str
    description: str
    quantity: float
    unit_code: str
    unit_price_net: float
    line_net_amount: float
    vat_rate_percent: float
    vat_category_code: str


class EInvoiceInput(TypedDict, total=False):
    invoice_number: str
    invoice_date: str
    invoice_type_code: str
    currency: str
    supplier: PartyAddress
    customer: PartyAddress
    lines: list[InvoiceLineDict]
    total_net: float
    total_vat: float
    total_gross: float
    payment_terms_text: str
    payment_due_date: str
    buyer_reference: str


_xrechnung_generator: Optional[Callable[[EInvoiceInput], str]] = None


def set_xrechnung_generator(callable_or_none: Optional[Callable[[EInvoiceInput], str]]) -> None:
    """Setzt optionalen externen XRechnung-Generator für volle Schematron-Konformität."""
    global _xrechnung_generator
    _xrechnung_generator = callable_or_none


def _money(value: Any, *, places: int = 2) -> str:
    """Formatiert Geldbetrag für UBL/CII (2 Nachkommastellen, Punkt als Dezimaltrenner)."""
    if value is None:
        return "0.00"
    if isinstance(value, str):
        value = Decimal(value.replace(",", "."))
    elif not isinstance(value, Decimal):
        value = Decimal(str(value))
    q = Decimal(10) ** -places
    return str(value.quantize(q, rounding=ROUND_HALF_UP))


def _quantity(value: Any, *, places: int = 4) -> str:
    """Formatiert Mengen-Wert (4 Nachkommastellen üblich)."""
    if value is None:
        return "0"
    if isinstance(value, str):
        value = Decimal(value.replace(",", "."))
    elif not isinstance(value, Decimal):
        value = Decimal(str(value))
    q = Decimal(10) ** -places
    return str(value.quantize(q, rounding=ROUND_HALF_UP))


def _esc(value: Any) -> str:
    """XML-escape mit None-Schutz."""
    if value is None:
        return ""
    return xml_escape(str(value))


def _aggregate_tax_subtotals(lines: list[InvoiceLineDict]) -> list[dict]:
    """Aggregiert TaxSubtotal pro VAT-Rate für BG-23 TaxBreakdown."""
    groups: dict[tuple[float, str], dict] = {}
    for ln in lines:
        rate = float(ln.get("vat_rate_percent", 0) or 0)
        cat = str(ln.get("vat_category_code", "S"))
        net = Decimal(str(ln.get("line_net_amount", 0) or 0))
        key = (rate, cat)
        if key not in groups:
            groups[key] = {
                "rate": rate,
                "category": cat,
                "taxable_amount": Decimal("0"),
                "tax_amount": Decimal("0"),
            }
        groups[key]["taxable_amount"] += net
        groups[key]["tax_amount"] += (net * Decimal(str(rate)) / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    return list(groups.values())


def build_xrechnung_xml(data: EInvoiceInput) -> str:
    """
    Generiert XRechnung-3.0-konformes UBL-2.1-XML mit EN-16931-Pflichtfeldern.

    Implementiert (Business Terms nach EN 16931):
    - BT-1 Invoice number (cbc:ID)
    - BT-2 Invoice issue date (cbc:IssueDate)
    - BT-3 Invoice type code (cbc:InvoiceTypeCode, default 380)
    - BT-5 Invoice currency (cbc:DocumentCurrencyCode)
    - BT-9 Payment due date (cbc:DueDate)
    - BT-10 Buyer reference (cbc:BuyerReference)
    - BT-22 Note (cbc:Note)
    - BT-27/28/30 Seller details (cac:AccountingSupplierParty)
    - BT-31 Seller VAT identifier
    - BT-44/47/49 Buyer details (cac:AccountingCustomerParty)
    - BT-48 Buyer VAT identifier
    - BG-22 Document totals (cac:LegalMonetaryTotal)
      BT-106 Sum of line net amounts, BT-109 Invoice total net, BT-110 Invoice total VAT,
      BT-112 Invoice total with VAT, BT-115 Amount due for payment
    - BG-23 VAT breakdown (cac:TaxTotal/cac:TaxSubtotal) pro VAT-Rate
      BT-110/116/118/119
    - BG-25 Invoice lines (cac:InvoiceLine)
      BT-126/127/129/130/131/146/148/152

    Externer Generator (Schematron-volle Lib) wird verwendet, falls registriert.
    """
    if _xrechnung_generator is not None:
        try:
            return _xrechnung_generator(data)
        except Exception as e:  # noqa: BLE001
            logger.warning("External xrechnung generator failed, using fallback: %s", e)

    invoice_number = _esc(data.get("invoice_number", ""))
    invoice_date = data.get("invoice_date") or date.today().isoformat()
    invoice_type = _esc(data.get("invoice_type_code", "380"))
    currency = _esc(data.get("currency", "EUR"))
    buyer_reference = _esc(data.get("buyer_reference", invoice_number))
    payment_due = data.get("payment_due_date") or invoice_date
    payment_terms = _esc(data.get("payment_terms_text", "Zahlbar gemäß Vereinbarung"))

    supplier = data.get("supplier") or {}
    customer = data.get("customer") or {}
    lines = data.get("lines") or []

    total_net = data.get("total_net", sum(float(ln.get("line_net_amount", 0) or 0) for ln in lines))
    total_vat = data.get("total_vat", 0)
    if total_vat == 0 and lines:
        total_vat = sum(
            float(ln.get("line_net_amount", 0) or 0)
            * float(ln.get("vat_rate_percent", 0) or 0)
            / 100.0
            for ln in lines
        )
    total_gross = data.get("total_gross", float(total_net) + float(total_vat))

    tax_subtotals = _aggregate_tax_subtotals(lines)

    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        f'<Invoice xmlns="{UBL_NS}"'
        f' xmlns:cac="{CAC_NS}"'
        f' xmlns:cbc="{CBC_NS}">'
    )
    parts.append(f"<cbc:CustomizationID>{XRECHNUNG_CUSTOMIZATION_ID}</cbc:CustomizationID>")
    parts.append(f"<cbc:ProfileID>{XRECHNUNG_PROFILE_ID}</cbc:ProfileID>")
    parts.append(f"<cbc:ID>{invoice_number}</cbc:ID>")
    parts.append(f"<cbc:IssueDate>{_esc(invoice_date)}</cbc:IssueDate>")
    parts.append(f"<cbc:DueDate>{_esc(payment_due)}</cbc:DueDate>")
    parts.append(f"<cbc:InvoiceTypeCode>{invoice_type}</cbc:InvoiceTypeCode>")
    note = data.get("payment_terms_text")
    if note:
        parts.append(f"<cbc:Note>{_esc(note)}</cbc:Note>")
    parts.append(f"<cbc:DocumentCurrencyCode>{currency}</cbc:DocumentCurrencyCode>")
    parts.append(f"<cbc:BuyerReference>{buyer_reference}</cbc:BuyerReference>")

    parts.append("<cac:AccountingSupplierParty><cac:Party>")
    parts.append(f"<cac:PartyName><cbc:Name>{_esc(supplier.get('name', ''))}</cbc:Name></cac:PartyName>")
    parts.append("<cac:PostalAddress>")
    parts.append(f"<cbc:StreetName>{_esc(supplier.get('street', ''))}</cbc:StreetName>")
    parts.append(f"<cbc:CityName>{_esc(supplier.get('city', ''))}</cbc:CityName>")
    parts.append(f"<cbc:PostalZone>{_esc(supplier.get('postal_code', ''))}</cbc:PostalZone>")
    parts.append(
        f"<cac:Country><cbc:IdentificationCode>"
        f"{_esc(supplier.get('country_code', 'DE'))}"
        f"</cbc:IdentificationCode></cac:Country>"
    )
    parts.append("</cac:PostalAddress>")
    if supplier.get("vat_id"):
        parts.append(
            "<cac:PartyTaxScheme>"
            f"<cbc:CompanyID>{_esc(supplier['vat_id'])}</cbc:CompanyID>"
            "<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>"
            "</cac:PartyTaxScheme>"
        )
    parts.append(
        f"<cac:PartyLegalEntity><cbc:RegistrationName>{_esc(supplier.get('name', ''))}"
        "</cbc:RegistrationName></cac:PartyLegalEntity>"
    )
    if supplier.get("email"):
        parts.append(
            "<cac:Contact>"
            f"<cbc:ElectronicMail>{_esc(supplier['email'])}</cbc:ElectronicMail>"
            "</cac:Contact>"
        )
    parts.append("</cac:Party></cac:AccountingSupplierParty>")

    parts.append("<cac:AccountingCustomerParty><cac:Party>")
    parts.append(f"<cac:PartyName><cbc:Name>{_esc(customer.get('name', ''))}</cbc:Name></cac:PartyName>")
    parts.append("<cac:PostalAddress>")
    parts.append(f"<cbc:StreetName>{_esc(customer.get('street', ''))}</cbc:StreetName>")
    parts.append(f"<cbc:CityName>{_esc(customer.get('city', ''))}</cbc:CityName>")
    parts.append(f"<cbc:PostalZone>{_esc(customer.get('postal_code', ''))}</cbc:PostalZone>")
    parts.append(
        f"<cac:Country><cbc:IdentificationCode>"
        f"{_esc(customer.get('country_code', 'DE'))}"
        f"</cbc:IdentificationCode></cac:Country>"
    )
    parts.append("</cac:PostalAddress>")
    if customer.get("vat_id"):
        parts.append(
            "<cac:PartyTaxScheme>"
            f"<cbc:CompanyID>{_esc(customer['vat_id'])}</cbc:CompanyID>"
            "<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>"
            "</cac:PartyTaxScheme>"
        )
    parts.append(
        f"<cac:PartyLegalEntity><cbc:RegistrationName>{_esc(customer.get('name', ''))}"
        "</cbc:RegistrationName></cac:PartyLegalEntity>"
    )
    parts.append("</cac:Party></cac:AccountingCustomerParty>")

    parts.append(
        f'<cac:PaymentTerms><cbc:Note>{payment_terms}</cbc:Note></cac:PaymentTerms>'
    )

    parts.append(
        f'<cac:TaxTotal>'
        f'<cbc:TaxAmount currencyID="{currency}">{_money(total_vat)}</cbc:TaxAmount>'
    )
    for sub in tax_subtotals:
        parts.append(
            "<cac:TaxSubtotal>"
            f'<cbc:TaxableAmount currencyID="{currency}">{_money(sub["taxable_amount"])}</cbc:TaxableAmount>'
            f'<cbc:TaxAmount currencyID="{currency}">{_money(sub["tax_amount"])}</cbc:TaxAmount>'
            "<cac:TaxCategory>"
            f'<cbc:ID>{_esc(sub["category"])}</cbc:ID>'
            f'<cbc:Percent>{_money(sub["rate"])}</cbc:Percent>'
            "<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>"
            "</cac:TaxCategory>"
            "</cac:TaxSubtotal>"
        )
    parts.append("</cac:TaxTotal>")

    parts.append(
        "<cac:LegalMonetaryTotal>"
        f'<cbc:LineExtensionAmount currencyID="{currency}">{_money(total_net)}</cbc:LineExtensionAmount>'
        f'<cbc:TaxExclusiveAmount currencyID="{currency}">{_money(total_net)}</cbc:TaxExclusiveAmount>'
        f'<cbc:TaxInclusiveAmount currencyID="{currency}">{_money(total_gross)}</cbc:TaxInclusiveAmount>'
        f'<cbc:PayableAmount currencyID="{currency}">{_money(total_gross)}</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
    )

    for idx, ln in enumerate(lines, start=1):
        line_id = _esc(ln.get("line_id", str(idx)))
        qty = _quantity(ln.get("quantity", 0))
        unit = _esc(ln.get("unit_code", "C62"))
        net = _money(ln.get("line_net_amount", 0))
        unit_price = _money(ln.get("unit_price_net", 0))
        article = _esc(ln.get("article", ""))
        description = _esc(ln.get("description", ln.get("article", "")))
        rate = ln.get("vat_rate_percent", 0)
        category = _esc(ln.get("vat_category_code", "S"))
        parts.append(
            "<cac:InvoiceLine>"
            f"<cbc:ID>{line_id}</cbc:ID>"
            f'<cbc:InvoicedQuantity unitCode="{unit}">{qty}</cbc:InvoicedQuantity>'
            f'<cbc:LineExtensionAmount currencyID="{currency}">{net}</cbc:LineExtensionAmount>'
            f"<cac:Item><cbc:Name>{article}</cbc:Name>"
            f"<cbc:Description>{description}</cbc:Description>"
            "<cac:ClassifiedTaxCategory>"
            f"<cbc:ID>{category}</cbc:ID>"
            f"<cbc:Percent>{_money(rate)}</cbc:Percent>"
            "<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>"
            "</cac:ClassifiedTaxCategory>"
            "</cac:Item>"
            "<cac:Price>"
            f'<cbc:PriceAmount currencyID="{currency}">{unit_price}</cbc:PriceAmount>'
            "</cac:Price>"
            "</cac:InvoiceLine>"
        )

    parts.append("</Invoice>")
    return "".join(parts)


def build_zugferd_cii_xml(data: EInvoiceInput) -> str:
    """
    Generiert ZUGFeRD-2.x-konformes CII-XML (CrossIndustryInvoice, Profil EN 16931 "Comfort").
    Wird in PDF/A-3 eingebettet (siehe build_zugferd_pdf).
    """
    invoice_number = _esc(data.get("invoice_number", ""))
    invoice_date = data.get("invoice_date") or date.today().isoformat()
    invoice_type = _esc(data.get("invoice_type_code", "380"))
    currency = _esc(data.get("currency", "EUR"))
    issue_date_compact = invoice_date.replace("-", "")

    supplier = data.get("supplier") or {}
    customer = data.get("customer") or {}
    lines = data.get("lines") or []

    total_net = data.get("total_net", sum(float(ln.get("line_net_amount", 0) or 0) for ln in lines))
    total_vat = data.get("total_vat", 0)
    if total_vat == 0 and lines:
        total_vat = sum(
            float(ln.get("line_net_amount", 0) or 0)
            * float(ln.get("vat_rate_percent", 0) or 0)
            / 100.0
            for ln in lines
        )
    total_gross = data.get("total_gross", float(total_net) + float(total_vat))

    tax_subtotals = _aggregate_tax_subtotals(lines)

    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        '<rsm:CrossIndustryInvoice'
        f' xmlns:rsm="{ZUGFERD_RSM_NS}"'
        f' xmlns:ram="{ZUGFERD_RAM_NS}"'
        f' xmlns:udt="{ZUGFERD_UDT_NS}">'
    )
    parts.append(
        "<rsm:ExchangedDocumentContext>"
        "<ram:GuidelineSpecifiedDocumentContextParameter>"
        f"<ram:ID>{ZUGFERD_GUIDELINE_EN16931}</ram:ID>"
        "</ram:GuidelineSpecifiedDocumentContextParameter>"
        "</rsm:ExchangedDocumentContext>"
    )
    parts.append(
        "<rsm:ExchangedDocument>"
        f"<ram:ID>{invoice_number}</ram:ID>"
        f"<ram:TypeCode>{invoice_type}</ram:TypeCode>"
        "<ram:IssueDateTime>"
        f'<udt:DateTimeString format="102">{issue_date_compact}</udt:DateTimeString>'
        "</ram:IssueDateTime>"
        "</rsm:ExchangedDocument>"
    )

    parts.append("<rsm:SupplyChainTradeTransaction>")
    for idx, ln in enumerate(lines, start=1):
        parts.append(
            "<ram:IncludedSupplyChainTradeLineItem>"
            f"<ram:AssociatedDocumentLineDocument><ram:LineID>{_esc(ln.get('line_id', str(idx)))}</ram:LineID></ram:AssociatedDocumentLineDocument>"
            "<ram:SpecifiedTradeProduct>"
            f"<ram:Name>{_esc(ln.get('article', ''))}</ram:Name>"
            "</ram:SpecifiedTradeProduct>"
            "<ram:SpecifiedLineTradeAgreement>"
            "<ram:NetPriceProductTradePrice>"
            f'<ram:ChargeAmount>{_money(ln.get("unit_price_net", 0))}</ram:ChargeAmount>'
            "</ram:NetPriceProductTradePrice>"
            "</ram:SpecifiedLineTradeAgreement>"
            "<ram:SpecifiedLineTradeDelivery>"
            f'<ram:BilledQuantity unitCode="{_esc(ln.get("unit_code", "C62"))}">{_quantity(ln.get("quantity", 0))}</ram:BilledQuantity>'
            "</ram:SpecifiedLineTradeDelivery>"
            "<ram:SpecifiedLineTradeSettlement>"
            "<ram:ApplicableTradeTax>"
            "<ram:TypeCode>VAT</ram:TypeCode>"
            f"<ram:CategoryCode>{_esc(ln.get('vat_category_code', 'S'))}</ram:CategoryCode>"
            f"<ram:RateApplicablePercent>{_money(ln.get('vat_rate_percent', 0))}</ram:RateApplicablePercent>"
            "</ram:ApplicableTradeTax>"
            "<ram:SpecifiedTradeSettlementLineMonetarySummation>"
            f'<ram:LineTotalAmount>{_money(ln.get("line_net_amount", 0))}</ram:LineTotalAmount>'
            "</ram:SpecifiedTradeSettlementLineMonetarySummation>"
            "</ram:SpecifiedLineTradeSettlement>"
            "</ram:IncludedSupplyChainTradeLineItem>"
        )

    parts.append(
        "<ram:ApplicableHeaderTradeAgreement>"
        "<ram:SellerTradeParty>"
        f"<ram:Name>{_esc(supplier.get('name', ''))}</ram:Name>"
        "<ram:PostalTradeAddress>"
        f"<ram:PostcodeCode>{_esc(supplier.get('postal_code', ''))}</ram:PostcodeCode>"
        f"<ram:LineOne>{_esc(supplier.get('street', ''))}</ram:LineOne>"
        f"<ram:CityName>{_esc(supplier.get('city', ''))}</ram:CityName>"
        f"<ram:CountryID>{_esc(supplier.get('country_code', 'DE'))}</ram:CountryID>"
        "</ram:PostalTradeAddress>"
        + (
            "<ram:SpecifiedTaxRegistration>"
            f'<ram:ID schemeID="VA">{_esc(supplier.get("vat_id", ""))}</ram:ID>'
            "</ram:SpecifiedTaxRegistration>"
            if supplier.get("vat_id") else ""
        )
        + "</ram:SellerTradeParty>"
        "<ram:BuyerTradeParty>"
        f"<ram:Name>{_esc(customer.get('name', ''))}</ram:Name>"
        "<ram:PostalTradeAddress>"
        f"<ram:PostcodeCode>{_esc(customer.get('postal_code', ''))}</ram:PostcodeCode>"
        f"<ram:LineOne>{_esc(customer.get('street', ''))}</ram:LineOne>"
        f"<ram:CityName>{_esc(customer.get('city', ''))}</ram:CityName>"
        f"<ram:CountryID>{_esc(customer.get('country_code', 'DE'))}</ram:CountryID>"
        "</ram:PostalTradeAddress>"
        + (
            "<ram:SpecifiedTaxRegistration>"
            f'<ram:ID schemeID="VA">{_esc(customer.get("vat_id", ""))}</ram:ID>'
            "</ram:SpecifiedTaxRegistration>"
            if customer.get("vat_id") else ""
        )
        + "</ram:BuyerTradeParty>"
        "</ram:ApplicableHeaderTradeAgreement>"
    )

    parts.append("<ram:ApplicableHeaderTradeDelivery/>")
    parts.append("<ram:ApplicableHeaderTradeSettlement>")
    parts.append(f"<ram:InvoiceCurrencyCode>{currency}</ram:InvoiceCurrencyCode>")
    for sub in tax_subtotals:
        parts.append(
            "<ram:ApplicableTradeTax>"
            f"<ram:CalculatedAmount>{_money(sub['tax_amount'])}</ram:CalculatedAmount>"
            "<ram:TypeCode>VAT</ram:TypeCode>"
            f"<ram:BasisAmount>{_money(sub['taxable_amount'])}</ram:BasisAmount>"
            f"<ram:CategoryCode>{_esc(sub['category'])}</ram:CategoryCode>"
            f"<ram:RateApplicablePercent>{_money(sub['rate'])}</ram:RateApplicablePercent>"
            "</ram:ApplicableTradeTax>"
        )
    parts.append(
        "<ram:SpecifiedTradeSettlementHeaderMonetarySummation>"
        f"<ram:LineTotalAmount>{_money(total_net)}</ram:LineTotalAmount>"
        f"<ram:TaxBasisTotalAmount>{_money(total_net)}</ram:TaxBasisTotalAmount>"
        f'<ram:TaxTotalAmount currencyID="{currency}">{_money(total_vat)}</ram:TaxTotalAmount>'
        f"<ram:GrandTotalAmount>{_money(total_gross)}</ram:GrandTotalAmount>"
        f"<ram:DuePayableAmount>{_money(total_gross)}</ram:DuePayableAmount>"
        "</ram:SpecifiedTradeSettlementHeaderMonetarySummation>"
    )
    parts.append("</ram:ApplicableHeaderTradeSettlement>")
    parts.append("</rsm:SupplyChainTradeTransaction>")
    parts.append("</rsm:CrossIndustryInvoice>")
    return "".join(parts)


def build_zugferd_pdf(data: EInvoiceInput, *, base_pdf: Optional[bytes] = None) -> bytes:
    """
    Generiert ZUGFeRD PDF/A-3 mit eingebettetem CII-XML (Profil EN 16931).

    Args:
        data: EInvoiceInput
        base_pdf: Optionales bereits erzeugtes PDF (sonst wird ein minimales generiert)

    Returns:
        PDF/A-3-Bytes mit eingebettetem `factur-x.xml`

    Raises:
        RuntimeError: wenn die factur-x Library nicht verfügbar ist
    """
    cii_xml = build_zugferd_cii_xml(data)

    if base_pdf is None:
        base_pdf = _build_minimal_pdf(data)

    try:
        from io import BytesIO

        from facturx import generate_facturx_from_file  # type: ignore[import-not-found]
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "factur-x Library nicht verfügbar — bitte 'pip install factur-x' installieren"
        ) from e

    out_buf = BytesIO()
    generate_facturx_from_file(
        BytesIO(base_pdf),
        cii_xml.encode("utf-8"),
        "EN 16931",
        out_buf,
    )
    return out_buf.getvalue()


def _build_minimal_pdf(data: EInvoiceInput) -> bytes:
    """Erzeugt ein einfaches Begleit-PDF für ZUGFeRD-Hybrid (lesbarer Teil)."""
    try:
        from io import BytesIO

        from reportlab.lib.pagesizes import A4  # type: ignore[import-not-found]
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore[import-not-found]
        from reportlab.platypus import (  # type: ignore[import-not-found]
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
        from reportlab.lib import colors  # type: ignore[import-not-found]
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "reportlab Library nicht verfügbar — bitte 'pip install reportlab' installieren"
        ) from e

    styles = getSampleStyleSheet()
    buf = BytesIO()
    story: list = []
    story.append(Paragraph(f"<b>Rechnung {data.get('invoice_number', '')}</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Datum: {data.get('invoice_date', '')}", styles["Normal"]))
    story.append(Paragraph(f"Währung: {data.get('currency', 'EUR')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    supplier = data.get("supplier") or {}
    customer = data.get("customer") or {}
    story.append(Paragraph(f"<b>Lieferant:</b> {supplier.get('name', '')}", styles["Normal"]))
    story.append(Paragraph(f"{supplier.get('street', '')}, {supplier.get('postal_code', '')} {supplier.get('city', '')}", styles["Normal"]))
    if supplier.get("vat_id"):
        story.append(Paragraph(f"USt-ID: {supplier['vat_id']}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Kunde:</b> {customer.get('name', '')}", styles["Normal"]))
    story.append(Paragraph(f"{customer.get('street', '')}, {customer.get('postal_code', '')} {customer.get('city', '')}", styles["Normal"]))
    story.append(Spacer(1, 18))

    rows = [["Pos", "Artikel", "Menge", "Einzelpreis", "Netto"]]
    for idx, ln in enumerate(data.get("lines") or [], start=1):
        rows.append([
            str(idx),
            str(ln.get("article", "")),
            _quantity(ln.get("quantity", 0)),
            _money(ln.get("unit_price_net", 0)),
            _money(ln.get("line_net_amount", 0)),
        ])
    tbl = Table(rows, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    total_net = data.get("total_net", 0)
    total_vat = data.get("total_vat", 0)
    total_gross = data.get("total_gross", 0)
    story.append(Paragraph(f"<b>Netto:</b> {_money(total_net)} {data.get('currency', 'EUR')}", styles["Normal"]))
    story.append(Paragraph(f"<b>USt:</b> {_money(total_vat)} {data.get('currency', 'EUR')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Brutto:</b> {_money(total_gross)} {data.get('currency', 'EUR')}", styles["Normal"]))

    SimpleDocTemplate(buf, pagesize=A4).build(story)
    return buf.getvalue()


__all__ = [
    "EInvoiceInput",
    "InvoiceLineDict",
    "PartyAddress",
    "build_xrechnung_xml",
    "build_zugferd_cii_xml",
    "build_zugferd_pdf",
    "set_xrechnung_generator",
]
