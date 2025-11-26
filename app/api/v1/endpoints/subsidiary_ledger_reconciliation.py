"""
Subsidiary Ledger Reconciliation API
FIBU-CLS-02: Nebenbuch-Abstimmung implementieren
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel
import logging

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subsidiary-ledger-reconciliation", tags=["finance", "reconciliation"])


class ReconciliationEntry(BaseModel):
    """Single reconciliation entry"""
    account_number: str
    account_name: str
    subsidiary_balance: Decimal
    general_ledger_balance: Decimal
    difference: Decimal
    is_balanced: bool
    entry_count: int
    unmatched_entries: int


class ReconciliationDetail(BaseModel):
    """Detail entry for drilldown"""
    entry_id: str
    entry_number: str
    entry_date: date
    amount: Decimal
    description: str
    source: str
    status: str
    matched: bool


class ReconciliationResult(BaseModel):
    """Result of subsidiary ledger reconciliation"""
    ledger_type: str  # AR, AP, BANK, FA
    period: str
    reconciliation_date: date
    total_accounts: int
    balanced_accounts: int
    unbalanced_accounts: int
    total_difference: Decimal
    entries: List[ReconciliationEntry]
    details: Optional[List[ReconciliationDetail]] = None


@router.get("/ar", response_model=ReconciliationResult)
async def reconcile_ar(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Reconcile Accounts Receivable (Debitoren) with General Ledger.
    """
    try:
        # Get AR account (typically 1400)
        ar_account_query = text("""
            SELECT id, account_number, name
            FROM domain_erp.chart_of_accounts
            WHERE account_number LIKE '14%' 
            AND account_type = 'ASSET'
            AND tenant_id = :tenant_id
            ORDER BY account_number
            LIMIT 1
        """)
        
        ar_account = db.execute(ar_account_query, {"tenant_id": tenant_id}).fetchone()
        
        if not ar_account:
            # Return mock data if no AR account found
            return ReconciliationResult(
                ledger_type="AR",
                period=period,
                reconciliation_date=date.today(),
                total_accounts=0,
                balanced_accounts=0,
                unbalanced_accounts=0,
                total_difference=Decimal("0.00"),
                entries=[]
            )
        
        ar_account_id = str(ar_account[0])
        ar_account_number = str(ar_account[1])
        ar_account_name = str(ar_account[2])
        
        # Get GL balance for AR account
        gl_balance_query = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) as total_debit,
                COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) as total_credit
            FROM domain_erp.journal_entry_lines jel
            JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE jel.account_id = :account_id
            AND je.tenant_id = :tenant_id
            AND je.status = 'posted'
            AND TO_CHAR(je.entry_date, 'YYYY-MM') = :period
        """)
        
        gl_row = db.execute(gl_balance_query, {
            "account_id": ar_account_id,
            "tenant_id": tenant_id,
            "period": period
        }).fetchone()
        
        gl_debit = Decimal(str(gl_row[0])) if gl_row and gl_row[0] else Decimal("0.00")
        gl_credit = Decimal(str(gl_row[1])) if gl_row and gl_row[1] else Decimal("0.00")
        gl_balance = gl_debit - gl_credit
        
        # Get AR subsidiary ledger balance (from offene_posten)
        ar_balance_query = text("""
            SELECT 
                COALESCE(SUM(open_amount), 0) as total_open
            FROM domain_erp.offene_posten
            WHERE tenant_id = :tenant_id
            AND debtor_id IS NOT NULL
            AND TO_CHAR(booking_date, 'YYYY-MM') <= :period
        """)
        
        ar_row = db.execute(ar_balance_query, {
            "tenant_id": tenant_id,
            "period": period
        }).fetchone()
        
        ar_balance = Decimal(str(ar_row[0])) if ar_row and ar_row[0] else Decimal("0.00")
        
        # Count entries
        entry_count_query = text("""
            SELECT COUNT(*)
            FROM domain_erp.offene_posten
            WHERE tenant_id = :tenant_id
            AND debtor_id IS NOT NULL
            AND TO_CHAR(booking_date, 'YYYY-MM') <= :period
        """)
        
        entry_count = db.execute(entry_count_query, {
            "tenant_id": tenant_id,
            "period": period
        }).scalar() or 0
        
        difference = ar_balance - gl_balance
        is_balanced = abs(difference) < Decimal("0.01")
        
        entries = [ReconciliationEntry(
            account_number=ar_account_number,
            account_name=ar_account_name,
            subsidiary_balance=ar_balance,
            general_ledger_balance=gl_balance,
            difference=difference,
            is_balanced=is_balanced,
            entry_count=entry_count,
            unmatched_entries=0
        )]
        
        return ReconciliationResult(
            ledger_type="AR",
            period=period,
            reconciliation_date=date.today(),
            total_accounts=1,
            balanced_accounts=1 if is_balanced else 0,
            unbalanced_accounts=0 if is_balanced else 1,
            total_difference=difference,
            entries=entries
        )
        
    except Exception as e:
        logger.error(f"Error reconciling AR: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reconcile AR: {str(e)}")


@router.get("/ap", response_model=ReconciliationResult)
async def reconcile_ap(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Reconcile Accounts Payable (Kreditoren) with General Ledger.
    """
    try:
        # Get AP account (typically 4400)
        ap_account_query = text("""
            SELECT id, account_number, name
            FROM domain_erp.chart_of_accounts
            WHERE account_number LIKE '44%' 
            AND account_type = 'LIABILITY'
            AND tenant_id = :tenant_id
            ORDER BY account_number
            LIMIT 1
        """)
        
        ap_account = db.execute(ap_account_query, {"tenant_id": tenant_id}).fetchone()
        
        if not ap_account:
            return ReconciliationResult(
                ledger_type="AP",
                period=period,
                reconciliation_date=date.today(),
                total_accounts=0,
                balanced_accounts=0,
                unbalanced_accounts=0,
                total_difference=Decimal("0.00"),
                entries=[]
            )
        
        ap_account_id = str(ap_account[0])
        ap_account_number = str(ap_account[1])
        ap_account_name = str(ap_account[2])
        
        # Get GL balance for AP account
        gl_balance_query = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) as total_debit,
                COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) as total_credit
            FROM domain_erp.journal_entry_lines jel
            JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE jel.account_id = :account_id
            AND je.tenant_id = :tenant_id
            AND je.status = 'posted'
            AND TO_CHAR(je.entry_date, 'YYYY-MM') = :period
        """)
        
        gl_row = db.execute(gl_balance_query, {
            "account_id": ap_account_id,
            "tenant_id": tenant_id,
            "period": period
        }).fetchone()
        
        gl_debit = Decimal(str(gl_row[0])) if gl_row and gl_row[0] else Decimal("0.00")
        gl_credit = Decimal(str(gl_row[1])) if gl_row and gl_row[1] else Decimal("0.00")
        # For liabilities, balance = credit - debit
        gl_balance = gl_credit - gl_debit
        
        # Get AP subsidiary ledger balance (from offene_posten)
        ap_balance_query = text("""
            SELECT 
                COALESCE(SUM(open_amount), 0) as total_open
            FROM domain_erp.offene_posten
            WHERE tenant_id = :tenant_id
            AND creditor_id IS NOT NULL
            AND TO_CHAR(booking_date, 'YYYY-MM') <= :period
        """)
        
        ap_row = db.execute(ap_balance_query, {
            "tenant_id": tenant_id,
            "period": period
        }).fetchone()
        
        ap_balance = Decimal(str(ap_row[0])) if ap_row and ap_row[0] else Decimal("0.00")
        
        # Count entries
        entry_count_query = text("""
            SELECT COUNT(*)
            FROM domain_erp.offene_posten
            WHERE tenant_id = :tenant_id
            AND creditor_id IS NOT NULL
            AND TO_CHAR(booking_date, 'YYYY-MM') <= :period
        """)
        
        entry_count = db.execute(entry_count_query, {
            "tenant_id": tenant_id,
            "period": period
        }).scalar() or 0
        
        difference = ap_balance - gl_balance
        is_balanced = abs(difference) < Decimal("0.01")
        
        entries = [ReconciliationEntry(
            account_number=ap_account_number,
            account_name=ap_account_name,
            subsidiary_balance=ap_balance,
            general_ledger_balance=gl_balance,
            difference=difference,
            is_balanced=is_balanced,
            entry_count=entry_count,
            unmatched_entries=0
        )]
        
        return ReconciliationResult(
            ledger_type="AP",
            period=period,
            reconciliation_date=date.today(),
            total_accounts=1,
            balanced_accounts=1 if is_balanced else 0,
            unbalanced_accounts=0 if is_balanced else 1,
            total_difference=difference,
            entries=entries
        )
        
    except Exception as e:
        logger.error(f"Error reconciling AP: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reconcile AP: {str(e)}")


@router.get("/bank", response_model=ReconciliationResult)
async def reconcile_bank(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Reconcile Bank accounts with General Ledger.
    """
    try:
        # Get all bank accounts
        bank_accounts_query = text("""
            SELECT ba.id, ba.account_number, coa.name, ba.balance
            FROM domain_erp.bank_accounts ba
            JOIN domain_erp.chart_of_accounts coa ON ba.account_number = coa.account_number
            WHERE ba.tenant_id = :tenant_id
            AND coa.tenant_id = :tenant_id
        """)
        
        bank_accounts = db.execute(bank_accounts_query, {"tenant_id": tenant_id}).fetchall()
        
        if not bank_accounts:
            return ReconciliationResult(
                ledger_type="BANK",
                period=period,
                reconciliation_date=date.today(),
                total_accounts=0,
                balanced_accounts=0,
                unbalanced_accounts=0,
                total_difference=Decimal("0.00"),
                entries=[]
            )
        
        entries = []
        total_difference = Decimal("0.00")
        balanced_count = 0
        
        for bank_account in bank_accounts:
            bank_account_id = str(bank_account[0])
            account_number = str(bank_account[1])
            account_name = str(bank_account[2])
            bank_balance = Decimal(str(bank_account[3])) if bank_account[3] else Decimal("0.00")
            
            # Get GL balance for bank account
            gl_balance_query = text("""
                SELECT 
                    COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) as total_debit,
                    COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) as total_credit
                FROM domain_erp.journal_entry_lines jel
                JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
                JOIN domain_erp.chart_of_accounts coa ON jel.account_id = coa.id
                WHERE coa.account_number = :account_number
                AND je.tenant_id = :tenant_id
                AND je.status = 'posted'
                AND TO_CHAR(je.entry_date, 'YYYY-MM') = :period
            """)
            
            gl_row = db.execute(gl_balance_query, {
                "account_number": account_number,
                "tenant_id": tenant_id,
                "period": period
            }).fetchone()
            
            gl_debit = Decimal(str(gl_row[0])) if gl_row and gl_row[0] else Decimal("0.00")
            gl_credit = Decimal(str(gl_row[1])) if gl_row and gl_row[1] else Decimal("0.00")
            gl_balance = gl_debit - gl_credit
            
            difference = bank_balance - gl_balance
            is_balanced = abs(difference) < Decimal("0.01")
            
            if is_balanced:
                balanced_count += 1
            
            total_difference += abs(difference)
            
            entries.append(ReconciliationEntry(
                account_number=account_number,
                account_name=account_name,
                subsidiary_balance=bank_balance,
                general_ledger_balance=gl_balance,
                difference=difference,
                is_balanced=is_balanced,
                entry_count=0,
                unmatched_entries=0
            ))
        
        return ReconciliationResult(
            ledger_type="BANK",
            period=period,
            reconciliation_date=date.today(),
            total_accounts=len(entries),
            balanced_accounts=balanced_count,
            unbalanced_accounts=len(entries) - balanced_count,
            total_difference=total_difference,
            entries=entries
        )
        
    except Exception as e:
        logger.error(f"Error reconciling Bank: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reconcile Bank: {str(e)}")


@router.get("/{ledger_type}/details", response_model=List[ReconciliationDetail])
async def get_reconciliation_details(
    ledger_type: str,
    account_number: str = Query(..., description="Account number"),
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get detailed entries for drilldown into differences.
    """
    try:
        details = []
        
        if ledger_type == "AR":
            # Get AR entries from offene_posten
            query = text("""
                SELECT id, op_number, booking_date, open_amount, description, 'op' as source, 'open' as status
                FROM domain_erp.offene_posten
                WHERE tenant_id = :tenant_id
                AND debtor_id IS NOT NULL
                AND TO_CHAR(booking_date, 'YYYY-MM') <= :period
                ORDER BY booking_date DESC
            """)
            
            rows = db.execute(query, {
                "tenant_id": tenant_id,
                "period": period
            }).fetchall()
            
            for row in rows:
                details.append(ReconciliationDetail(
                    entry_id=str(row[0]),
                    entry_number=str(row[1]) if row[1] else "",
                    entry_date=row[2],
                    amount=Decimal(str(row[3])) if row[3] else Decimal("0.00"),
                    description=str(row[4]) if row[4] else "",
                    source="AR",
                    status=str(row[6]),
                    matched=True
                ))
        
        elif ledger_type == "AP":
            # Get AP entries from offene_posten
            query = text("""
                SELECT id, op_number, booking_date, open_amount, description, 'op' as source, 'open' as status
                FROM domain_erp.offene_posten
                WHERE tenant_id = :tenant_id
                AND creditor_id IS NOT NULL
                AND TO_CHAR(booking_date, 'YYYY-MM') <= :period
                ORDER BY booking_date DESC
            """)
            
            rows = db.execute(query, {
                "tenant_id": tenant_id,
                "period": period
            }).fetchall()
            
            for row in rows:
                details.append(ReconciliationDetail(
                    entry_id=str(row[0]),
                    entry_number=str(row[1]) if row[1] else "",
                    entry_date=row[2],
                    amount=Decimal(str(row[3])) if row[3] else Decimal("0.00"),
                    description=str(row[4]) if row[4] else "",
                    source="AP",
                    status=str(row[6]),
                    matched=True
                ))
        
        return details
        
    except Exception as e:
        logger.error(f"Error getting reconciliation details: {e}")
        return []


@router.get("/summary", response_model=Dict[str, Any])
async def get_reconciliation_summary(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get summary of all subsidiary ledger reconciliations.
    """
    try:
        # Get AR reconciliation
        ar_result = await reconcile_ar(period, tenant_id, db)
        
        # Get AP reconciliation
        ap_result = await reconcile_ap(period, tenant_id, db)
        
        # Get Bank reconciliation
        bank_result = await reconcile_bank(period, tenant_id, db)
        
        total_accounts = ar_result.total_accounts + ap_result.total_accounts + bank_result.total_accounts
        total_balanced = ar_result.balanced_accounts + ap_result.balanced_accounts + bank_result.balanced_accounts
        total_unbalanced = ar_result.unbalanced_accounts + ap_result.unbalanced_accounts + bank_result.unbalanced_accounts
        
        return {
            "period": period,
            "reconciliation_date": date.today().isoformat(),
            "total_accounts": total_accounts,
            "balanced_accounts": total_balanced,
            "unbalanced_accounts": total_unbalanced,
            "reconciliations": {
                "AR": {
                    "total_accounts": ar_result.total_accounts,
                    "balanced_accounts": ar_result.balanced_accounts,
                    "unbalanced_accounts": ar_result.unbalanced_accounts,
                    "total_difference": float(ar_result.total_difference)
                },
                "AP": {
                    "total_accounts": ap_result.total_accounts,
                    "balanced_accounts": ap_result.balanced_accounts,
                    "unbalanced_accounts": ap_result.unbalanced_accounts,
                    "total_difference": float(ap_result.total_difference)
                },
                "BANK": {
                    "total_accounts": bank_result.total_accounts,
                    "balanced_accounts": bank_result.balanced_accounts,
                    "unbalanced_accounts": bank_result.unbalanced_accounts,
                    "total_difference": float(bank_result.total_difference)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting reconciliation summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

