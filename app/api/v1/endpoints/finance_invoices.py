"""
Finance Invoices API Endpoints
Spezifische Endpoints für Finance-Modul Invoices
"""

from datetime import datetime, timedelta
import logging
from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.customer_sales_eligibility import assert_customer_allowed_for_invoice
from app.services.sales_posting_service import SalesPostingService
from app.services.finance_transaction_service import FinanceTransactionService
from app.core.fibu_audit import log_fibu_audit
from app.core.gobd_artifact import register_artifact, sha256_hex
from app.core.tenant import get_tenant_id
from app.documents.models import SalesInvoice
from app.documents.router_helpers import (
    delete_from_store,
    get_from_store,
    get_repository,
    list_from_store,
    save_to_store,
)

from app.api.v1.schemas.base import StatusResponse
from app.api.v1.schemas.finance_invoices_schemas import FinanceInvoicesOut


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finance/invoices", tags=["finance", "invoices"])


def _resolve_open_items_table(db: Session) -> str:
    """Resolve offene_posten table name for mixed deployments."""
    for candidate in ("domain_erp.offene_posten", "offene_posten"):
        if db.execute(text("SELECT to_regclass(:name)"), {"name": candidate}).scalar():
            return candidate
    raise RuntimeError("offene_posten table not found")


def _resolve_customer_name(db: Session, customer_id: str, tenant_id: str | None = None) -> str:
    """Den Namen zur Partnerkennung holen — sonst steht die Kennung im Beleg.

    Gelesen wurde ``domain_shared.business_partners``: eine Tabelle, die es
    nicht gibt. Das ``except`` fing das ab, und im Beleg stand statt des Namens
    die Kennung — was aussieht, als sei der Kunde so benannt.

    Der Partnerstamm liegt in ``domain_crm.business_partners``, und der Name
    heisst dort ``name_1`` (es gibt ein ``name_2`` daneben). Der Mandant gehoert
    in die Abfrage: Ein Partnername ist nichts, was ueber Mandantengrenzen
    hinweg beantwortet wird.
    """
    customer_name = customer_id
    try:
        row = db.execute(
            text(
                """
                SELECT name_1
                FROM domain_crm.business_partners
                WHERE partner_id = :partner_id
                  AND (:tenant_id IS NULL OR tenant_id = :tenant_id)
                LIMIT 1
                """
            ),
            {"partner_id": customer_id, "tenant_id": tenant_id},
        ).fetchone()
        if row and row[0]:
            customer_name = str(row[0])
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass
    return customer_name


def _post_sales_invoice_financials(
    db: Session,
    invoice: SalesInvoice,
    tenant_id: str,
) -> dict[str, str]:
    """Buchung + offener Posten in der Transaktion des Aufrufers (kein eigener Commit)."""
    return SalesPostingService(db, tenant_id, commit=False).post_ausgangsrechnung_with_op(
        invoice_number=invoice.number,
        invoice_date=invoice.date,
        customer_id=invoice.customerId,
        net_amount=invoice.subtotalNet,
        tax_amount=invoice.totalTax,
        gross_amount=invoice.totalGross,
        due_date=invoice.dueDate,
    )


def _beleg_speichern(repo, number: str, data: dict) -> dict:
    """Rechnungsbeleg ohne eigenen Commit; ohne Datenbank (kein Repository) der Prozessspeicher."""
    if repo is None:
        return save_to_store("sales_invoice", number, data, repo)
    return repo.save_document("sales_invoice", number, data, commit=False)


@router.post("", response_model=FinanceInvoicesOut, summary="Invoice anlegen")
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
        # Beleg, Buchung, offener Posten, Archiv und Lieferscheinbezug: ein Commit am
        # Ende. Bis 08.10.2026 committete der Dokumentspeicher zuerst; scheiterte die
        # Buchung, stand die Rechnung ohne Buchung und ohne offenen Posten da.
        result = _beleg_speichern(repo, invoice.number, doc_data)

        if invoice.status != "ENTWURF":
            _post_sales_invoice_financials(db, invoice, tenant_id)
            canonical = f"{invoice.number}|{invoice.date}|{invoice.totalGross}|{invoice.customerId}"
            content_hash = sha256_hex(canonical.encode("utf-8"))
            register_artifact(
                db,
                tenant_id,
                invoice.number,
                "other",
                content_hash,
                f"invoice/ar/{invoice.number}",
                file_name=f"Rechnung_{invoice.number}_buchungsdaten.txt",
                created_by=None,
                doc_type="sales_invoice",
                content=canonical.encode("utf-8"),
            )

        # Belegbruch schließen: Lieferschein invoice_number befüllen wenn sourceDelivery gesetzt
        if invoice.sourceDelivery:
            try:
                # Savepoint: ein Fehler hier bricht die Transaktion nicht ab. Bis
                # 07.10.2026 lief das UPDATE nach dem letzten Commit und wurde nie
                # festgeschrieben; ein Fehler liess die Transaktion tot zurueck.
                with db.begin_nested():
                    db.execute(
                        text("""
                            UPDATE domain_sales.delivery_notes
                            SET invoice_number = :inv_nr, updated_at = NOW()
                            WHERE (id = :dn_ref OR delivery_note_number = :dn_ref)
                              AND tenant_id = :tid
                              AND (invoice_number IS NULL OR invoice_number = '')
                        """),
                        {"inv_nr": invoice.number, "dn_ref": invoice.sourceDelivery, "tid": tenant_id},
                    )
            except SQLAlchemyError as exc:  # Lieferscheinbezug ist Nebeninformation
                logger.warning("Lieferschein %s nicht mit Rechnung %s verknuepft: %s",
                               invoice.sourceDelivery, invoice.number, exc)

        # Archiveintrag und Lieferscheinbezug gemeinsam festschreiben.
        db.commit()
        logger.info("Invoice created: %s", invoice.number)
        return {
            "ok": True,
            "id": invoice.number,
            "number": invoice.number,
            "invoice": result,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Error creating invoice: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")


@router.get("/{invoice_number}", response_model=StatusResponse, summary="Invoice abrufen")
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


@router.put("/{invoice_number}", response_model=FinanceInvoicesOut, summary="Invoice aktualisieren")
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

        result = _beleg_speichern(repo, invoice_number, invoice.model_dump())

        old_status = existing.get("status", "ENTWURF")
        if old_status == "ENTWURF" and invoice.status != "ENTWURF":
            _post_sales_invoice_financials(db, invoice, tenant_id)
        # Beleg und Buchung gemeinsam (wie beim Anlegen).
        db.commit()

        logger.info("Invoice updated: %s", invoice_number)
        return {
            "ok": True,
            "id": invoice_number,
            "number": invoice_number,
            "invoice": result,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Error updating invoice: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")


@router.get("", response_model=FinanceInvoicesOut, summary="Invoices auflisten")
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


@router.post("/{invoice_number}/storno", response_model=StatusResponse, summary="Invoice storno")
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
                    """  # nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden
                ),
                {"tid": tenant_id, "nr": invoice_number},
            )
            db.commit()
        except Exception:
            db.rollback()

        # Belegbruch schließen: Rechnungsdokument im Store auf STORNIERT setzen
        try:
            repo = get_repository(db)
            inv = get_from_store("sales_invoice", invoice_number, repo)
            if inv:
                inv["status"] = "STORNIERT"
                save_to_store("sales_invoice", invoice_number, inv, repo)
        except Exception:  # noqa: BLE001 — Store-Update nicht kritisch für Buchungsstorno
            pass

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
