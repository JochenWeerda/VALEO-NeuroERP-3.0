"""
Accounts Payable (AP) Invoices API
FIBU-AP-02: Eingangsrechnungen
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.core.database import get_db
from app.core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_ap_invoice_datensatz,
)
from app.core import endpoint_gateways
from app.core.fibu_audit import log_fibu_audit
from app.core.ap_approval_status import APPROVAL_STATUS_TO_DOCUMENT_STATUS
from app.documents.models import SalesInvoice  # Reusing model structure for now
from app.documents.router_helpers import get_repository, save_to_store, get_from_store, list_from_store, delete_from_store
from app.domains.shared.events import get_event_publisher
from app.domains.shared.process_events import APInvoicePosted
from app.infrastructure.eventbus.outbox import OutboxPublisher
from app.finance.tax_resolver import resolve_partner_country, resolve_tax_key_accounts

logger = logging.getLogger(__name__)
from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.api.v1.schemas.ap_invoices_schemas import ApInvoicesOut


router = APIRouter(prefix="/ap/invoices", tags=["finance", "ap", "invoices"])


def _build_ap_invoice_dq_datensatz(invoice: SalesInvoice) -> dict[str, Any]:
    return {
        "rechnungsnummer": invoice.number,
        "lieferant_id": invoice.customerId,
        "faelligkeit": invoice.dueDate,
        "brutto_betrag_eur": invoice.totalGross,
        "waehrung": "EUR",
    }


def _compute_ap_invoice_semantic_status(invoice: dict[str, Any]) -> str:
    document_status = str(invoice.get("status") or "ENTWURF")
    approval_status = invoice.get("approval_status")

    if document_status in {"VERBUCHT", "BEZAHLT", "TEILWEISE_FREIGEGEBEN"}:
        return document_status
    if approval_status == "pending":
        return "ZUR_FREIGABE"
    if approval_status == "partially_approved":
        return "TEILWEISE_FREIGEGEBEN"
    if approval_status == "approved":
        return "FREIGEGEBEN"
    if approval_status == "rejected":
        return "ABGELEHNT"
    return document_status


def _serialize_approval_snapshot(response) -> dict[str, Any]:
    return {
        "approval_status": response.status,
        "approval_required_approvals": response.required_approvals,
        "approval_current_approvals": response.current_approvals,
        "approval_override_resolution": response.override_resolution.model_dump(exclude_none=True),
        "approval_explainability": response.explainability.model_dump(exclude_none=True),
    }


async def _load_invoice_approval_status(invoice: dict[str, Any], db: Session):
    gateway = endpoint_gateways.get_approval_workflow_gateway()
    if gateway is None:
        from app.api.v1.endpoints.ap_approval_workflow import get_approval_status

        return await get_approval_status(
            invoice["number"],
            tenant_id=invoice.get("tenantId", "system"),
            db=db,
        )
    return await gateway.get_status(invoice["number"], invoice.get("tenantId", "system"), db)


async def _enrich_invoice_with_approval(invoice: dict[str, Any], db: Session) -> dict[str, Any]:
    enriched = dict(invoice)
    response = await _load_invoice_approval_status(enriched, db)
    enriched.update(_serialize_approval_snapshot(response))
    enriched["semantic_status"] = _compute_ap_invoice_semantic_status(enriched)
    return enriched


async def _store_ap_invoice_posted_event_in_outbox(
    db,
    *,
    tenant_id: str,
    invoice_id: str,
    posted_by: str,
    journal_entry_id: str | None,
) -> None:
    event = APInvoicePosted(
        aggregate_id=invoice_id,
        timestamp=datetime.utcnow(),
        tenant_id=tenant_id,
        workflow_instance_id=f"wf-ap-{invoice_id}",
        invoice_id=invoice_id,
        posted_by=posted_by,
        journal_entry_id=journal_entry_id,
    )
    outbox = OutboxPublisher(db, get_event_publisher())
    await outbox.store_event(event, tenant_id=tenant_id)


# Helper to calculate totals (same as AR invoices)
def calculate_invoice_totals(invoice: SalesInvoice) -> SalesInvoice:
    """Berechnet Summen für Eingangsrechnung."""
    subtotal_net = 0.0
    total_tax = 0.0
    for line in invoice.lines:
        line_net = line.qty * (line.price or 0)
        subtotal_net += line_net
        total_tax += line_net * ((line.vatRate or 0) / 100)
    invoice.subtotalNet = round(subtotal_net, 2)
    invoice.totalTax = round(total_tax, 2)
    invoice.totalGross = round(subtotal_net + total_tax, 2)
    return invoice


@router.post("/", summary="Ap invoice anlegen",
    response_model=ApInvoicesOut, status_code=201
)
async def create_ap_invoice(doc: SalesInvoice, db: Session = Depends(get_db)) -> dict:
    """Erstellt eine neue Eingangsrechnung (Kreditoren)."""
    logger.info(f"Creating AP invoice: {doc.number}")
    try:
        doc.date = datetime.now().isoformat()[:10]  # Set current date
        doc.dueDate = (datetime.now() + timedelta(days=30)).isoformat()[:10]  # Default 30 days due
        doc.status = "ENTWURF"  # Initial status

        doc = calculate_invoice_totals(doc)  # Calculate totals
        dq_result = evaluate_ap_invoice_datensatz(_build_ap_invoice_dq_datensatz(doc))
        if not dq_result.bestanden:
            raise HTTPException(status_code=422, detail=build_dq_error_detail("APRechnung", dq_result))

        repo = get_repository(db)
        result = save_to_store("ap_invoice", doc.number, doc.model_dump(), repo)
        return {"status": "ok", "message": "AP Invoice created", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating AP invoice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create AP invoice: {str(e)}")


@router.get("/{invoice_id}", summary="Ap invoice abrufen",
    response_model=ApInvoicesOut
)
async def get_ap_invoice(invoice_id: str, db: Session = Depends(get_db)) -> dict:
    """Ruft eine Eingangsrechnung anhand ihrer ID ab."""
    logger.info(f"Fetching AP invoice: {invoice_id}")
    repo = get_repository(db)
    invoice = get_from_store("ap_invoice", invoice_id, repo)
    if not invoice:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return await _enrich_invoice_with_approval(invoice, db)


@router.put("/{invoice_id}", summary="Ap invoice aktualisieren",
    response_model=ApInvoicesOut
)
async def update_ap_invoice(invoice_id: str, doc: SalesInvoice, db: Session = Depends(get_db)) -> dict:
    """Aktualisiert eine bestehende Eingangsrechnung."""
    logger.info(f"Updating AP invoice: {invoice_id}")
    repo = get_repository(db)
    existing_invoice = get_from_store("ap_invoice", invoice_id, repo)
    if not existing_invoice:
        raise HTTPException(status_code=404, detail="AP Invoice not found")

    doc.number = invoice_id  # Ensure number matches ID
    doc = calculate_invoice_totals(doc)  # Recalculate totals
    dq_result = evaluate_ap_invoice_datensatz(_build_ap_invoice_dq_datensatz(doc))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("APRechnung", dq_result))

    result = save_to_store("ap_invoice", doc.number, doc.model_dump(), repo)
    return {"status": "ok", "message": "AP Invoice updated", "data": result}


@router.get("/", summary="Ap invoices auflisten",
    response_model=list[ApInvoicesOut]
)
async def list_ap_invoices(
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    status: Optional[str] = None,
    supplier_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[dict]:
    """Listet Eingangsrechnungen auf, optional mit Filterung."""
    logger.info(f"Listing AP invoices with skip={skip}, limit={limit}, query={query}, status={status}, supplier_id={supplier_id}")
    repo = get_repository(db)
    result = list_from_store("ap_invoice", skip, limit, None, repo)
    all_invoices = result.get("data", []) if isinstance(result, dict) else []

    filtered_invoices = []
    for inv in all_invoices:
        enriched = await _enrich_invoice_with_approval(inv, db)
        match = True
        if query and not (query.lower() in enriched.get("number", "").lower() or
                         query.lower() in enriched.get("customerId", "").lower() or
                         query.lower() in enriched.get("notes", "").lower()):
            match = False
        if status and enriched.get("semantic_status", enriched.get("status", "")).lower() != status.lower():
            match = False
        if supplier_id and enriched.get("customerId", "").lower() != supplier_id.lower():
            match = False
        if match:
            filtered_invoices.append(enriched)

    return filtered_invoices[skip : skip + limit]


@router.delete("/{invoice_id}", summary="Ap invoice löschen",
    response_model=StatusResponse
)
async def delete_ap_invoice(invoice_id: str, db: Session = Depends(get_db)) -> dict:
    """Löscht eine Eingangsrechnung."""
    logger.info(f"Deleting AP invoice: {invoice_id}")
    repo = get_repository(db)
    success = delete_from_store("ap_invoice", invoice_id, repo)
    if not success:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return {"success": True, "message": "AP Invoice deleted"}


@router.post("/{invoice_id}/approve", summary="Ap invoice genehmigen",
    response_model=ApInvoicesOut
)
async def approve_ap_invoice(
    invoice_id: str,
    approved_by: str = Query(...),
    db: Session = Depends(get_db)
) -> dict:
    """Genehmigt eine Eingangsrechnung (für Freigabeworkflow)."""
    logger.info(f"Approving AP invoice: {invoice_id} by {approved_by}")
    repo = get_repository(db)
    invoice = get_from_store("ap_invoice", invoice_id, repo)
    if not invoice:
        raise HTTPException(status_code=404, detail="AP Invoice not found")

    tenant_id = invoice.get("tenantId", "system")
    gateway = endpoint_gateways.get_approval_workflow_gateway()
    if gateway is None:
        from app.api.v1.endpoints.ap_approval_workflow import approve_invoice

        response = await approve_invoice(
            type("ApprovalActionCompat", (), {
                "invoice_id": invoice_id,
                "approved_by": approved_by,
                "action": "approve",
                "comment": None,
            })(),
            tenant_id=tenant_id,
            db=db,
        )
    else:
        current_status = await gateway.get_status(invoice_id, tenant_id, db)
        if current_status.status == "not_requested":
            await gateway.request_approval(invoice_id, tenant_id, approved_by, None, db)
        response = await gateway.approve_invoice(invoice_id, tenant_id, approved_by, "approve", None, db)

    invoice["status"] = APPROVAL_STATUS_TO_DOCUMENT_STATUS.get(response.status, invoice.get("status", "ENTWURF"))
    invoice["approvedBy"] = approved_by
    invoice["approvedAt"] = datetime.now().isoformat()
    save_to_store("ap_invoice", invoice_id, invoice, repo)
    return {
        "status": "ok",
        "message": "AP Invoice approved",
        "data": response.model_dump(exclude_none=True),
    }


@router.post("/{invoice_id}/post", summary="Ap invoice erstellen",
    response_model=ApInvoicesOut
)
async def post_ap_invoice(
    invoice_id: str,
    posted_by: str = Query(...),
    db: Session = Depends(get_db)
) -> dict:
    """Bucht eine Eingangsrechnung (erzeugt GL-Buchung + OP)."""
    logger.info(f"Posting AP invoice: {invoice_id} by {posted_by}")
    repo = get_repository(db)
    invoice = get_from_store("ap_invoice", invoice_id, repo)
    if not invoice:
        raise HTTPException(status_code=404, detail="AP Invoice not found")

    # Check approval status via workflow API
    try:
        from app.api.v1.endpoints.ap_approval_workflow import get_approval_status
        approval_status = await get_approval_status(invoice_id, tenant_id=invoice.get("tenantId", "system"), db=db)
        
        if not approval_status.can_post:
            raise HTTPException(
                status_code=400,
                detail=f"Invoice must be approved before posting. Current status: {approval_status.status}, Required: {approval_status.required_approvals}, Current: {approval_status.current_approvals}"
            )
    except ImportError:
        # Fallback to simple status check if workflow API not available
        if invoice.get("status") != "FREIGEGEBEN":
            raise HTTPException(
                status_code=400,
                detail="Invoice must be approved before posting"
            )

    # FIBU-GL-05: block posting in closed periods
    invoice_date = invoice.get("date", datetime.now().isoformat()[:10])
    period = str(invoice_date)[:7]
    period_status = db.execute(
        text(
            """
            SELECT status
            FROM finance_accounting_periods
            WHERE tenant_id = :tenant_id AND period = :period
            LIMIT 1
            """
        ),
        {"tenant_id": invoice.get("tenantId", "system"), "period": period},
    ).fetchone()
    if period_status and str(period_status[0]) != "OPEN":
        raise HTTPException(
            status_code=403,
            detail=f"Period {period} is {period_status[0]}. Posting is blocked."
        )

    # Update status to posted
    invoice["status"] = "VERBUCHT"
    invoice["postedBy"] = posted_by
    invoice["postedAt"] = datetime.now().isoformat()

    # Create GL journal entry
    try:
        from app.api.v1.schemas.finance import JournalEntryCreate, JournalEntryLine
        
        # Extract invoice data
        invoice_date = invoice.get("date", datetime.now().isoformat()[:10])
        invoice_number = invoice.get("number", invoice_id)
        total_gross = float(invoice.get("totalGross", 0))
        subtotal_net = float(invoice.get("subtotalNet", 0))
        total_tax = float(invoice.get("totalTax", 0))
        tenant_id = invoice.get("tenantId", "system")
        supplier_partner_id = invoice.get("customerId", "") or invoice.get("supplierId", "")
        invoice_country = invoice.get("country") or resolve_partner_country(db, supplier_partner_id, "DE")
        max_rate = Decimal("0.00")
        line_rates = []
        for line in (invoice.get("lines") or []):
            try:
                line_rates.append(Decimal(str(line.get("vatRate", 0) or 0)).quantize(Decimal("0.01")))
            except Exception:
                continue
        if line_rates:
            max_rate = max(line_rates)
        tax_key_cfg = resolve_tax_key_accounts(db, tenant_id, max_rate, invoice_country)
        input_tax_account = tax_key_cfg.get("debit_account") or "1576"
        reverse_charge = bool(tax_key_cfg.get("reverse_charge"))
        
        # Determine period from invoice date
        period = invoice_date[:7]  # YYYY-MM format
        
        # Create journal entry lines
        from app.api.v1.schemas.finance import JournalEntryLine  # noqa: F811
        
        journal_lines = [
            JournalEntryLine(
                account_id=invoice.get("supplierAccountId", "3300"),  # Kreditorenkonto
                debit_amount=Decimal(str(total_gross)),
                credit_amount=Decimal("0.00"),
                line_number=1,
                description=f"Eingangsrechnung {invoice_number}"
            ),
            JournalEntryLine(
                account_id=invoice.get("expenseAccountId", "6000"),  # Aufwandskonto
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal(str(subtotal_net)),
                line_number=2,
                description="Aufwand"
            )
        ]
        
        # Add tax line if tax > 0
        if total_tax > 0:
            journal_lines.append(
                JournalEntryLine(
                    account_id=input_tax_account,
                    debit_amount=Decimal("0.00"),
                    credit_amount=Decimal(str(total_tax)),
                    line_number=3,
                    description="Vorsteuer (Reverse-Charge)" if reverse_charge else "Vorsteuer"
                )
            )
        
        # Create journal entry
        journal_entry_data = JournalEntryCreate(
            date=invoice_date,
            period=period,
            description=f"Eingangsrechnung {invoice_number}",
            lines=journal_lines,
            document_type="AP_INVOICE",
            document_id=invoice_id,
            tenant_id=tenant_id
        )
        
        # Create journal entry directly via repository
        from app.infrastructure.repositories import JournalEntryRepository
        from app.core.dependency_container import container
        
        entry_repo = container.resolve(JournalEntryRepository)
        
        # Convert to dict for repository
        entry_dict = journal_entry_data.model_dump()
        entry_dict['total_debit'] = total_gross
        entry_dict['total_credit'] = subtotal_net + total_tax
        
        journal_entry = await entry_repo.create(entry_dict, tenant_id)
        je_id = str(journal_entry.id) if hasattr(journal_entry, 'id') else str(journal_entry.get('id', ''))
        log_fibu_audit(
            db, tenant_id, "create", "journal_entry", je_id,
            {"source": "ap_invoice", "invoice_id": invoice_id},
            request=None,
        )
        # Store journal entry ID in invoice
        invoice["journalEntryId"] = je_id
        logger.info(f"Created GL journal entry {invoice.get('journalEntryId')} for AP invoice {invoice_id}")
        
    except Exception as e:
        logger.error(f"Could not create GL journal entry: {e}", exc_info=True)
        # Continue without GL entry - invoice is still posted
        invoice["journalEntryError"] = str(e)

    # Create open item (OP) for AP invoice
    try:
        op_insert = text("""
            INSERT INTO domain_erp.offene_posten
            (id, tenant_id, konto_typ, op_status, rechnungsnr, rechnungsdatum, datum, faelligkeit, op_betrag, betrag, offen,
             lieferant_id, lieferant_name, waehrung, zahlbar, created_at, updated_at)
            VALUES (:id, :tenant_id, 'kreditoren', 'offen', :rechnungsnr, :rechnungsdatum, :datum, :faelligkeit, :op_betrag, :betrag, :offen,
                    :lieferant_id, :lieferant_name, :waehrung, :zahlbar, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                offen = EXCLUDED.offen,
                op_status = EXCLUDED.op_status,
                updated_at = NOW()
        """)
        
        db.execute(op_insert, {
            "id": f"OP-AP-{invoice_id}",
            "tenant_id": invoice.get("tenantId", "system"),
            "rechnungsnr": invoice.get("number", invoice_id),
            "rechnungsdatum": invoice.get("date", datetime.now().isoformat()[:10]),
            "datum": invoice.get("date", datetime.now().isoformat()[:10]),
            "faelligkeit": invoice.get("dueDate", (datetime.now() + timedelta(days=30)).isoformat()[:10]),
            "op_betrag": invoice.get("totalGross", 0),
            "betrag": invoice.get("totalGross", 0),
            "offen": invoice.get("totalGross", 0),
            "lieferant_id": invoice.get("customerId", "") or invoice.get("supplierId", ""),
            "lieferant_name": invoice.get("supplierName", "") or invoice.get("customerName", ""),
            "waehrung": invoice.get("currency", "EUR"),
            "zahlbar": True
        })
        db.commit()
        logger.info(f"Created open item for AP invoice {invoice_id}")
        
    except Exception as e:
        logger.warning(f"Could not create open item (table may not exist): {e}")
        db.rollback()
        # Continue without OP for now

    result = save_to_store("ap_invoice", invoice_id, invoice, repo)
    journal_entry_id = invoice.get("journalEntryId")
    if journal_entry_id:
        try:
            await _store_ap_invoice_posted_event_in_outbox(
                db,
                tenant_id=invoice.get("tenantId", "system"),
                invoice_id=invoice_id,
                posted_by=posted_by,
                journal_entry_id=journal_entry_id,
            )
        except Exception as exc:
            logger.warning("Could not store AP invoice posted outbox event: %s", exc)
    return {"status": "ok", "message": "AP Invoice posted", "data": result}

