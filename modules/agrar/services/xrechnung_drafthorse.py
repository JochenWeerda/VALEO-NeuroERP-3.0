"""
XRechnung/ZUGFeRD-Generator mit drafthorse (Open Source, Apache 2.0).

Mappt Self-Billing-Daten auf das ZUGFeRD-Datenmodell und liefert
EN16931-konformes XML. Bei installiertem drafthorse wird dieser Generator
automatisch in generate_einvoice_xrechnung verwendet.

Installation: pip install drafthorse
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from modules.agrar.services.self_billing_service import SelfBillingInvoice

logger = logging.getLogger(__name__)

_drafthorse_available = False
try:
    from drafthorse.models.accounting import ApplicableTradeTax
    from drafthorse.models.document import Document
    from drafthorse.models.party import TaxRegistration
    from drafthorse.models.tradelines import LineItem
    _drafthorse_available = True
except ImportError:
    pass


def is_available() -> bool:
    """True, wenn drafthorse installiert ist."""
    return _drafthorse_available


def build_xrechnung_xml(
    invoice: "SelfBillingInvoice",
    supplier_data: Dict[str, Any],
    customer_data: Dict[str, Any],
    line_items: List[Dict[str, Any]],
) -> str:
    """
    Erzeugt ZUGFeRD/XRechnung-XML (EN16931) aus Self-Billing-Daten.

    Signatur kompatibel zu set_xrechnung_generator; wird von
    generate_einvoice_xrechnung aufgerufen, wenn dieser Generator registriert ist.

    Raises:
        ImportError: wenn drafthorse nicht installiert
        Exception: bei Validierungsfehlern des Schemas
    """
    if not _drafthorse_available:
        raise ImportError("drafthorse is not installed. Install with: pip install drafthorse")

    doc = Document()
    doc.context.guideline_parameter.id = (
        "urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended"
    )
    doc.header.id = invoice.invoice_number
    doc.header.type_code = "380"  # Rechnung; 381 = Gutschrift
    doc.header.name = "RECHNUNG"
    doc.header.issue_date_time = invoice.created_at.date() if invoice.created_at else date.today()
    if hasattr(doc.header, "languages"):
        doc.header.languages.add("de")
    else:
        doc.header.language = "de"

    # Lieferant
    doc.trade.agreement.seller.name = (supplier_data.get("name") or "").strip() or "Lieferant"
    doc.trade.settlement.payee.name = doc.trade.agreement.seller.name
    doc.trade.agreement.seller.address.country_id = (supplier_data.get("country_code") or "DE").strip()[:2]
    doc.trade.agreement.seller.address.line_one = (supplier_data.get("street") or "").strip()
    doc.trade.agreement.seller.address.city_name = (supplier_data.get("city") or "").strip()
    doc.trade.agreement.seller.address.postcode = (supplier_data.get("postal_code") or "").strip()
    vat_supplier = (supplier_data.get("vat_id") or "").strip()
    if vat_supplier:
        cc = vat_supplier[:2].upper() if len(vat_supplier) >= 2 else "DE"
        doc.trade.agreement.seller.tax_registrations.add(
            TaxRegistration(id=("VA", vat_supplier.replace(" ", "")))
        )

    # Kunde
    doc.trade.agreement.buyer.name = (customer_data.get("name") or "").strip() or "Kunde"
    doc.trade.settlement.invoicee.name = doc.trade.agreement.buyer.name
    doc.trade.agreement.buyer.address.country_id = (customer_data.get("country_code") or "DE").strip()[:2]
    doc.trade.agreement.buyer.address.line_one = (customer_data.get("street") or "").strip()
    doc.trade.agreement.buyer.address.city_name = (customer_data.get("city") or "").strip()
    doc.trade.agreement.buyer.address.postcode = (customer_data.get("postal_code") or "").strip()

    doc.trade.settlement.currency_code = "EUR"
    doc.trade.settlement.payment_means.type_code = "30"  # SEPA/Überweisung; 48 = Bank

    now_dt = datetime.now(timezone.utc)
    doc.trade.agreement.seller_order.issue_date_time = now_dt
    doc.trade.agreement.buyer_order.issue_date_time = now_dt
    doc.trade.agreement.customer_order.issue_date_time = now_dt

    net = Decimal(str(invoice.total_net_amount_eur))
    tax = Decimal(str(invoice.total_vat_amount_eur))
    gross = Decimal(str(invoice.total_gross_amount_eur))
    vat_rate = Decimal(str(invoice.vat_rate_percent))

    if line_items:
        for idx, row in enumerate(line_items, start=1):
            li = LineItem()
            li.document.line_id = str(idx)
            li.product.name = (row.get("description") or row.get("name") or f"Position {idx}")[:200]
            amount_net = _decimal(row, "net_amount", "amount", "price", default=Decimal("0"))
            qty = _decimal(row, "quantity", "qty", default=Decimal("1"))
            unit = (row.get("unit") or row.get("unit_code") or "C62")[:3]  # C62 = Stück
            li.agreement.gross.amount = amount_net * (1 + vat_rate / 100) if vat_rate else amount_net
            li.agreement.gross.basis_quantity = (qty, unit)
            li.agreement.net.amount = amount_net
            li.agreement.net.basis_quantity = (amount_net, "EUR")
            li.delivery.billed_quantity = (qty, unit)
            li.settlement.trade_tax.type_code = "VAT"
            li.settlement.trade_tax.category_code = "S"  # Standard
            li.settlement.trade_tax.rate_applicable_percent = vat_rate
            li.settlement.monetary_summation.total_amount = amount_net
            doc.trade.items.add(li)
    else:
        # Eine Sammelposition
        li = LineItem()
        li.document.line_id = "1"
        li.product.name = "Self-Billing Gutschrift"
        li.agreement.gross.amount = gross
        li.agreement.gross.basis_quantity = (Decimal("1.0000"), "C62")
        li.agreement.net.amount = net
        li.agreement.net.basis_quantity = (net, "EUR")
        li.delivery.billed_quantity = (Decimal("1.0000"), "C62")
        li.settlement.trade_tax.type_code = "VAT"
        li.settlement.trade_tax.category_code = "S"
        li.settlement.trade_tax.rate_applicable_percent = vat_rate
        li.settlement.monetary_summation.total_amount = net
        doc.trade.items.add(li)

    trade_tax = ApplicableTradeTax()
    trade_tax.calculated_amount = tax
    trade_tax.basis_amount = net
    trade_tax.type_code = "VAT"
    trade_tax.category_code = "S"
    trade_tax.rate_applicable_percent = vat_rate
    doc.trade.settlement.trade_tax.add(trade_tax)

    doc.trade.settlement.monetary_summation.line_total = net
    doc.trade.settlement.monetary_summation.charge_total = Decimal("0.00")
    doc.trade.settlement.monetary_summation.allowance_total = Decimal("0.00")
    doc.trade.settlement.monetary_summation.tax_basis_total = net
    doc.trade.settlement.monetary_summation.tax_total = tax
    doc.trade.settlement.monetary_summation.grand_total = gross
    doc.trade.settlement.monetary_summation.due_amount = gross

    xml = doc.serialize(schema="FACTUR-X_EXTENDED")
    return xml.decode("utf-8") if isinstance(xml, bytes) else xml


def _decimal(row: Dict[str, Any], *keys: str, default: Optional[Decimal] = None) -> Decimal:
    for k in keys:
        v = row.get(k)
        if v is not None:
            try:
                return Decimal(str(v))
            except Exception:
                pass
    return default if default is not None else Decimal("0")


def register_as_xrechnung_generator() -> bool:
    """
    Registriert build_xrechnung_xml als XRechnung-Generator.
    Aufruf z. B. beim App-Start (wenn drafthorse installiert ist).
    Returns: True wenn registriert, False wenn drafthorse fehlt.
    """
    if not _drafthorse_available:
        logger.info("drafthorse not installed; XRechnung uses built-in UBL fallback")
        return False
    from modules.agrar.services.self_billing_service import set_xrechnung_generator
    set_xrechnung_generator(build_xrechnung_xml)
    logger.info("XRechnung generator registered (drafthorse ZUGFeRD)")
    return True
