"""
Open Items (OP) management endpoints
RESTful API for open items settlement and matching
FIBU-AR-05: OP-Verwaltung Ausgleich/Verrechnung
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime
import json
import logging

from ....core.database import get_db
from ..schemas.base import PaginatedResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/open-items", tags=["finance", "open-items"])


class OpenItemSettlement(BaseModel):
    """Schema for open item settlement"""
    op_id: str
    payment_amount: Decimal
    payment_date: datetime
    payment_reference: Optional[str] = None
    payment_type: str = "payment"  # payment, discount, credit_note, reversal
    notes: Optional[str] = None


class SettlementResult(BaseModel):
    """Result of settlement operation"""
    op_id: str
    settlement_id: str
    previous_open_amount: Decimal
    settlement_amount: Decimal
    new_open_amount: Decimal
    status: str  # settled, partial, overpaid
    settlement_date: datetime
    audit_trail_id: Optional[str] = None


@router.post("/{op_id}/settle", response_model=SettlementResult)
async def settle_open_item(
    op_id: str,
    settlement: OpenItemSettlement,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Settle an open item with a payment.
    Creates audit trail entry for GoBD compliance.
    """
    try:
        # Get current open item from offene_posten table
        op_query = text("""
            SELECT id, tenant_id, rechnungsnr, datum, faelligkeit, betrag, offen, 
                   kunde_id, kunde_name, mahn_stufe, zahlbar
            FROM offene_posten
            WHERE id = :op_id AND tenant_id = :tenant_id
        """)
        
        op_row = db.execute(op_query, {"op_id": op_id, "tenant_id": tenant_id}).fetchone()
        
        if not op_row:
            raise HTTPException(status_code=404, detail="Open item not found")
        
        current_open_amount = Decimal(str(op_row[6])) if op_row[6] else Decimal("0.00")
        # op_row indices: 0=id, 1=tenant_id, 2=rechnungsnr, 3=datum, 4=faelligkeit, 5=betrag, 6=offen
        settlement_amount = Decimal(str(settlement.payment_amount))
        
        if settlement_amount <= 0:
            raise HTTPException(status_code=400, detail="Settlement amount must be positive")
        
        if settlement_amount > current_open_amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Settlement amount ({settlement_amount}) exceeds open amount ({current_open_amount})"
            )
        
        # Calculate new open amount
        new_open_amount = current_open_amount - settlement_amount
        
        # Determine new status
        if new_open_amount <= Decimal("0.01"):
            new_status = "settled"
            new_open_amount = Decimal("0.00")
        else:
            new_status = "partial"
        
        # Create settlement record
        settlement_id = f"SET-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        # Update open item in offene_posten table
        update_query = text("""
            UPDATE offene_posten
            SET offen = :new_open_amount,
                updated_at = NOW()
            WHERE id = :op_id
            RETURNING id
        """)
        
        db.execute(update_query, {
            "op_id": op_id,
            "new_open_amount": new_open_amount,
            "new_status": new_status,
            "payment_date": settlement.payment_date
        })
        
        # Create payment record (store in journal_entries as reference)
        # Note: In production, create a separate open_item_payments table
        # For now, we'll store payment info in the journal entry description
        
        # Create audit trail entry (GoBD compliance)
        # Store in infrastructure.audit_log if available
        audit_trail_id = f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        try:
            audit_insert = text("""
                INSERT INTO infrastructure.audit_log
                (id, user_id, action, entity_type, entity_id, changes, created_at)
                VALUES (:id, :user_id, :action, :entity_type, :entity_id, :changes::jsonb, NOW())
                RETURNING id
            """)
            
            changes = {
                "previous_open_amount": float(current_open_amount),
                "settlement_amount": float(settlement_amount),
                "new_open_amount": float(new_open_amount),
                "payment_reference": settlement.payment_reference,
                "payment_type": settlement.payment_type
            }
            
            db.execute(audit_insert, {
                "id": audit_trail_id,
                "user_id": None,  # TODO: Get from context
                "action": "settle_open_item",
                "entity_type": "offener_posten",
                "entity_id": op_id,
                "changes": json.dumps(changes)
            })
        except Exception:
            # If audit_log table doesn't exist, continue without audit trail
            audit_trail_id = None
        
        # Create GL journal entry for the payment
        # This ensures proper accounting
        journal_entry_id = f"JE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        # Debit: Bank account (or cash)
        # Credit: Accounts Receivable (Debitoren)
        journal_insert = text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, description, 
             source, currency, status, total_debit, total_credit, created_at, updated_at)
            VALUES (:id, :tenant_id, :entry_number, :entry_date, :posting_date, :description,
                    :source, :currency, :status, :total_debit, :total_credit, NOW(), NOW())
            RETURNING id
        """)
        
        entry_number = f"OP-SETTLE-{datetime.now().strftime('%Y%m%d')}-{op_id[:8]}"
        description = f"OP-Ausgleich {op_row[2]} - {settlement.payment_reference or 'Zahlung'}"
        
        db.execute(journal_insert, {
            "id": journal_entry_id,
            "tenant_id": tenant_id,
            "entry_number": entry_number,
            "entry_date": settlement.payment_date,
            "posting_date": settlement.payment_date,
            "description": description,
            "source": "op_settlement",
            "currency": "EUR",  # Default currency
            "status": "posted",
            "total_debit": settlement_amount,
            "total_credit": settlement_amount
        })
        
        # Create journal entry lines
        # Line 1: Debit Bank/Cash
        bank_account = "1000"  # Default bank account - TODO: Get from settlement
        journal_line1 = text("""
            INSERT INTO domain_erp.journal_entry_lines
            (id, tenant_id, journal_entry_id, account_id, debit_amount, credit_amount,
             line_number, description, created_at, updated_at)
            VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit_amount, :credit_amount,
                    :line_number, :description, NOW(), NOW())
        """)
        
        db.execute(journal_line1, {
            "id": f"{journal_entry_id}-L1",
            "tenant_id": tenant_id,
            "journal_entry_id": journal_entry_id,
            "account_id": bank_account,
            "debit_amount": settlement_amount,
            "credit_amount": Decimal("0.00"),
            "line_number": 1,
            "description": f"Zahlungseingang {settlement.payment_reference or ''}"
        })
        
        # Line 2: Credit Accounts Receivable
        ar_account = "1200"  # Forderungen aus Lieferungen und Leistungen
        journal_line2 = text("""
            INSERT INTO domain_erp.journal_entry_lines
            (id, tenant_id, journal_entry_id, account_id, debit_amount, credit_amount,
             line_number, description, created_at, updated_at)
            VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit_amount, :credit_amount,
                    :line_number, :description, NOW(), NOW())
        """)
        
        db.execute(journal_line2, {
            "id": f"{journal_entry_id}-L2",
            "tenant_id": tenant_id,
            "journal_entry_id": journal_entry_id,
            "account_id": ar_account,
            "debit_amount": Decimal("0.00"),
            "credit_amount": settlement_amount,
            "line_number": 2,
            "description": f"OP-Ausgleich {op_row[3]}"
        })
        
        db.commit()
        
        return SettlementResult(
            op_id=op_id,
            settlement_id=settlement_id,
            previous_open_amount=current_open_amount,
            settlement_amount=settlement_amount,
            new_open_amount=new_open_amount,
            status=new_status,
            settlement_date=settlement.payment_date,
            audit_trail_id=audit_trail_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to settle open item: {str(e)}")


@router.get("/{op_id}/settlements", response_model=List[dict])
async def get_settlements(
    op_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get all settlements for an open item (audit trail).
    """
    try:
        # Get settlements from journal entries related to this OP
        query = text("""
            SELECT id, entry_number, entry_date, description, total_debit, created_at
            FROM domain_erp.journal_entries
            WHERE description LIKE :op_pattern 
            AND source = 'op_settlement'
            AND tenant_id = :tenant_id
            ORDER BY entry_date DESC, created_at DESC
        """)
        
        op_pattern = f"%{op_id}%"
        rows = db.execute(query, {"op_id": op_id, "tenant_id": tenant_id, "op_pattern": op_pattern}).fetchall()
        
        return [
            {
                "id": str(row[0]),
                "payment_amount": float(row[4]) if row[4] else 0.0,
                "payment_date": row[2].isoformat() if row[2] else None,
                "payment_reference": row[1],  # Use entry_number as reference
                "payment_type": "payment",
                "notes": row[3],  # Use description as notes
                "created_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
    except Exception as e:
        # If table doesn't exist, return empty list
        return []


@router.post("/{op_id}/reverse-settlement", response_model=dict)
async def reverse_settlement(
    op_id: str,
    settlement_id: str,
    reason: str = Query(..., min_length=10, description="Reason for reversal (min 10 chars)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Reverse a settlement (Storno).
    Requires reason for GoBD compliance.
    """
    try:
        # Get settlement from journal entry
        settlement_query = text("""
            SELECT id, total_debit, entry_date
            FROM domain_erp.journal_entries
            WHERE id = :settlement_id AND tenant_id = :tenant_id
            AND source = 'op_settlement'
        """)
        
        settlement_row = db.execute(settlement_query, {
            "settlement_id": settlement_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not settlement_row:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        settlement_amount = Decimal(str(settlement_row[1]))
        
        # Get current open item
        op_query = text("""
            SELECT id, offen
            FROM offene_posten
            WHERE id = :op_id AND tenant_id = :tenant_id
        """)
        
        op_row = db.execute(op_query, {"op_id": op_id, "tenant_id": tenant_id}).fetchone()
        
        if not op_row:
            raise HTTPException(status_code=404, detail="Open item not found")
        
        current_open_amount = Decimal(str(op_row[1])) if op_row[1] else Decimal("0.00")
        new_open_amount = current_open_amount + settlement_amount
        
        # Update open item
        update_query = text("""
            UPDATE offene_posten
            SET offen = :new_open_amount,
                updated_at = NOW()
            WHERE id = :op_id
        """)
        
        db.execute(update_query, {
            "op_id": op_id,
            "new_open_amount": new_open_amount
        })
        
        # Mark journal entry as reversed
        reverse_query = text("""
            UPDATE domain_erp.journal_entries
            SET status = 'cancelled',
                description = description || E'\\nSTORNIERT: ' || :reason,
                updated_at = NOW()
            WHERE id = :settlement_id
        """)
        
        db.execute(reverse_query, {
            "settlement_id": settlement_id,
            "reason": reason
        })
        
        # Create audit trail entry
        audit_trail_id = f"AUDIT-REV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        try:
            audit_insert = text("""
                INSERT INTO infrastructure.audit_log
                (id, user_id, action, entity_type, entity_id, changes, created_at)
                VALUES (:id, :user_id, :action, :entity_type, :entity_id, :changes::jsonb, NOW())
            """)
            
            changes = {
                "settlement_id": settlement_id,
                "reversed_amount": float(settlement_amount),
                "previous_open_amount": float(current_open_amount),
                "new_open_amount": float(new_open_amount),
                "reason": reason
            }
            
            db.execute(audit_insert, {
                "id": audit_trail_id,
                "user_id": None,  # TODO: Get from context
                "action": "reverse_settlement",
                "entity_type": "offener_posten",
                "entity_id": op_id,
                "changes": json.dumps(changes)
            })
        except Exception:
            # If audit_log table doesn't exist, continue without audit trail
            audit_trail_id = None
        
        db.commit()
        
        return {
            "success": True,
            "message": "Settlement reversed successfully",
            "settlement_id": settlement_id,
            "audit_trail_id": audit_trail_id,
            "new_open_amount": float(new_open_amount)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reverse settlement: {str(e)}")

