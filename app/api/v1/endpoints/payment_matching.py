"""
Payment Matching API
FIBU-AR-03: Zahlungseingänge & Matching
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
import logging
import csv
import io

from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class PaymentEntry(BaseModel):
    """Payment entry from bank import."""
    id: Optional[str] = None
    tenant_id: str
    bank_account: str
    booking_date: date
    value_date: date
    amount: Decimal
    currency: str = "EUR"
    reference: Optional[str] = None
    remittance_info: Optional[str] = None
    creditor_name: Optional[str] = None
    creditor_iban: Optional[str] = None
    debtor_name: Optional[str] = None
    debtor_iban: Optional[str] = None
    matched_op_id: Optional[str] = None
    match_status: str = "UNMATCHED"  # UNMATCHED, MATCHED, PARTIAL, MANUAL
    created_at: Optional[datetime] = None


class OpenItemMatch(BaseModel):
    """Open item for matching."""
    op_id: str
    document_number: str
    customer_id: str
    customer_name: str
    amount: Decimal
    open_amount: Decimal
    due_date: date
    currency: str
    status: str


class MatchResult(BaseModel):
    """Result of payment matching."""
    payment_id: str
    matched_op_id: Optional[str] = None
    match_type: str  # FULL, PARTIAL, MULTIPLE
    matched_amount: Decimal
    remaining_amount: Decimal
    confidence: float  # 0.0 - 1.0
    match_reason: str


@router.post("/import/csv", response_model=List[PaymentEntry])
async def import_payments_csv(
    file: UploadFile = File(...),
    tenant_id: str = Query("default"),
    bank_account: str = Query(...),
    db: Session = Depends(get_db)
):
    """Import payments from CSV file."""
    try:
        content = await file.read()
        text_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(text_content))
        
        payments = []
        for row in csv_reader:
            # Expected CSV format: date, amount, reference, remittance_info
            try:
                booking_date = datetime.strptime(row.get('date', ''), '%Y-%m-%d').date()
                amount = Decimal(str(row.get('amount', '0')).replace(',', '.'))
                reference = row.get('reference', '')
                remittance_info = row.get('remittance_info', '')
                
                payment = PaymentEntry(
                    tenant_id=tenant_id,
                    bank_account=bank_account,
                    booking_date=booking_date,
                    value_date=booking_date,  # Use booking_date if value_date not provided
                    amount=amount,
                    reference=reference,
                    remittance_info=remittance_info,
                    match_status="UNMATCHED"
                )
                payments.append(payment)
            except Exception as e:
                logger.warning(f"Skipping invalid CSV row: {e}")
                continue
        
        # Store payments (simplified - in production, use proper table)
        payment_ids = []
        for payment in payments:
            payment_id = f"PAY-{datetime.now().timestamp()}-{len(payment_ids)}"
            payment.id = payment_id
            payment_ids.append(payment_id)
        
        logger.info(f"Imported {len(payments)} payments from CSV")
        return payments
        
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import CSV: {str(e)}")


@router.get("/unmatched", response_model=List[PaymentEntry])
async def get_unmatched_payments(
    tenant_id: str = Query("default"),
    bank_account: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get unmatched payment entries."""
    # In production, query from payment_entries table
    # For now, return empty list as placeholder
    return []


@router.get("/open-items/{customer_id}", response_model=List[OpenItemMatch])
async def get_open_items_for_matching(
    customer_id: str,
    tenant_id: str = Query("default"),
    db: Session = Depends(get_db)
):
    """Get open items for a customer for payment matching."""
    try:
        # Query open items from finance_open_items or offene_posten
        # Using simplified query - in production, use proper ORM
        query = """
            SELECT 
                id, document_number, customer_id, customer_name,
                amount, amount as open_amount, due_date, currency, status
            FROM finance_open_items
            WHERE tenant_id = :tenant_id 
            AND customer_id = :customer_id
            AND status IN ('open', 'partial')
            ORDER BY due_date ASC
        """
        
        results = db.execute(
            text(query),
            {"tenant_id": tenant_id, "customer_id": customer_id}
        ).fetchall()
        
        return [
            OpenItemMatch(
                op_id=str(r[0]),
                document_number=str(r[1]),
                customer_id=str(r[2]),
                customer_name=str(r[3]),
                amount=Decimal(str(r[4])),
                open_amount=Decimal(str(r[5])),
                due_date=r[6],
                currency=str(r[7]),
                status=str(r[8])
            )
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Error fetching open items: {e}")
        # Return empty list if table doesn't exist yet
        return []


@router.post("/match/{payment_id}", response_model=MatchResult)
async def match_payment(
    payment_id: str,
    op_id: Optional[str] = Query(None),
    match_type: str = Query("AUTO"),  # AUTO, MANUAL
    tenant_id: str = Query("default"),
    db: Session = Depends(get_db)
):
    """Match a payment to an open item."""
    try:
        # In production, fetch payment and OP from database
        # For now, return a match result
        
        if not op_id:
            raise HTTPException(status_code=400, detail="op_id is required for manual matching")
        
        # Fetch OP
        op_query = """
            SELECT id, document_number, customer_id, customer_name,
                   amount, amount as open_amount, due_date, currency, status
            FROM finance_open_items
            WHERE id = :op_id AND tenant_id = :tenant_id
        """
        op_result = db.execute(
            text(op_query),
            {"op_id": op_id, "tenant_id": tenant_id}
        ).fetchone()
        
        if not op_result:
            raise HTTPException(status_code=404, detail="Open item not found")
        
        open_amount = Decimal(str(op_result[5]))
        
        # In production, fetch payment amount and match
        # For now, assume full match
        matched_amount = open_amount
        remaining_amount = Decimal("0.00")
        
        # Update OP status
        if remaining_amount == 0:
            new_status = "closed"
        else:
            new_status = "partial"
        
        update_query = """
            UPDATE finance_open_items
            SET status = :status,
                amount = amount - :matched_amount
            WHERE id = :op_id AND tenant_id = :tenant_id
        """
        db.execute(
            text(update_query),
            {
                "status": new_status,
                "matched_amount": matched_amount,
                "op_id": op_id,
                "tenant_id": tenant_id
            }
        )
        db.commit()
        
        return MatchResult(
            payment_id=payment_id,
            matched_op_id=op_id,
            match_type="FULL" if remaining_amount == 0 else "PARTIAL",
            matched_amount=matched_amount,
            remaining_amount=remaining_amount,
            confidence=1.0,
            match_reason="Manual match"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching payment: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to match payment: {str(e)}")


@router.post("/auto-match", response_model=List[MatchResult])
async def auto_match_payments(
    tenant_id: str = Query("default"),
    bank_account: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Automatically match unmatched payments to open items."""
    try:
        # Get unmatched payments (simplified - in production, query from payment_entries table)
        # For now, we'll match based on bank statement lines
        
        # Get unmatched bank statement lines
        unmatched_query = text("""
            SELECT id, booking_date, amount, reference, remittance_info, creditor_name, debtor_name
            FROM domain_erp.bank_statement_lines
            WHERE tenant_id = :tenant_id 
            AND status = 'UNMATCHED'
            AND (bank_account_id = :bank_account OR :bank_account IS NULL)
            ORDER BY booking_date DESC
            LIMIT 100
        """)
        
        unmatched_lines = db.execute(
            unmatched_query,
            {"tenant_id": tenant_id, "bank_account": bank_account}
        ).fetchall()
        
        match_results = []
        
        for line in unmatched_lines:
            line_id = str(line[0])
            amount = Decimal(str(line[2]))
            reference = line[3]
            remittance_info = line[4] or ""
            creditor_name = line[5]
            debtor_name = line[6]
            
            # Rule 1: Match by reference number (extract invoice number from reference/remittance)
            invoice_match = None
            if reference:
                # Try to extract invoice number (e.g., "RE-2025-0001" or "INV-123")
                import re
                invoice_pattern = r'(RE|INV|RE-?\d{4}-?\d+|\d{4}-\d+)'
                invoice_match = re.search(invoice_pattern, reference.upper())
            
            if not invoice_match and remittance_info:
                invoice_match = re.search(invoice_pattern, remittance_info.upper())
            
            # Rule 2: Match by amount and customer
            customer_id = None
            if creditor_name:
                # Try to find customer by name
                customer_query = text("""
                    SELECT id FROM domain_erp.customers
                    WHERE tenant_id = :tenant_id 
                    AND (name ILIKE :name OR company_name ILIKE :name)
                    LIMIT 1
                """)
                customer_row = db.execute(
                    customer_query,
                    {"tenant_id": tenant_id, "name": f"%{creditor_name}%"}
                ).fetchone()
                if customer_row:
                    customer_id = str(customer_row[0])
            
            # Find matching open item
            op_query = text("""
                SELECT id, document_number, customer_id, customer_name, amount, amount as open_amount, due_date, currency, status
                FROM finance_open_items
                WHERE tenant_id = :tenant_id
                AND status IN ('open', 'partial')
                AND (
                    (:reference IS NOT NULL AND document_number ILIKE :reference_pattern)
                    OR (:customer_id IS NOT NULL AND customer_id = :customer_id AND ABS(amount - :amount) < 0.01)
                )
                ORDER BY 
                    CASE WHEN document_number ILIKE :reference_pattern THEN 1 ELSE 2 END,
                    ABS(amount - :amount) ASC
                LIMIT 5
            """)
            
            reference_pattern = f"%{invoice_match.group(0) if invoice_match else reference}%" if reference else None
            
            op_results = db.execute(
                op_query,
                {
                    "tenant_id": tenant_id,
                    "reference": reference,
                    "reference_pattern": reference_pattern,
                    "customer_id": customer_id,
                    "amount": amount
                }
            ).fetchall()
            
            if op_results:
                # Match to first (best) open item
                best_op = op_results[0]
                op_id = str(best_op[0])
                open_amount = Decimal(str(best_op[5]))
                
                # Calculate match
                matched_amount = min(amount, open_amount)
                remaining_amount = amount - matched_amount
                
                # Update bank statement line
                update_line = text("""
                    UPDATE domain_erp.bank_statement_lines
                    SET status = :status,
                        matched_op_id = :op_id
                    WHERE id = :line_id AND tenant_id = :tenant_id
                """)
                
                new_status = "MATCHED" if remaining_amount == 0 else "PARTIAL"
                db.execute(
                    update_line,
                    {
                        "status": new_status,
                        "op_id": op_id,
                        "line_id": line_id,
                        "tenant_id": tenant_id
                    }
                )
                
                # Update open item
                update_op = text("""
                    UPDATE finance_open_items
                    SET status = CASE WHEN (amount - :matched) <= 0.01 THEN 'closed' ELSE 'partial' END,
                        amount = amount - :matched
                    WHERE id = :op_id AND tenant_id = :tenant_id
                """)
                db.execute(
                    update_op,
                    {
                        "matched": matched_amount,
                        "op_id": op_id,
                        "tenant_id": tenant_id
                    }
                )
                
                match_results.append(MatchResult(
                    payment_id=line_id,
                    matched_op_id=op_id,
                    match_type="FULL" if remaining_amount == 0 else "PARTIAL",
                    matched_amount=matched_amount,
                    remaining_amount=remaining_amount,
                    confidence=0.9 if invoice_match else 0.7,
                    match_reason=f"Auto-matched by {'reference' if invoice_match else 'amount+customer'}"
                ))
        
        db.commit()
        logger.info(f"Auto-matched {len(match_results)} payments")
        return match_results
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in auto-match: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to auto-match: {str(e)}")


@router.get("/match-suggestions/{payment_id}", response_model=List[OpenItemMatch])
async def get_match_suggestions(
    payment_id: str,
    tenant_id: str = Query("default"),
    db: Session = Depends(get_db)
):
    """Get suggested open items for a payment."""
    try:
        # Get payment from bank statement lines
        payment_query = text("""
            SELECT amount, reference, remittance_info, creditor_name, debtor_name
            FROM domain_erp.bank_statement_lines
            WHERE id = :payment_id AND tenant_id = :tenant_id
        """)
        
        payment_row = db.execute(
            payment_query,
            {"payment_id": payment_id, "tenant_id": tenant_id}
        ).fetchone()
        
        if not payment_row:
            return []
        
        amount = Decimal(str(payment_row[0]))
        reference = payment_row[1]
        remittance_info = payment_row[2] or ""
        creditor_name = payment_row[3]
        debtor_name = payment_row[4]
        
        # Find customer ID
        customer_id = None
        if creditor_name:
            customer_query = text("""
                SELECT id FROM domain_erp.customers
                WHERE tenant_id = :tenant_id 
                AND (name ILIKE :name OR company_name ILIKE :name)
                LIMIT 1
            """)
            customer_row = db.execute(
                customer_query,
                {"tenant_id": tenant_id, "name": f"%{creditor_name}%"}
            ).fetchone()
            if customer_row:
                customer_id = str(customer_row[0])
        
        # Extract invoice number from reference/remittance
        import re
        invoice_pattern = r'(RE|INV|RE-?\d{4}-?\d+|\d{4}-\d+)'
        invoice_match = None
        if reference:
            invoice_match = re.search(invoice_pattern, reference.upper())
        if not invoice_match and remittance_info:
            invoice_match = re.search(invoice_pattern, remittance_info.upper())
        
        # Find matching open items
        op_query = text("""
            SELECT id, document_number, customer_id, customer_name, amount, amount as open_amount, due_date, currency, status
            FROM finance_open_items
            WHERE tenant_id = :tenant_id
            AND status IN ('open', 'partial')
            AND (
                (:reference_pattern IS NOT NULL AND document_number ILIKE :reference_pattern)
                OR (:customer_id IS NOT NULL AND customer_id = :customer_id AND ABS(amount - :amount) < 10.00)
            )
            ORDER BY 
                CASE WHEN document_number ILIKE :reference_pattern THEN 1 ELSE 2 END,
                ABS(amount - :amount) ASC,
                due_date ASC
            LIMIT 10
        """)
        
        reference_pattern = f"%{invoice_match.group(0) if invoice_match else reference}%" if (invoice_match or reference) else None
        
        op_results = db.execute(
            op_query,
            {
                "tenant_id": tenant_id,
                "reference_pattern": reference_pattern,
                "customer_id": customer_id,
                "amount": amount
            }
        ).fetchall()
        
        return [
            OpenItemMatch(
                op_id=str(r[0]),
                document_number=str(r[1]),
                customer_id=str(r[2]),
                customer_name=str(r[3]),
                amount=Decimal(str(r[4])),
                open_amount=Decimal(str(r[5])),
                due_date=r[6],
                currency=str(r[7]),
                status=str(r[8])
            )
            for r in op_results
        ]
        
    except Exception as e:
        logger.error(f"Error getting match suggestions: {e}")
        # Return empty list if error (table may not exist)
        return []

