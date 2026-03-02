"""
Finance Invoices API Endpoints
Spezifische Endpoints für Finance-Modul Invoices
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
import logging

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.gobd_artifact import register_artifact, sha256_hex
from app.documents.models import SalesInvoice, DocLine
from app.documents.router_helpers import (
    get_repository, save_to_store, get_from_store, list_from_store
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finance/invoices", tags=["finance", "invoices"])


async def _create_gl_booking_and_op(db: Session, invoice: SalesInvoice, repo, tenant_id: str = "default") -> None:
    """
    FIBU-AR-02: Erzeugt GL-Buchung und OP für Rechnung
    """
    try:
        period = invoice.date[:7]  # YYYY-MM format
        
        # Try to get customer name from business_partners table
        customer_name = invoice.customerId
        try:
            from app.infrastructure.models import BusinessPartner
            bp = db.query(BusinessPartner).filter(
                BusinessPartner.partner_id == invoice.customerId
            ).first()
            if bp:
                customer_name = bp.name or bp.partner_number or invoice.customerId
        except Exception:
            pass  # Use customerId as fallback
        
        # 1. Erzeuge GL-Journal Entry (Debitoren Soll, Erlöse Haben, USt Haben)
        # Soll: Debitoren (Forderungen) = totalGross
        # Haben: Erlöse = subtotalNet
        # Haben: USt = totalTax
        
        # Standard-Konten (in Production aus Konfiguration)
        debtor_account = "1200"  # Forderungen aus Lieferungen und Leistungen
        revenue_account = "8000"  # Erlöse
        
        # VAT accounts by rate
        vat_accounts = {
            19.0: "1776",  # USt 19%
            7.0: "1771",   # USt 7%
            0.0: "1779",   # USt 0% / Freigestellt
        }
        
        # Determine VAT rate from invoice lines (use most common)
        vat_rates = [line.vatRate or 0.0 for line in invoice.lines if line.vatRate]
        vat_rate = max(vat_rates) if vat_rates else 0.0
        vat_account = vat_accounts.get(vat_rate, "1776")  # Default to 19%
        
        # Journal Entry erstellen
        journal_entry_id = f"JE-{invoice.number}"
        
        # Group revenue and VAT by rate
        from collections import defaultdict
        revenue_by_rate = defaultdict(float)
        vat_by_rate = defaultdict(float)
        
        for line in invoice.lines:
            net = line.qty * (line.price or 0.0)
            vat_rate = line.vatRate or 0.0
            vat = net * vat_rate / 100
            revenue_by_rate[vat_rate] += net
            vat_by_rate[vat_rate] += vat
        
        # Build journal entry lines
        journal_lines = [
            {
                "account_id": debtor_account,
                "debit_amount": invoice.totalGross,
                "credit_amount": 0.0,
                "description": f"Forderung {invoice.customerId}"
            }
        ]
        
        # Revenue lines by rate
        for vat_rate, net_amount in revenue_by_rate.items():
            if net_amount > 0:
                journal_lines.append({
                    "account_id": revenue_account,
                    "debit_amount": 0.0,
                    "credit_amount": net_amount,
                    "description": f"Erlöse {vat_rate}%"
                })
        
        # VAT lines by rate
        for vat_rate, vat_amount in vat_by_rate.items():
            if vat_amount > 0:
                vat_acc = vat_accounts.get(vat_rate, "1776")
                journal_lines.append({
                    "account_id": vat_acc,
                    "debit_amount": 0.0,
                    "credit_amount": vat_amount,
                    "description": f"USt {vat_rate}%"
                })
        
        journal_entry = {
            "id": journal_entry_id,
            "tenant_id": tenant_id,
            "period": period,
            "entry_date": invoice.date,
            "description": f"Rechnung {invoice.number}",
            "status": "posted",
            "source": "sales_invoice",
            "source_id": invoice.number,
            "lines": journal_lines
        }
        
        # Speichere Journal Entry (vereinfacht - in Production über Repository)
        save_to_store("journal_entry", journal_entry_id, journal_entry, repo)
        
        # 2. Erzeuge Open Item (OP) für Debitoren
        op_id = f"OP-{invoice.number}"
        open_item = {
            "id": op_id,
            "tenant_id": tenant_id,
            "document_number": invoice.number,
            "customer_id": invoice.customerId,
            "customer_name": customer_name,
            "amount": invoice.totalGross,
            "open_amount": invoice.totalGross,
            "currency": "EUR",
            "due_date": invoice.dueDate,
            "status": "open",
            "created_at": datetime.now().isoformat()
        }
        
        # Speichere OP (vereinfacht - in Production über Repository)
        save_to_store("open_item", op_id, open_item, repo)
        
        logger.info(f"Created GL booking and OP for invoice {invoice.number}")
        
    except Exception as e:
        logger.error(f"Error creating GL booking/OP for invoice {invoice.number}: {e}")
        # Don't fail invoice creation if GL/OP creation fails
        # In production, use transaction rollback


@router.post("", response_model=dict)
async def create_invoice(
    invoice: SalesInvoice,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
) -> dict:
    """
    Erstellt eine neue Rechnung im Finance-Modul
    
    Args:
        invoice: SalesInvoice Model mit allen notwendigen Feldern
        db: Database Session
    
    Returns:
        Erstellte Rechnung mit ID und Nummer
    """
    try:
        repo = get_repository(db)
        
        # Berechne Beträge falls nicht gesetzt
        if invoice.subtotalNet == 0.0 and invoice.lines:
            invoice.subtotalNet = sum(
                line.qty * (line.price or 0.0) for line in invoice.lines
            )
        
        if invoice.totalTax == 0.0 and invoice.lines:
            invoice.totalTax = sum(
                line.qty * (line.price or 0.0) * (line.vatRate or 0.19) / 100
                for line in invoice.lines
            )
        
        if invoice.totalGross == 0.0:
            invoice.totalGross = invoice.subtotalNet + invoice.totalTax
        
        # Berechne Fälligkeitsdatum basierend auf Zahlungsbedingungen
        if not invoice.dueDate:
            payment_days = 30  # Default: 30 Tage netto
            if invoice.paymentTerms.startswith("net"):
                try:
                    payment_days = int(invoice.paymentTerms.replace("net", ""))
                except:
                    pass
            
            invoice_date = datetime.strptime(invoice.date, "%Y-%m-%d")
            due_date = invoice_date + timedelta(days=payment_days)
            invoice.dueDate = due_date.strftime("%Y-%m-%d")
        
        # Speichere Rechnung
        doc_data = invoice.model_dump()
        result = save_to_store("sales_invoice", invoice.number, doc_data, repo)
        
        # FIBU-AR-02: Wenn Rechnung verbucht wird (status != ENTWURF), erzeuge GL-Buchung + OP
        if invoice.status != "ENTWURF":
            await _create_gl_booking_and_op(db, invoice, repo, tenant_id)
            # GoBD: Belegartefakt für Ausgangsrechnung registrieren
            canonical = f"{invoice.number}|{invoice.date}|{invoice.totalGross}|{invoice.customerId}"
            content_hash = sha256_hex(canonical.encode("utf-8"))
            register_artifact(
                db, tenant_id, invoice.number, "other",
                content_hash, f"invoice/ar/{invoice.number}", file_name=f"Rechnung_{invoice.number}.pdf", created_by=None,
            )
        
        logger.info(f"Invoice created: {invoice.number}")
        
        return {
            "ok": True,
            "id": invoice.number,
            "number": invoice.number,
            "invoice": result
        }
    
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")


@router.get("/{invoice_number}", response_model=dict)
async def get_invoice(
    invoice_number: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Ruft eine Rechnung anhand der Rechnungsnummer ab
    
    Args:
        invoice_number: Rechnungsnummer (z.B. "INV-2025-00001")
        db: Database Session
    
    Returns:
        Rechnung-Daten
    """
    try:
        repo = get_repository(db)
        invoice = get_from_store("sales_invoice", invoice_number, repo)
        
        if not invoice:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_number} not found")
        
        return {
            "ok": True,
            "invoice": invoice
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get invoice: {str(e)}")


@router.put("/{invoice_number}", response_model=dict)
async def update_invoice(
    invoice_number: str,
    invoice: SalesInvoice,
    db: Session = Depends(get_db)
) -> dict:
    """
    Aktualisiert eine bestehende Rechnung
    
    Args:
        invoice_number: Rechnungsnummer
        invoice: Aktualisierte Rechnungsdaten
        db: Database Session
    
    Returns:
        Aktualisierte Rechnung
    """
    try:
        repo = get_repository(db)
        
        # Prüfe ob Rechnung existiert
        existing = get_from_store("sales_invoice", invoice_number, repo)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_number} not found")
        
        # Berechne Beträge falls nicht gesetzt
        if invoice.subtotalNet == 0.0 and invoice.lines:
            invoice.subtotalNet = sum(
                line.qty * (line.price or 0.0) for line in invoice.lines
            )
        
        if invoice.totalTax == 0.0 and invoice.lines:
            invoice.totalTax = sum(
                line.qty * (line.price or 0.0) * (line.vatRate or 0.19) / 100
                for line in invoice.lines
            )
        
        if invoice.totalGross == 0.0:
            invoice.totalGross = invoice.subtotalNet + invoice.totalTax
        
        # Speichere aktualisierte Rechnung
        doc_data = invoice.model_dump()
        result = save_to_store("sales_invoice", invoice_number, doc_data, repo)
        
        # FIBU-AR-02: Wenn Rechnung jetzt verbucht wird (status != ENTWURF), erzeuge GL-Buchung + OP
        old_status = existing.get("status", "ENTWURF")
        if old_status == "ENTWURF" and invoice.status != "ENTWURF":
            await _create_gl_booking_and_op(db, invoice, repo)
        
        logger.info(f"Invoice updated: {invoice_number}")
        
        return {
            "ok": True,
            "id": invoice_number,
            "number": invoice_number,
            "invoice": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")


@router.get("", response_model=dict)
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Listet alle Rechnungen auf mit Filterung
    
    Args:
        skip: Anzahl zu überspringender Einträge (Pagination)
        limit: Maximale Anzahl zurückgegebener Einträge
        status: Filter nach Status (optional)
        customer_id: Filter nach Kunden-ID (optional)
        db: Database Session
    
    Returns:
        Liste von Rechnungen mit Pagination-Info
    """
    try:
        repo = get_repository(db)
        all_invoices = list_from_store("sales_invoice", repo)
        
        # Filter anwenden
        filtered = all_invoices
        if status:
            filtered = [inv for inv in filtered if inv.get("status") == status]
        if customer_id:
            filtered = [inv for inv in filtered if inv.get("customerId") == customer_id]
        
        # Sortiere nach Datum (neueste zuerst)
        filtered.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Pagination
        total = len(filtered)
        paginated = filtered[skip:skip + limit]
        
        return {
            "ok": True,
            "invoices": paginated,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error listing invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list invoices: {str(e)}")

