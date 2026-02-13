"""
Bank Reconciliation API
FIBU-BNK-04: Bankabstimmung Saldoabgleich
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel
import logging

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bank-reconciliation", tags=["finance", "bank-reconciliation"])


class BalanceComparison(BaseModel):
    """Balance comparison between bank statement and accounting"""
    bank_statement_balance: Decimal
    accounting_balance: Decimal
    difference: Decimal
    is_balanced: bool
    statement_date: date
    comparison_date: date


class DifferenceItem(BaseModel):
    """Single difference between bank and accounting"""
    item_type: str  # UNMATCHED_STATEMENT, UNMATCHED_ACCOUNTING, AMOUNT_MISMATCH
    statement_line_id: Optional[str] = None
    journal_entry_id: Optional[str] = None
    date: date
    amount: Decimal
    bank_amount: Optional[Decimal] = None
    accounting_amount: Optional[Decimal] = None
    reference: Optional[str] = None
    description: str
    suggested_account: Optional[str] = None
    suggested_action: Optional[str] = None  # CREATE_ENTRY, ADJUST_ENTRY, INVESTIGATE


class ReconciliationResult(BaseModel):
    """Result of bank reconciliation"""
    statement_id: str
    bank_account_id: str
    balance_comparison: BalanceComparison
    differences: List[DifferenceItem]
    total_differences: int
    can_be_booked: bool
    booking_suggestions: Optional[List[dict]] = None


@router.get("/{statement_id}/balance-comparison", response_model=BalanceComparison)
async def get_balance_comparison(
    statement_id: str,
    bank_account_id: str = Query(..., description="Bank account ID"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Compare bank statement balance with accounting balance.
    """
    try:
        # Get bank statement balance
        statement_query = text("""
            SELECT opening_balance, closing_balance, statement_date
            FROM domain_erp.bank_statements
            WHERE id = :statement_id AND tenant_id = :tenant_id
        """)
        
        statement_row = db.execute(statement_query, {
            "statement_id": statement_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not statement_row:
            raise HTTPException(status_code=404, detail="Bank statement not found")
        
        bank_statement_balance = Decimal(str(statement_row[1])) if statement_row[1] else Decimal("0.00")
        statement_date = statement_row[2] if statement_row[2] else date.today()
        
        # Get accounting balance for bank account
        # Sum all journal entries for this bank account
        accounting_query = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) as total_debit,
                COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) as total_credit
            FROM domain_erp.journal_entry_lines jel
            JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            JOIN domain_erp.chart_of_accounts coa ON jel.account_id = coa.id
            JOIN domain_erp.bank_accounts ba ON coa.account_number = ba.account_number
            WHERE ba.id = :bank_account_id 
            AND ba.tenant_id = :tenant_id
            AND je.status = 'posted'
            AND je.entry_date <= :statement_date
        """)
        
        accounting_row = db.execute(accounting_query, {
            "bank_account_id": bank_account_id,
            "tenant_id": tenant_id,
            "statement_date": statement_date
        }).fetchone()
        
        if not accounting_row:
            # If no journal entries, try to get balance from bank_accounts table
            bank_account_query = text("""
                SELECT balance FROM domain_erp.bank_accounts
                WHERE id = :bank_account_id AND tenant_id = :tenant_id
            """)
            bank_account_row = db.execute(bank_account_query, {
                "bank_account_id": bank_account_id,
                "tenant_id": tenant_id
            }).fetchone()
            
            if bank_account_row:
                accounting_balance = Decimal(str(bank_account_row[0])) if bank_account_row[0] else Decimal("0.00")
            else:
                accounting_balance = Decimal("0.00")
        else:
            total_debit = Decimal(str(accounting_row[0])) if accounting_row[0] else Decimal("0.00")
            total_credit = Decimal(str(accounting_row[1])) if accounting_row[1] else Decimal("0.00")
            # For asset accounts (bank), balance = debit - credit
            accounting_balance = total_debit - total_credit
        
        difference = bank_statement_balance - accounting_balance
        is_balanced = abs(difference) < Decimal("0.01")
        
        return BalanceComparison(
            bank_statement_balance=bank_statement_balance,
            accounting_balance=accounting_balance,
            difference=difference,
            is_balanced=is_balanced,
            statement_date=statement_date,
            comparison_date=date.today()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing balances: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare balances: {str(e)}")


@router.get("/{statement_id}/differences", response_model=List[DifferenceItem])
async def get_reconciliation_differences(
    statement_id: str,
    bank_account_id: str = Query(..., description="Bank account ID"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get list of differences between bank statement and accounting records.
    """
    try:
        differences = []
        
        # Get unmatched statement lines
        unmatched_statement_query = text("""
            SELECT id, booking_date, amount, reference, remittance_info
            FROM domain_erp.bank_statement_lines
            WHERE statement_id = :statement_id 
            AND tenant_id = :tenant_id
            AND status = 'UNMATCHED'
            ORDER BY booking_date
        """)
        
        unmatched_statement_rows = db.execute(unmatched_statement_query, {
            "statement_id": statement_id,
            "tenant_id": tenant_id
        }).fetchall()
        
        for row in unmatched_statement_rows:
            differences.append(DifferenceItem(
                item_type="UNMATCHED_STATEMENT",
                statement_line_id=str(row[0]),
                date=row[1],
                amount=Decimal(str(row[2])),
                bank_amount=Decimal(str(row[2])),
                reference=row[3],
                description=row[4] or row[3] or "Unmatched bank transaction",
                suggested_account="1200",  # Default: Accounts Receivable
                suggested_action="CREATE_ENTRY"
            ))
        
        # Get accounting entries that might not be in bank statement
        # This is more complex - we'd need to match by date/amount
        # For now, we'll focus on unmatched statement lines
        
        return differences
        
    except Exception as e:
        logger.error(f"Error getting differences: {e}")
        return []


@router.post("/{statement_id}/reconcile", response_model=ReconciliationResult)
async def reconcile_bank_statement(
    statement_id: str,
    bank_account_id: str = Query(..., description="Bank account ID"),
    tenant_id: str = Query("system", description="Tenant ID"),
    auto_book: bool = Query(False, description="Automatically book differences"),
    db: Session = Depends(get_db)
):
    """
    Perform bank reconciliation and generate booking suggestions.
    """
    try:
        # Get balance comparison
        balance_comp = await get_balance_comparison(statement_id, bank_account_id, tenant_id, db)
        
        # Get differences
        differences = await get_reconciliation_differences(statement_id, bank_account_id, tenant_id, db)
        
        # Generate booking suggestions for unmatched items
        booking_suggestions = []
        
        for diff in differences:
            if diff.item_type == "UNMATCHED_STATEMENT" and diff.suggested_action == "CREATE_ENTRY":
                # Suggest journal entry for unmatched bank transaction
                suggestion = {
                    "type": "journal_entry",
                    "description": diff.description,
                    "date": diff.date.isoformat(),
                    "account_debit": "1000",  # Bank account
                    "account_credit": diff.suggested_account or "1200",  # Default AR
                    "amount": float(diff.amount),
                    "reference": diff.reference,
                    "statement_line_id": diff.statement_line_id
                }
                booking_suggestions.append(suggestion)
        
        can_be_booked = balance_comp.is_balanced or len(differences) == 0
        
        # Auto-book if requested and balanced
        if auto_book and can_be_booked and booking_suggestions:
            for suggestion in booking_suggestions:
                try:
                    # Create journal entry
                    journal_entry_id = f"JE-RECON-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    
                    journal_insert = text("""
                        INSERT INTO domain_erp.journal_entries
                        (id, tenant_id, entry_number, entry_date, posting_date, description,
                         source, currency, status, total_debit, total_credit, created_at, updated_at)
                        VALUES (:id, :tenant_id, :entry_number, :entry_date, :posting_date, :description,
                                :source, :currency, :status, :total_debit, :total_credit, NOW(), NOW())
                        RETURNING id
                    """)
                    
                    entry_date = datetime.strptime(suggestion["date"], '%Y-%m-%d').date()
                    entry_number = f"BANK-RECON-{entry_date.strftime('%Y%m%d')}"
                    
                    db.execute(journal_insert, {
                        "id": journal_entry_id,
                        "tenant_id": tenant_id,
                        "entry_number": entry_number,
                        "entry_date": entry_date,
                        "posting_date": entry_date,
                        "description": suggestion["description"],
                        "source": "bank_reconciliation",
                        "currency": "EUR",
                        "status": "posted",
                        "total_debit": Decimal(str(suggestion["amount"])),
                        "total_credit": Decimal(str(suggestion["amount"]))
                    })
                    
                    # Create journal entry lines
                    # Debit: Bank account
                    bank_account_query = text("""
                        SELECT id FROM domain_erp.chart_of_accounts
                        WHERE account_number = :account_number AND tenant_id = :tenant_id
                        LIMIT 1
                    """)
                    bank_account_row = db.execute(bank_account_query, {
                        "account_number": suggestion["account_debit"],
                        "tenant_id": tenant_id
                    }).fetchone()
                    
                    if bank_account_row:
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
                            "account_id": str(bank_account_row[0]),
                            "debit_amount": Decimal(str(suggestion["amount"])),
                            "credit_amount": Decimal("0.00"),
                            "line_number": 1,
                            "description": suggestion["description"]
                        })
                    
                    # Credit: Suggested account
                    credit_account_row = db.execute(bank_account_query, {
                        "account_number": suggestion["account_credit"],
                        "tenant_id": tenant_id
                    }).fetchone()
                    
                    if credit_account_row:
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
                            "account_id": str(credit_account_row[0]),
                            "debit_amount": Decimal("0.00"),
                            "credit_amount": Decimal(str(suggestion["amount"])),
                            "line_number": 2,
                            "description": suggestion["description"]
                        })
                    
                    # Mark statement line as matched
                    if suggestion.get("statement_line_id"):
                        update_line = text("""
                            UPDATE domain_erp.bank_statement_lines
                            SET status = 'MATCHED', updated_at = NOW()
                            WHERE id = :line_id AND tenant_id = :tenant_id
                        """)
                        
                        db.execute(update_line, {
                            "line_id": suggestion["statement_line_id"],
                            "tenant_id": tenant_id
                        })
                    
                except Exception as e:
                    logger.error(f"Error creating journal entry for suggestion: {e}")
                    continue
            
            db.commit()
        
        return ReconciliationResult(
            statement_id=statement_id,
            bank_account_id=bank_account_id,
            balance_comparison=balance_comp,
            differences=differences,
            total_differences=len(differences),
            can_be_booked=can_be_booked,
            booking_suggestions=booking_suggestions if not auto_book else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error reconciling bank statement: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reconcile: {str(e)}")


@router.get("/{statement_id}/summary", response_model=dict)
async def get_reconciliation_summary(
    statement_id: str,
    bank_account_id: str = Query(..., description="Bank account ID"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get summary of bank reconciliation status.
    """
    try:
        # Get balance comparison
        balance_comp = await get_balance_comparison(statement_id, bank_account_id, tenant_id, db)
        
        # Get differences count
        differences = await get_reconciliation_differences(statement_id, bank_account_id, tenant_id, db)
        
        # Get statement line counts
        line_counts_query = text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'MATCHED' THEN 1 ELSE 0 END) as matched,
                SUM(CASE WHEN status = 'UNMATCHED' THEN 1 ELSE 0 END) as unmatched
            FROM domain_erp.bank_statement_lines
            WHERE statement_id = :statement_id AND tenant_id = :tenant_id
        """)
        
        line_counts_row = db.execute(line_counts_query, {
            "statement_id": statement_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        total_lines = line_counts_row[0] if line_counts_row else 0
        matched_lines = line_counts_row[1] if line_counts_row else 0
        unmatched_lines = line_counts_row[2] if line_counts_row else 0
        
        return {
            "statement_id": statement_id,
            "bank_account_id": bank_account_id,
            "balance_comparison": {
                "bank_balance": float(balance_comp.bank_statement_balance),
                "accounting_balance": float(balance_comp.accounting_balance),
                "difference": float(balance_comp.difference),
                "is_balanced": balance_comp.is_balanced
            },
            "line_counts": {
                "total": total_lines,
                "matched": matched_lines,
                "unmatched": unmatched_lines
            },
            "differences_count": len(differences),
            "can_be_booked": balance_comp.is_balanced and unmatched_lines == 0
        }
        
    except Exception as e:
        logger.error(f"Error getting reconciliation summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

