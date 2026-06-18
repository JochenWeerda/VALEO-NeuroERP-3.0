"""INT-XRECHNUNG-001: XRechnung / ZUGFeRD E-Rechnung Export.

Erzeugt UBL 2.1 / XRechnung 3.0 konforme XML-Rechnungen für B2B-Pflicht
ab 2025 (§ 14 UStG). Unterstützt:
- GET /xrechnung/{invoice_id} → XML-Download
- GET /xrechnung/{invoice_id}/validate → Konformitätsprüfung
- GET /xrechnung/batch → Mehrere Rechnungen als ZIP
"""
from __future__ import annotations

import io
import zipfile
import hashlib
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/xrechnung", tags=["schnittstellen", "e-rechnung"])

# XRechnung / UBL 2.1 Namespaces
_NS = {
    "ubl": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def _build_xrechnung_xml(inv: dict, lines: list[dict]) -> str:
    """Baut XRechnung 3.0 / UBL 2.1 XML aus Rechnungsdaten."""
    root = ET.Element("{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice")
    root.set("xmlns:cac", _NS["cac"])
    root.set("xmlns:cbc", _NS["cbc"])

    def _cbc(parent: ET.Element, tag: str, text_: str, **attrs) -> ET.Element:
        el = ET.SubElement(parent, f"{{{_NS['cbc']}}}{tag}")
        el.text = text_
        for k, v in attrs.items():
            el.set(k, v)
        return el

    def _cac(parent: ET.Element, tag: str) -> ET.Element:
        return ET.SubElement(parent, f"{{{_NS['cac']}}}{tag}")

    _cbc(root, "CustomizationID",
         "urn:cen.eu:en16931:2017#compliant#urn:xoev-de:kosit:standard:xrechnung_3.0")
    _cbc(root, "ProfileID", "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0")
    _cbc(root, "ID", str(inv.get("invoice_number", "UNBEKANNT")))
    _cbc(root, "IssueDate", str(inv.get("invoice_date", date.today()))[:10])
    _cbc(root, "DueDate", str(inv.get("due_date", date.today()))[:10])
    _cbc(root, "InvoiceTypeCode", "380")  # 380 = Handelsrechnung
    _cbc(root, "DocumentCurrencyCode", str(inv.get("currency", "EUR")))
    _cbc(root, "BuyerReference", str(inv.get("buyer_reference", inv.get("customer_id", "LREF"))))

    # Lieferant (Seller)
    seller = _cac(root, "AccountingSupplierParty")
    seller_party = _cac(seller, "Party")
    seller_name = _cac(seller_party, "PartyName")
    _cbc(seller_name, "Name", str(inv.get("seller_name", "VALEO Landhandel GmbH")))
    seller_tax = _cac(seller_party, "PartyTaxScheme")
    _cbc(seller_tax, "CompanyID", str(inv.get("seller_vat_id", "DE000000000")))
    seller_tax_scheme = _cac(seller_tax, "TaxScheme")
    _cbc(seller_tax_scheme, "ID", "VAT")
    seller_legal = _cac(seller_party, "PartyLegalEntity")
    _cbc(seller_legal, "RegistrationName", str(inv.get("seller_name", "VALEO Landhandel GmbH")))

    # Käufer (Buyer)
    buyer = _cac(root, "AccountingCustomerParty")
    buyer_party = _cac(buyer, "Party")
    buyer_name = _cac(buyer_party, "PartyName")
    _cbc(buyer_name, "Name", str(inv.get("customer_name", inv.get("customer_id", "KUNDE"))))
    buyer_legal = _cac(buyer_party, "PartyLegalEntity")
    _cbc(buyer_legal, "RegistrationName", str(inv.get("customer_name", "KUNDE")))

    # Zahlungsbedingungen
    payment = _cac(root, "PaymentTerms")
    _cbc(payment, "Note", str(inv.get("payment_terms", "Zahlbar innerhalb 30 Tagen")))

    # Steuersummen
    tax_total = _cac(root, "TaxTotal")
    total_tax = float(inv.get("tax_amount", 0) or 0)
    _cbc(tax_total, "TaxAmount", f"{total_tax:.2f}", currencyID="EUR")
    subtotal = _cac(tax_total, "TaxSubtotal")
    taxable_amt = float(inv.get("net_amount", 0) or 0)
    _cbc(subtotal, "TaxableAmount", f"{taxable_amt:.2f}", currencyID="EUR")
    _cbc(subtotal, "TaxAmount", f"{total_tax:.2f}", currencyID="EUR")
    tax_cat = _cac(subtotal, "TaxCategory")
    _cbc(tax_cat, "ID", "S")
    tax_rate = 19.0 if total_tax > 0 and taxable_amt > 0 else 0.0
    _cbc(tax_cat, "Percent", f"{tax_rate:.1f}")
    tax_scheme2 = _cac(tax_cat, "TaxScheme")
    _cbc(tax_scheme2, "ID", "VAT")

    # Gesamtbeträge
    legal_mon = _cac(root, "LegalMonetaryTotal")
    _cbc(legal_mon, "LineExtensionAmount", f"{taxable_amt:.2f}", currencyID="EUR")
    _cbc(legal_mon, "TaxExclusiveAmount", f"{taxable_amt:.2f}", currencyID="EUR")
    gross = float(inv.get("total_amount", taxable_amt + total_tax))
    _cbc(legal_mon, "TaxInclusiveAmount", f"{gross:.2f}", currencyID="EUR")
    _cbc(legal_mon, "PayableAmount", f"{gross:.2f}", currencyID="EUR")

    # Positionen
    for i, line in enumerate(lines, start=1):
        inv_line = _cac(root, "InvoiceLine")
        _cbc(inv_line, "ID", str(i))
        qty = float(line.get("quantity", 1))
        _cbc(inv_line, "InvoicedQuantity", f"{qty:.3f}",
             unitCode=str(line.get("unit", "TNE")))
        line_ext = float(line.get("line_total", 0) or line.get("net_total", 0))
        _cbc(inv_line, "LineExtensionAmount", f"{line_ext:.2f}", currencyID="EUR")
        line_item = _cac(inv_line, "Item")
        _cbc(line_item, "Name", str(line.get("description", line.get("article_name", "Position"))))
        line_price = _cac(inv_line, "Price")
        unit_price = float(line.get("unit_price", 0) or line.get("price_per_unit", 0))
        _cbc(line_price, "PriceAmount", f"{unit_price:.4f}", currencyID="EUR")

    ET.indent(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


def _load_invoice(db: Session, invoice_id: str, tenant_id: str) -> tuple[dict, list[dict]]:
    """Lädt Rechnungskopf + Positionen aus der DB."""
    inv_row = db.execute(text("""
        SELECT si.id, si.invoice_number, si.invoice_date, si.due_date,
               si.customer_id, si.net_amount, si.tax_amount, si.total_amount,
               si.currency, bp.name AS customer_name
          FROM domain_erp.sales_invoices si
          LEFT JOIN domain_erp.business_partners bp ON bp.id = si.customer_id
         WHERE si.id = :id AND si.tenant_id = :tid
    """), {"id": invoice_id, "tid": tenant_id}).fetchone()

    if not inv_row:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    inv = {
        "invoice_number": inv_row[1],
        "invoice_date": inv_row[2],
        "due_date": inv_row[3],
        "customer_id": inv_row[4],
        "net_amount": inv_row[5],
        "tax_amount": inv_row[6],
        "total_amount": inv_row[7],
        "currency": inv_row[8] or "EUR",
        "customer_name": inv_row[9],
        "seller_name": "VALEO Landhandel GmbH",
        "seller_vat_id": "DE000000000",
        "payment_terms": "Zahlbar innerhalb 30 Tagen netto",
    }

    line_rows = db.execute(text("""
        SELECT article_id, description, quantity, unit, unit_price,
               quantity * unit_price AS line_total
          FROM domain_erp.sales_invoice_lines
         WHERE invoice_id = :id
         ORDER BY position
    """), {"id": invoice_id}).fetchall()

    lines = [
        {
            "article_name": str(r[1] or r[0]),
            "description": str(r[1] or r[0]),
            "quantity": float(r[2] or 1),
            "unit": str(r[3] or "TNE"),
            "unit_price": float(r[4] or 0),
            "line_total": float(r[5] or 0),
        }
        for r in line_rows
    ] or [{"description": "Siehe Rechnung", "quantity": 1, "unit": "C62",
            "unit_price": float(inv["net_amount"] or 0), "line_total": float(inv["net_amount"] or 0)}]

    return inv, lines


@router.get("/{invoice_id}", summary="XRechnung XML exportieren (INT-XRECHNUNG-001)")
def export_xrechnung(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    """Exportiert eine Rechnung als XRechnung 3.0 / UBL 2.1 XML."""
    inv, lines = _load_invoice(db, invoice_id, tenant_id)
    xml = _build_xrechnung_xml(inv, lines)
    filename = f"XRechnung_{inv['invoice_number']}.xml"
    return Response(
        content=xml.encode("utf-8"),
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{invoice_id}/validate", summary="XRechnung Pflichtfelder prüfen")
def validate_xrechnung(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Prüft ob Pflichtfelder für XRechnung vorhanden sind (kein vollständiger Schematron-Check)."""
    inv, lines = _load_invoice(db, invoice_id, tenant_id)
    errors: list[str] = []
    if not inv.get("invoice_number"):
        errors.append("Rechnungsnummer fehlt (BT-1)")
    if not inv.get("invoice_date"):
        errors.append("Rechnungsdatum fehlt (BT-2)")
    if not inv.get("customer_id"):
        errors.append("Käufer fehlt (BT-44)")
    if not inv.get("seller_vat_id") or inv["seller_vat_id"] == "DE000000000":
        errors.append("Lieferanten-UST-ID fehlt oder Platzhalter (BT-31)")
    if not inv.get("net_amount"):
        errors.append("Nettobetrag fehlt (BT-109)")
    if not lines:
        errors.append("Keine Rechnungspositionen (mindestens 1 erforderlich)")
    xml = _build_xrechnung_xml(inv, lines)
    sha256 = hashlib.sha256(xml.encode()).hexdigest()
    return {
        "invoice_id": invoice_id,
        "invoice_number": inv.get("invoice_number"),
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": ["seller_vat_id ist Platzhalter"] if inv.get("seller_vat_id") == "DE000000000" else [],
        "xml_sha256": sha256,
        "standard": "XRechnung 3.0 / UBL 2.1 / EN 16931",
    }


@router.get("/batch/export", summary="Mehrere XRechnungen als ZIP exportieren")
def export_xrechnung_batch(
    periode: str = Query(..., description="Periode YYYY-MM"),
    status: str = Query("VERBUCHT", description="Rechnungsstatus"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    """Exportiert alle Rechnungen einer Periode als XRechnung-ZIP."""
    try:
        rows = db.execute(text("""
            SELECT id FROM domain_erp.sales_invoices
             WHERE tenant_id = :tid
               AND status = :status
               AND TO_CHAR(invoice_date, 'YYYY-MM') = :periode
             ORDER BY invoice_date, invoice_number
             LIMIT 500
        """), {"tid": tenant_id, "status": status, "periode": periode}).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for (inv_id,) in rows:
            try:
                inv, lines = _load_invoice(db, str(inv_id), tenant_id)
                xml = _build_xrechnung_xml(inv, lines)
                filename = f"XRechnung_{inv['invoice_number']}.xml"
                zf.writestr(filename, xml.encode("utf-8"))
            except Exception:
                continue

    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="XRechnungen_{periode}.zip"'},
    )
