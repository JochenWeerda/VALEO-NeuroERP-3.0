"""Self-Billing in DocFlow (BELEG-052): purchase_invoice ist führender Beleg.

``domain_finance.self_billing_invoices`` bleibt Agrar-Erweiterung (Steuerkontext, E-Rechnung,
Dispute) und verweist auf den DocFlow-Kopf — keine dauerhafte Doppelbelegführung.

Wichtig: Die Anlage hier darf die Aufrufer-Transaktion nicht committen (Erntefreigabe
läuft in ``begin_nested``). Deshalb kein ``DocflowService.create_document`` /
``create_snapshot`` (die committen), sondern ``_apply_create`` + ``flush``.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal
from hashlib import sha256
from typing import Optional, Union

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.belegvertrag import BELEGARTEN
from app.core.exceptions import ConflictError, ValidationFailedError
from app.services.beleg_anlage import Position, _belegtag

QUELLE = "self_billing"
ART = "purchase_invoice"


def lege_self_billing_beleg_an(
    db: Session,
    tenant_id: str,
    *,
    supplier_id: str,
    invoice_number: str,
    tax_code: str,
    net_amount: Decimal,
    description: str,
    harvest_acceptance_id: Optional[str],
    akteur: str,
    document_date: Optional[Union[date, datetime]] = None,
) -> str:
    """Legt DocFlow-``purchase_invoice``-Entwurf an; ohne Session-Commit.

    ``document_date`` steuert historische Steuerschlüssel (Lieferdatum); Default: Geschäftstag.
    """
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_create_command import _apply_create
    from app.services.docflow_service import DocflowService

    if harvest_acceptance_id:
        existing = db.execute(
            text(
                "SELECT id FROM domain_docflow.document_headers "
                "WHERE tenant_id = :t AND doc_type = :a AND source_system = :q "
                "AND source_ref = :r AND deleted_at IS NULL LIMIT 1"
            ),
            {"t": tenant_id, "a": ART, "q": QUELLE, "r": f"HA:{harvest_acceptance_id}"},
        ).scalar()
        if existing:
            raise ConflictError("DocFlow-Self-Billing-Beleg für diese Annahme existiert bereits.")
        referenz = f"HA:{harvest_acceptance_id}"
    else:
        referenz = invoice_number

    netto = Decimal(str(net_amount)).quantize(Decimal("0.01"))
    if netto <= 0:
        raise ValidationFailedError("Self-Billing-Netto muss positiv sein.")

    idempotenz = f"self_billing:{tenant_id}:{referenz}"
    variante = BELEGARTEN[ART]
    anhang = sha256(idempotenz.encode()).hexdigest()[:6]
    entwurf = f"{invoice_number}"[:72] + f"-{anhang}"
    partner = (
        {"supplier_id": supplier_id}
        if variante.partnerrolle == "lieferant"
        else {"customer_id": supplier_id}
    )
    position = Position(
        artikel_nr="SELF-BILLING",
        bezeichnung=(description or f"Self-Billing {invoice_number}")[:500],
        menge=1.0,
        einzelpreis=float(netto),
        steuerschluessel=tax_code,
    )
    if document_date is None:
        belegdatum = _belegtag()
    elif isinstance(document_date, datetime):
        belegdatum = document_date
    else:
        belegdatum = datetime.combine(document_date, time(), tzinfo=timezone.utc)
    anfrage = DocflowCreateRequest(
        doc_type=ART,
        doc_number=entwurf,
        status="draft",
        source_system=QUELLE[:40],
        source_ref=referenz[:80],
        currency="EUR",
        document_date=belegdatum,
        idempotency_key=None,  # Aufrufer (Ernte-_run) besitzt Idempotenz; kein create_snapshot-Commit
        **partner,
        items=[
            DocflowLineInput(
                article_number=position.artikel_nr,
                description=position.bezeichnung,
                quantity=position.menge,
                unit=position.einheit,
                unit_price=position.einzelpreis if variante.mit_preisen else 0,
                tax_code=position.steuerschluessel,
            )
        ],
    )
    service = DocflowService(db, tenant_id, akteur or "self_billing")
    doc_id = _apply_create(service, anfrage, None)
    db.flush()
    return str(doc_id)


def verknuepfe_erweiterung(
    db: Session,
    tenant_id: str,
    *,
    self_billing_invoice_id: str,
    docflow_header_id: str,
) -> None:
    """Schreibt DocFlow-Kopf-ID an die Agrar-Erweiterung."""
    updated = db.execute(
        text(
            "UPDATE domain_finance.self_billing_invoices "
            "SET docflow_header_id = :d, updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :t AND docflow_header_id IS NULL"
        ),
        {"d": docflow_header_id, "id": self_billing_invoice_id, "t": tenant_id},
    )
    if updated.rowcount == 0:
        # bereits verknüpft oder fehlende Zeile — bei Idempotenz ok wenn gleiche ID
        current = db.execute(
            text(
                "SELECT docflow_header_id FROM domain_finance.self_billing_invoices "
                "WHERE id = :id AND tenant_id = :t"
            ),
            {"id": self_billing_invoice_id, "t": tenant_id},
        ).scalar()
        if current != docflow_header_id:
            raise ConflictError(
                "Self-Billing-Erweiterung ist bereits mit einem anderen DocFlow-Beleg verknüpft."
            )


def assert_fuehrender_beleg_ist_docflow(
    db: Session, tenant_id: str, self_billing_invoice_id: str
) -> None:
    """Ratsche: gebuchte Self-Billing-Erweiterung braucht DocFlow-Kopf."""
    row = db.execute(
        text(
            "SELECT docflow_header_id, journal_entry_id FROM domain_finance.self_billing_invoices "
            "WHERE id = :id AND tenant_id = :t"
        ),
        {"id": self_billing_invoice_id, "t": tenant_id},
    ).mappings().first()
    if not row:
        raise ValidationFailedError("Self-Billing-Erweiterung nicht gefunden.")
    if row["journal_entry_id"] and not row["docflow_header_id"]:
        raise ValidationFailedError(
            "Gebuchte Self-Billing ohne DocFlow-Führungsbeleg — Doppelbelegführung verboten."
        )
