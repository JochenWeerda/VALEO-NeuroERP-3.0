"""
Accounts Payable (AP) Invoices API
FIBU-AP-02: Eingangsrechnungen
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.core.database import get_db
from app.documents.models import SalesInvoice  # Reusing model structure for now
from app.documents.router_helpers import get_repository, save_to_store, get_from_store, list_from_store, delete_from_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ap/invoices", tags=["finance", "ap", "invoices"])


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


@router.post("/")
async def create_ap_invoice(doc: SalesInvoice, db: Session = Depends(get_db)) -> dict:
    """Erstellt eine neue Eingangsrechnung (Kreditoren)."""
    logger.info(f"Creating AP invoice: {doc.number}")
    try:
        repo = get_repository(db)
        doc.date = datetime.now().isoformat()[:10]  # Set current date
        doc.dueDate = (datetime.now() + timedelta(days=30)).isoformat()[:10]  # Default 30 days due
        doc.status = "ENTWURF"  # Initial status

        doc = calculate_invoice_totals(doc)  # Calculate totals

        result = save_to_store("ap_invoice", doc.number, doc.model_dump(), repo)
        return {"status": "ok", "message": "AP Invoice created", "data": result}
    except Exception as e:
        logger.error(f"Error creating AP invoice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create AP invoice: {str(e)}")


@router.get("/{invoice_id}")
async def get_ap_invoice(invoice_id: str, db: Session = Depends(get_db)) -> dict:
    """Ruft eine Eingangsrechnung anhand ihrer ID ab."""
    logger.info(f"Fetching AP invoice: {invoice_id}")
    repo = get_repository(db)
    invoice = get_from_store("ap_invoice", invoice_id, repo)
    if not invoice:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return invoice


@router.put("/{invoice_id}")
async def update_ap_invoice(invoice_id: str, doc: SalesInvoice, db: Session = Depends(get_db)) -> dict:
    """Aktualisiert eine bestehende Eingangsrechnung."""
    logger.info(f"Updating AP invoice: {invoice_id}")
    repo = get_repository(db)
    existing_invoice = get_from_store("ap_invoice", invoice_id, repo)
    if not existing_invoice:
        raise HTTPException(status_code=404, detail="AP Invoice not found")

    doc.number = invoice_id  # Ensure number matches ID
    doc = calculate_invoice_totals(doc)  # Recalculate totals

    result = save_to_store("ap_invoice", doc.number, doc.model_dump(), repo)
    return {"status": "ok", "message": "AP Invoice updated", "data": result}


@router.get("/")
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
    all_invoices = list_from_store("ap_invoice", repo)

    filtered_invoices = []
    for inv in all_invoices:
        match = True
        if query and not (query.lower() in inv.get("number", "").lower() or
                         query.lower() in inv.get("customerId", "").lower() or  # customerId = supplier_id for AP
                         query.lower() in inv.get("notes", "").lower()):
            match = False
        if status and inv.get("status", "").lower() != status.lower():
            match = False
        if supplier_id and inv.get("customerId", "").lower() != supplier_id.lower():
            match = False
        if match:
            filtered_invoices.append(inv)

    return filtered_invoices[skip : skip + limit]


@router.delete("/{invoice_id}")
async def delete_ap_invoice(invoice_id: str, db: Session = Depends(get_db)) -> dict:
    """Löscht eine Eingangsrechnung."""
    logger.info(f"Deleting AP invoice: {invoice_id}")
    repo = get_repository(db)
    success = delete_from_store("ap_invoice", invoice_id, repo)
    if not success:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return {"status": "ok", "message": "AP Invoice deleted"}


@router.post("/{invoice_id}/approve")
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

    # Update status to approved
    invoice["status"] = "FREIGEGEBEN"
    invoice["approvedBy"] = approved_by
    invoice["approvedAt"] = datetime.now().isoformat()

    result = save_to_store("ap_invoice", invoice_id, invoice, repo)
    return {"status": "ok", "message": "AP Invoice approved", "data": result}


@router.post("/{invoice_id}/post")
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

    # Update status to posted
    invoice["status"] = "VERBUCHT"
    invoice["postedBy"] = posted_by
    invoice["postedAt"] = datetime.now().isoformat()

    # Create GL journal entry
    try:
        from app.api.v1.schemas.finance import JournalEntryCreate, JournalEntryLine
        from sqlalchemy import text
        
        # Extract invoice data
        invoice_date = invoice.get("date", datetime.now().isoformat()[:10])
        invoice_number = invoice.get("number", invoice_id)
        total_gross = float(invoice.get("totalGross", 0))
        subtotal_net = float(invoice.get("subtotalNet", 0))
        total_tax = float(invoice.get("totalTax", 0))
        tenant_id = invoice.get("tenantId", "system")
        
        # Determine period from invoice date
        period = invoice_date[:7]  # YYYY-MM format
        
        # Create journal entry lines
        from app.api.v1.schemas.finance import JournalEntryLine
        
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
                    account_id="1576",  # Vorsteuer
                    debit_amount=Decimal("0.00"),
                    credit_amount=Decimal(str(total_tax)),
                    line_number=3,
                    description="Vorsteuer"
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
        
        # Store journal entry ID in invoice
        invoice["journalEntryId"] = str(journal_entry.id) if hasattr(journal_entry, 'id') else str(journal_entry.get('id', ''))
        logger.info(f"Created GL journal entry {invoice.get('journalEntryId')} for AP invoice {invoice_id}")
        
    except Exception as e:
        logger.error(f"Could not create GL journal entry: {e}", exc_info=True)
        # Continue without GL entry - invoice is still posted
        invoice["journalEntryError"] = str(e)

    # Create open item (OP) for AP invoice
    try:
        op_insert = text("""
            INSERT INTO offene_posten
            (id, tenant_id, rechnungsnr, datum, faelligkeit, betrag, offen, kunde_id, kunde_name, zahlbar, created_at, updated_at)
            VALUES (:id, :tenant_id, :rechnungsnr, :datum, :faelligkeit, :betrag, :offen, :kunde_id, :kunde_name, :zahlbar, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                offen = EXCLUDED.offen,
                updated_at = NOW()
        """)
        
        db.execute(op_insert, {
            "id": f"OP-AP-{invoice_id}",
            "tenant_id": invoice.get("tenantId", "system"),
            "rechnungsnr": invoice.get("number", invoice_id),
            "datum": invoice.get("date", datetime.now().isoformat()[:10]),
            "faelligkeit": invoice.get("dueDate", (datetime.now() + timedelta(days=30)).isoformat()[:10]),
            "betrag": invoice.get("totalGross", 0),
            "offen": invoice.get("totalGross", 0),
            "kunde_id": invoice.get("supplierId", ""),  # supplierId = creditor for AP
            "kunde_name": invoice.get("supplierName", ""),
            "zahlbar": True
        })
        db.commit()
        logger.info(f"Created open item for AP invoice {invoice_id}")
        
    except Exception as e:
        logger.warning(f"Could not create open item (table may not exist): {e}")
        db.rollback()
        # Continue without OP for now

    result = save_to_store("ap_invoice", invoice_id, invoice, repo)
    return {"status": "ok", "message": "AP Invoice posted", "data": result}

