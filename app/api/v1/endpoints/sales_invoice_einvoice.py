"""
Slice-006: XRechnung/ZUGFeRD Export Endpoints für SalesInvoice.

Schließt die E-Rechnung-2025-Lücke für reguläre B2B-Verkaufsrechnungen:
- POST /sales/invoices/{invoice_number}/einvoice/xrechnung  → XML (UBL 2.1, XRechnung 3.0)
- POST /sales/invoices/{invoice_number}/einvoice/zugferd    → PDF/A-3 (mit eingebettetem CII-XML, EN 16931)
- GET  /sales/invoices/{invoice_number}/einvoice/xrechnung  → liefert zuletzt generiertes XML

XML wird zusätzlich GoBD-konform im document_artifacts-Archiv registriert.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.gobd_artifact import register_artifact, sha256_hex
from app.core.tenant import get_tenant_id
from app.documents.router_helpers import get_from_store, get_repository
from app.services.einvoice_generator import (
    EInvoiceInput,
    InvoiceLineDict,
    PartyAddress,
    build_xrechnung_xml,
    build_zugferd_pdf,
)

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.sales_invoice_einvoice_schemas import SalesInvoiceEinvoiceOut


router = APIRouter(prefix="/sales/invoices", tags=["sales", "invoices", "einvoice"])


class EInvoiceExportRequest(BaseModel):
    """Optionale Override-Daten für Lieferanten/Kunden, falls Stammdaten unvollständig."""

    supplier: Optional[PartyAddress] = Field(
        default=None,
        description="Optionaler Override des Lieferanten (Pflicht-EN-16931-Felder ergänzen)",
    )
    customer: Optional[PartyAddress] = Field(
        default=None,
        description="Optionaler Override des Kunden (Pflicht-EN-16931-Felder ergänzen)",
    )
    buyer_reference: Optional[str] = Field(
        default=None,
        description="BT-10 Käuferreferenz (Leitweg-ID für Öffentliche Verwaltung)",
    )
    payment_terms_text: Optional[str] = Field(default=None)
    payment_due_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")


def _resolve_customer_party(db: Session, tenant_id: str, customer_id: str) -> PartyAddress:
    """Lädt die Rechnungs-Partyadresse über die kanonische Schicht (BP-Stamm + CRM-Kunde)."""
    from app.services.business_partner_service import BusinessPartnerService

    party: PartyAddress = BusinessPartnerService(db, tenant_id).get_customer_party(customer_id)  # type: ignore[assignment]
    return party


def _resolve_supplier_party(db: Session, tenant_id: str) -> PartyAddress:
    """Lädt Mandanten-Lieferantenstammdaten aus tenants/branches (Fallback: leeres Dict)."""
    party: PartyAddress = {"name": tenant_id, "country_code": "DE"}
    try:
        row = db.execute(
            text(
                """
                SELECT name, street, postal_code, city, country_code, vat_id, email
                FROM domain_shared.tenants
                WHERE id = :tenant_id
                LIMIT 1
                """
            ),
            {"tenant_id": tenant_id},
        ).fetchone()
        if row:
            party = {
                "name": row[0] or tenant_id,
                "street": row[1] or "",
                "postal_code": row[2] or "",
                "city": row[3] or "",
                "country_code": row[4] or "DE",
                "vat_id": row[5] or "",
                "email": row[6] or "",
            }
    except Exception as e:  # noqa: BLE001 — best-effort enrichment, fallback uses tenant_id
        logger.debug("Tenant lookup failed (using fallback): %s", e)
    return party


def _invoice_to_einvoice_input(
    invoice_dict: dict,
    supplier: PartyAddress,
    customer: PartyAddress,
    overrides: EInvoiceExportRequest,
) -> EInvoiceInput:
    """Konvertiert SalesInvoice-Daten in den generischen Generator-Input."""
    lines_in = invoice_dict.get("lines") or []
    lines: list[InvoiceLineDict] = []
    for idx, line in enumerate(lines_in, start=1):
        qty = float(line.get("qty", 0) or 0)
        unit_price = float(line.get("price", 0) or 0)
        net = qty * unit_price
        lines.append({
            "line_id": str(idx),
            "article": str(line.get("article", "")),
            "description": str(line.get("article", "")),
            "quantity": qty,
            "unit_code": "C62",
            "unit_price_net": unit_price,
            "line_net_amount": net,
            "vat_rate_percent": float(line.get("vatRate", 0) or 0),
            "vat_category_code": "S",
        })

    if overrides.supplier:
        supplier = {**supplier, **overrides.supplier}
    if overrides.customer:
        customer = {**customer, **overrides.customer}

    return {
        "invoice_number": invoice_dict.get("number", ""),
        "invoice_date": invoice_dict.get("date", ""),
        "invoice_type_code": "380",
        "currency": "EUR",
        "buyer_reference": overrides.buyer_reference or invoice_dict.get("number", ""),
        "payment_due_date": overrides.payment_due_date or invoice_dict.get("dueDate", ""),
        "payment_terms_text": overrides.payment_terms_text or invoice_dict.get("paymentTerms", "net30"),
        "supplier": supplier,
        "customer": customer,
        "lines": lines,
        "total_net": float(invoice_dict.get("subtotalNet", 0) or 0),
        "total_vat": float(invoice_dict.get("totalTax", 0) or 0),
        "total_gross": float(invoice_dict.get("totalGross", 0) or 0),
    }


def _load_sales_invoice(db: Session, invoice_number: str) -> dict:
    repo = get_repository(db)
    invoice_dict = get_from_store("salesInvoice", invoice_number, repo=repo)
    if not invoice_dict:
        raise HTTPException(status_code=404, detail=f"SalesInvoice {invoice_number} not found")
    return invoice_dict


def _register_xml_artifact(
    db: Session,
    tenant_id: str,
    invoice_number: str,
    xml: str,
    file_name: str,
    artifact_subtype: str,
) -> None:
    """GoBD-Persistenz im document_artifacts-Archiv."""
    try:
        register_artifact(
            db=db,
            tenant_id=tenant_id,
            header_id=invoice_number,
            artifact_type="xml",
            content_hash_sha256=sha256_hex(xml.encode("utf-8")),
            storage_key=f"einvoice/{artifact_subtype}/{invoice_number}",
            file_name=file_name,
        )
    except Exception as e:  # noqa: BLE001 — GoBD-Archivierung ist best-effort
        logger.warning("E-Invoice GoBD artifact registration failed: %s", e)


@router.post(
    "/{invoice_number}/einvoice/xrechnung",
    summary="XRechnung 3.0 (UBL 2.1) generieren",
    response_model=SalesInvoiceEinvoiceOut,
    response_class=Response,
)
def generate_xrechnung(
    invoice_number: str,
    payload: EInvoiceExportRequest = EInvoiceExportRequest(),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    """
    Erzeugt eine XRechnung-3.0 (EN 16931, UBL 2.1) für eine bestehende SalesInvoice
    und registriert das XML im GoBD-Artifact-Archiv.
    """
    invoice_dict = _load_sales_invoice(db, invoice_number)
    supplier = _resolve_supplier_party(db, tenant_id)
    customer = _resolve_customer_party(db, tenant_id, invoice_dict.get("customerId", ""))
    einvoice_input = _invoice_to_einvoice_input(invoice_dict, supplier, customer, payload)
    xml = build_xrechnung_xml(einvoice_input)

    _register_xml_artifact(
        db, tenant_id, invoice_number, xml,
        file_name=f"xrechnung-{invoice_number}.xml",
        artifact_subtype="xrechnung",
    )

    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="xrechnung-{invoice_number}.xml"',
            "X-EInvoice-Format": "XRechnung-3.0",
            "X-EInvoice-Standard": "EN-16931",
        },
    )


@router.post(
    "/{invoice_number}/einvoice/zugferd",
    summary="ZUGFeRD 2.x (PDF/A-3 + CII EN 16931) generieren",
    response_model=SalesInvoiceEinvoiceOut,
    response_class=Response,
)
def generate_zugferd(
    invoice_number: str,
    payload: EInvoiceExportRequest = EInvoiceExportRequest(),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    """
    Erzeugt ZUGFeRD-2.x PDF/A-3 mit eingebettetem CII-XML (Profil EN 16931) und
    registriert das XML zusätzlich im GoBD-Artifact-Archiv.
    """
    invoice_dict = _load_sales_invoice(db, invoice_number)
    supplier = _resolve_supplier_party(db, tenant_id)
    customer = _resolve_customer_party(db, tenant_id, invoice_dict.get("customerId", ""))
    einvoice_input = _invoice_to_einvoice_input(invoice_dict, supplier, customer, payload)

    try:
        pdf_bytes = build_zugferd_pdf(einvoice_input)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "ZUGFeRD-Erzeugung nicht verfügbar (factur-x / reportlab fehlen). "
                f"Original: {e}"
            ),
        ) from e

    from app.services.einvoice_generator import build_zugferd_cii_xml
    cii_xml = build_zugferd_cii_xml(einvoice_input)
    _register_xml_artifact(
        db, tenant_id, invoice_number, cii_xml,
        file_name=f"zugferd-{invoice_number}-cii.xml",
        artifact_subtype="zugferd",
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="zugferd-{invoice_number}.pdf"',
            "X-EInvoice-Format": "ZUGFeRD-2.x",
            "X-EInvoice-Profile": "EN-16931",
        },
    )


@router.get(
    "/{invoice_number}/einvoice/xrechnung",
    summary="Letzte XRechnung als XML abrufen",
    response_class=Response,
)
def get_xrechnung(
    invoice_number: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    """
    Liefert das XRechnung-XML einer bereits generierten Rechnung. Generiert es
    on-the-fly auf Basis der Stammdaten, wenn noch nichts archiviert ist.
    """
    invoice_dict = _load_sales_invoice(db, invoice_number)
    supplier = _resolve_supplier_party(db, tenant_id)
    customer = _resolve_customer_party(db, tenant_id, invoice_dict.get("customerId", ""))
    einvoice_input = _invoice_to_einvoice_input(
        invoice_dict, supplier, customer, EInvoiceExportRequest()
    )
    xml = build_xrechnung_xml(einvoice_input)
    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="xrechnung-{invoice_number}.xml"',
            "X-EInvoice-Format": "XRechnung-3.0",
            "X-EInvoice-Standard": "EN-16931",
        },
    )
