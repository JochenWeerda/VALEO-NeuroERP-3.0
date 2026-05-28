"""
Finance Invoices API Endpoints
Spezifische Endpoints für Finance-Modul Invoices
"""

from datetime import datetime, timedelta
from decimal import Decimal
import logging
from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.customer_sales_eligibility import assert_customer_allowed_for_invoice
from app.services.sales_posting_service import SalesPostingService
from app.services.finance_transaction_service import FinanceTransactionService
from app.core.fibu_audit import log_fibu_audit
from app.core.gobd_artifact import register_artifact, sha256_hex
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.documents.models import SalesInvoice
from app.documents.router_helpers import (
    delete_from_store,
    get_from_store,
    get_repository,
    list_from_store,
    save_to_store,
)
from app.finance.tax_resolver import resolve_partner_country, resolve_tax_key_accounts

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/finance/invoices", tags=["finance", "invoices"])


def _resolve_open_items_table(db: Session) -> str:
    """Resolve offene_posten table name for mixed deployments."""
    for candidate in ("domain_erp.offene_posten", "offene_posten"):
        if db.execute(text("SELECT to_regclass(:name)"), {"name": candidate}).scalar():
            return candidate
    raise RuntimeError("offene_posten table not found")


def _ensure_account(
    db: Session,
    tenant_id: str,
    account_number: str,
    account_name: str,
    account_type: str,
    category: str,
) -> str:
    """Return chart_of_accounts.id for account_number, create minimal account if missing."""
    row = db.execute(
        text(
            """
            SELECT id
            FROM domain_erp.chart_of_accounts
            WHERE tenant_id = :tenant_id AND account_number = :account_number
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "account_number": account_number},
    ).fetchone()
    if row:
        return str(row[0])

    account_id = uuid7()
    db.execute(
        text(
            """
            INSERT INTO domain_erp.chart_of_accounts
            (id, tenant_id, account_number, account_name, account_type, category, is_active, created_at, updated_at)
            VALUES (:id, :tenant_id, :account_number, :account_name, :account_type, :category, TRUE, NOW(), NOW())
            """
        ),
        {
            "id": account_id,
            "tenant_id": tenant_id,
            "account_number": account_number,
            "account_name": account_name,
            "account_type": account_type,
            "category": category,
        },
    )
    return account_id


def _resolve_customer_name(db: Session, customer_id: str) -> str:
    customer_name = customer_id
    try:
        row = db.execute(
            text(
                """
                SELECT name
                FROM domain_shared.business_partners
                WHERE partner_id = :partner_id
                LIMIT 1
                """
            ),
            {"partner_id": customer_id},
        ).fetchone()
        if row and row[0]:
            customer_name = str(row[0])
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass
    return customer_name


async def _create_gl_booking_and_op(db: Session, invoice: SalesInvoice, tenant_id: str) -> None:
    """FIBU-AR-02: Erzeugt GL-Buchung + offenen Posten für Debitoren."""
    period = invoice.date[:7]

    period_status = db.execute(
        text(
            """
            SELECT status
            FROM finance_accounting_periods
            WHERE tenant_id = :tenant_id AND period = :period
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "period": period},
    ).fetchone()
    if period_status and str(period_status[0]) != "OPEN":
        raise HTTPException(
            status_code=403,
            detail=f"Period {period} is {period_status[0]}. Posting is blocked.",
        )

    customer_name = _resolve_customer_name(db, invoice.customerId)

    total_net = Decimal(str(invoice.subtotalNet or 0)).quantize(Decimal("0.01"))
    total_tax = Decimal(str(invoice.totalTax or 0)).quantize(Decimal("0.01"))
    total_gross = Decimal(str(invoice.totalGross or 0)).quantize(Decimal("0.01"))

    if total_net == Decimal("0.00"):
        total_net = sum(
            (Decimal(str(line.qty or 0)) * Decimal(str(line.price or 0)) for line in invoice.lines),
            Decimal("0.00"),
        ).quantize(Decimal("0.01"))

    if total_tax == Decimal("0.00") and invoice.lines:
        total_tax = sum(
            (
                (Decimal(str(line.qty or 0)) * Decimal(str(line.price or 0)))
                * Decimal(str(line.vatRate or 0))
                / Decimal("100")
                for line in invoice.lines
            ),
            Decimal("0.00"),
        ).quantize(Decimal("0.01"))

    if total_gross == Decimal("0.00"):
        total_gross = (total_net + total_tax).quantize(Decimal("0.01"))

    existing_je = db.execute(
        text(
            """
            SELECT id
            FROM domain_erp.journal_entries
            WHERE tenant_id = :tenant_id
              AND source = 'sales_invoice'
              AND (document_number = :invoice_number OR reference = :invoice_number)
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "invoice_number": invoice.number},
    ).fetchone()

    if not existing_je:
        # Resolve dynamic tax account (country-specific, reverse-charge aware)
        tax_account_no = "1776"
        reverse_charge = False
        if total_tax > Decimal("0.00") and invoice.lines:
            max_rate = max(
                Decimal(str(line.vatRate or 0)).quantize(Decimal("0.01"))
                for line in invoice.lines
            )
            invoice_country = getattr(invoice, "country", None) or resolve_partner_country(db, invoice.customerId, "DE")
            tax_key_cfg = resolve_tax_key_accounts(db, tenant_id, max_rate, invoice_country)
            tax_account_no = tax_key_cfg.get("credit_account") or "1776"
            reverse_charge = bool(tax_key_cfg.get("reverse_charge"))
            _ensure_account(db, tenant_id, tax_account_no, "Umsatzsteuer", "liability", "tax")

        _ensure_account(db, tenant_id, "1200", "Forderungen aus Lieferungen und Leistungen", "asset", "receivables")
        _ensure_account(db, tenant_id, "8400", "Umsatzerlöse", "revenue", "sales")

        lines: list[dict] = [
            {"account_id": "1200", "debit_amount": float(total_gross), "credit_amount": 0,
             "description": f"Forderung {invoice.customerId}"},
            {"account_id": "8400", "debit_amount": 0, "credit_amount": float(total_net),
             "description": "Umsatzerlöse"},
        ]
        if total_tax > Decimal("0.00"):
            lines.append({"account_id": tax_account_no, "debit_amount": 0, "credit_amount": float(total_tax),
                          "description": "Umsatzsteuer (Reverse-Charge)" if reverse_charge else "Umsatzsteuer"})

        fin = FinanceTransactionService(db, tenant_id)
        je = fin.create(
            entry_number=f"AR-{invoice.number}",
            description=f"Ausgangsrechnung {invoice.number}",
            entry_date=invoice.date,
            lines=lines,
            reference=invoice.number,
            source="sales_invoice",
            document_type="AR_INVOICE",
            period=period,
        )
        je_id = str(je.id)
        log_fibu_audit(
            db,
            tenant_id,
            "create",
            "journal_entry",
            je_id,
            {"source": "sales_invoice", "invoice_number": invoice.number, "period": period},
        )

    op_table = _resolve_open_items_table(db)
    existing_op = db.execute(
        text(
            f"""
            SELECT id
            FROM {op_table}
            WHERE tenant_id = :tenant_id AND rechnungsnr = :rechnungsnr AND konto_typ = 'debitoren'
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "rechnungsnr": invoice.number},
    ).fetchone()

    if existing_op:
        op_id = str(existing_op[0])
        db.execute(
            text(
                f"""
                UPDATE {op_table}
                SET op_betrag = :amount,
                    betrag = :amount,
                    offen = :amount,
                    kunde_id = :kunde_id,
                    kunde_name = :kunde_name,
                    faelligkeit = :faelligkeit,
                    op_status = 'offen',
                    updated_at = NOW()
                WHERE id = :id
                """
            ),
            {
                "id": op_id,
                "amount": total_gross,
                "kunde_id": invoice.customerId,
                "kunde_name": customer_name,
                "faelligkeit": invoice.dueDate,
            },
        )
    else:
        op_id = f"OP-AR-{invoice.number}"
        db.execute(
            text(
                f"""
                INSERT INTO {op_table}
                (id, tenant_id, konto_typ, op_status, rechnungsnr, rechnungsdatum, datum, faelligkeit,
                 op_betrag, betrag, offen, kunde_id, kunde_name, waehrung, zahlbar, created_at, updated_at)
                VALUES (:id, :tenant_id, 'debitoren', 'offen', :rechnungsnr, :rechnungsdatum, :datum, :faelligkeit,
                        :op_betrag, :betrag, :offen, :kunde_id, :kunde_name, :waehrung, :zahlbar, NOW(), NOW())
                """
            ),
            {
                "id": op_id,
                "tenant_id": tenant_id,
                "rechnungsnr": invoice.number,
                "rechnungsdatum": invoice.date,
                "datum": invoice.date,
                "faelligkeit": invoice.dueDate,
                "op_betrag": total_gross,
                "betrag": total_gross,
                "offen": total_gross,
                "kunde_id": invoice.customerId,
                "kunde_name": customer_name,
                "waehrung": "EUR",
                "zahlbar": True,
            },
        )

    db.commit()
    log_fibu_audit(
        db,
        tenant_id,
        "create",
        "open_item",
        op_id,
        {"source": "sales_invoice", "invoice_number": invoice.number, "amount": float(total_gross)},
    )
    logger.info("Created/updated GL booking and OP for invoice %s", invoice.number)


@router.post("", response_model=CompatFlexOut, summary="Invoice anlegen")
async def create_invoice(
    invoice: SalesInvoice,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
) -> dict:
    """Erstellt eine neue Rechnung im Finance-Modul."""
    try:
        if invoice.customerId:
            assert_customer_allowed_for_invoice(db, tenant_id, str(invoice.customerId))
        repo = get_repository(db)

        if invoice.subtotalNet == 0.0 and invoice.lines:
            invoice.subtotalNet = sum(line.qty * (line.price or 0.0) for line in invoice.lines)

        if invoice.totalTax == 0.0 and invoice.lines:
            invoice.totalTax = sum(
                line.qty * (line.price or 0.0) * (line.vatRate or 0.19) / 100
                for line in invoice.lines
            )

        if invoice.totalGross == 0.0:
            invoice.totalGross = invoice.subtotalNet + invoice.totalTax

        if not invoice.dueDate:
            payment_days = 30
            if invoice.paymentTerms.startswith("net"):
                try:
                    payment_days = int(invoice.paymentTerms.replace("net", ""))
                except Exception:
                    payment_days = 30
            invoice_date = datetime.strptime(invoice.date, "%Y-%m-%d")
            invoice.dueDate = (invoice_date + timedelta(days=payment_days)).strftime("%Y-%m-%d")

        doc_data = invoice.model_dump()
        result = save_to_store("sales_invoice", invoice.number, doc_data, repo)

        if invoice.status != "ENTWURF":
            await _create_gl_booking_and_op(db, invoice, tenant_id)
            canonical = f"{invoice.number}|{invoice.date}|{invoice.totalGross}|{invoice.customerId}"
            content_hash = sha256_hex(canonical.encode("utf-8"))
            register_artifact(
                db,
                tenant_id,
                invoice.number,
                "other",
                content_hash,
                f"invoice/ar/{invoice.number}",
                file_name=f"Rechnung_{invoice.number}.pdf",
                created_by=None,
            )

        logger.info("Invoice created: %s", invoice.number)
        return {
            "ok": True,
            "id": invoice.number,
            "number": invoice.number,
            "invoice": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating invoice: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")


@router.get("/{invoice_number}", response_model=CompatFlexOut, summary="Invoice abrufen")
async def get_invoice(
    invoice_number: str,
    db: Session = Depends(get_db)
) -> dict:
    """Ruft eine Rechnung anhand der Rechnungsnummer ab."""
    try:
        repo = get_repository(db)
        invoice = get_from_store("sales_invoice", invoice_number, repo)
        if not invoice:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_number} not found")
        return {"ok": True, "invoice": invoice}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting invoice: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get invoice: {str(e)}")


@router.put("/{invoice_number}", response_model=CompatFlexOut, summary="Invoice aktualisieren")
async def update_invoice(
    invoice_number: str,
    invoice: SalesInvoice,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
) -> dict:
    """Aktualisiert eine bestehende Rechnung."""
    try:
        repo = get_repository(db)
        existing = get_from_store("sales_invoice", invoice_number, repo)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_number} not found")

        if invoice.subtotalNet == 0.0 and invoice.lines:
            invoice.subtotalNet = sum(line.qty * (line.price or 0.0) for line in invoice.lines)

        if invoice.totalTax == 0.0 and invoice.lines:
            invoice.totalTax = sum(
                line.qty * (line.price or 0.0) * (line.vatRate or 0.19) / 100
                for line in invoice.lines
            )

        if invoice.totalGross == 0.0:
            invoice.totalGross = invoice.subtotalNet + invoice.totalTax

        result = save_to_store("sales_invoice", invoice_number, invoice.model_dump(), repo)

        old_status = existing.get("status", "ENTWURF")
        if old_status == "ENTWURF" and invoice.status != "ENTWURF":
            await _create_gl_booking_and_op(db, invoice, tenant_id)

        logger.info("Invoice updated: %s", invoice_number)
        return {
            "ok": True,
            "id": invoice_number,
            "number": invoice_number,
            "invoice": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating invoice: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")


@router.get("", response_model=CompatFlexOut, summary="Invoices auflisten")
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Listet alle Rechnungen auf mit Filterung."""
    try:
        repo = get_repository(db)
        payload = list_from_store(
            "sales_invoice", skip=0, limit=100_000, repo=repo
        )
        all_invoices = payload.get("data") or []

        filtered = all_invoices
        if status:
            filtered = [inv for inv in filtered if inv.get("status") == status]
        if customer_id:
            filtered = [inv for inv in filtered if inv.get("customerId") == customer_id]

        filtered.sort(key=lambda x: x.get("date", ""), reverse=True)
        total = len(filtered)
        paginated = filtered[skip:skip + limit]

        return {
            "ok": True,
            "invoices": paginated,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        logger.error("Error listing invoices: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list invoices: {str(e)}")



@router.delete("/{invoice_number}", status_code=204, response_class=Response, response_model=None, summary="Invoice löschen")
async def delete_invoice(
    invoice_number: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> None:
    """Löscht eine Rechnung im Entwurfsstatus."""
    try:
        repo = get_repository(db)
        existing = get_from_store("sales_invoice", invoice_number, repo)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_number} not found")
        if existing.get("status", "ENTWURF") not in ("ENTWURF", "DRAFT", "draft"):
            raise HTTPException(status_code=400, detail="Only draft invoices can be deleted")
        delete_from_store("sales_invoice", invoice_number, repo)
        logger.info("Invoice deleted: %s", invoice_number)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting invoice: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")


@router.post("/{invoice_number}/storno", response_model=CompatFlexOut, summary="Invoice storno")
async def storno_invoice(
    invoice_number: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Storniert eine gebuchte Rechnung: erzeugt Gegenbuchung (Reversal) via GoBD-Hashkette.

    - Setzt die ursprüngliche JournalEntry auf status='reversed'
    - Erstellt neue JournalEntry mit umgekehrten Soll/Haben-Positionen
    - Markiert den offenen Posten als 'storniert'
    """
    try:
        row = db.execute(
            text(
                """
                SELECT id, status FROM domain_erp.journal_entries
                WHERE tenant_id = :tid
                  AND source = 'sales_invoice'
                  AND (document_number = :nr OR reference = :nr)
                LIMIT 1
                """
            ),
            {"tid": tenant_id, "nr": invoice_number},
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"Keine Buchung für Rechnung {invoice_number} gefunden")

        je_id = str(row[0])
        fin = FinanceTransactionService(db, tenant_id)
        from app.core.exceptions import ValidationFailedError as _VFE
        try:
            original, reversal = fin.reverse(je_id, reason=f"Storno Rechnung {invoice_number}")
        except _VFE as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        op_table = _resolve_open_items_table(db)
        try:
            db.execute(
                text(
                    f"""
                    UPDATE {op_table}
                    SET op_status = 'storniert', offen = 0, updated_at = NOW()
                    WHERE tenant_id = :tid AND rechnungsnr = :nr AND konto_typ = 'debitoren'
                    """
                ),
                {"tid": tenant_id, "nr": invoice_number},
            )
            db.commit()
        except Exception:
            db.rollback()

        log_fibu_audit(
            db, tenant_id, "storno", "journal_entry", je_id,
            {"invoice_number": invoice_number, "reversal_id": str(reversal.id)},
        )
        logger.info("Invoice storno: %s → reversal %s", invoice_number, reversal.id)
        return {"ok": True, "original_entry_id": je_id, "reversal_entry_id": str(reversal.id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in storno_invoice: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Storno fehlgeschlagen: {str(e)}")
