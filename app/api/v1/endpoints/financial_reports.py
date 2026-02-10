"""
Financial Reports API
FIBU-REP-01: Standardreports (Bilanz/GuV/BWA) Backend-Integration
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

router = APIRouter(prefix="/financial-reports", tags=["finance", "reports"])


class BalanceSheetItem(BaseModel):
    """Balance sheet item"""
    account_number: str
    account_name: str
    account_type: str  # ASSET, LIABILITY, EQUITY
    balance: Decimal
    parent_account: Optional[str] = None
    level: int = 0


class BalanceSheet(BaseModel):
    """Balance sheet report"""
    period: str
    as_of_date: date
    assets: List[BalanceSheetItem]
    liabilities: List[BalanceSheetItem]
    equity: List[BalanceSheetItem]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    is_balanced: bool


class ProfitLossItem(BaseModel):
    """Profit & Loss statement item"""
    account_number: str
    account_name: str
    account_type: str  # REVENUE, EXPENSE
    amount: Decimal
    parent_account: Optional[str] = None
    level: int = 0


class ProfitLoss(BaseModel):
    """Profit & Loss statement"""
    period: str
    revenue: List[ProfitLossItem]
    expenses: List[ProfitLossItem]
    total_revenue: Decimal
    total_expenses: Decimal
    net_income: Decimal


class BWAItem(BaseModel):
    """BWA (Betriebswirtschaftliche Auswertung) item"""
    position: str
    description: str
    current_period: Decimal
    previous_period: Decimal
    year_to_date: Decimal
    percentage: Decimal


class BWA(BaseModel):
    """BWA (Betriebswirtschaftliche Auswertung) report"""
    period: str
    items: List[BWAItem]
    total_revenue: Decimal
    total_costs: Decimal
    net_result: Decimal


@router.get("/balance-sheet", response_model=BalanceSheet)
async def get_balance_sheet(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    as_of_date: Optional[date] = Query(None, description="As of date (defaults to end of period)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get balance sheet for a period.
    """
    try:
        if not as_of_date:
            # Default to end of period
            year, month = period.split('-')
            from calendar import monthrange
            last_day = monthrange(int(year), int(month))[1]
            as_of_date = date(int(year), int(month), last_day)
        
        # Get all accounts with balances
        accounts_query = text("""
            SELECT 
                coa.account_number,
                coa.name,
                coa.account_type,
                coa.parent_account_id,
                COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) as total_debit,
                COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) as total_credit
            FROM domain_erp.chart_of_accounts coa
            LEFT JOIN domain_erp.journal_entry_lines jel ON coa.id = jel.account_id
            LEFT JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE coa.tenant_id = :tenant_id
            AND (je.tenant_id = :tenant_id OR je.tenant_id IS NULL)
            AND (je.status = 'posted' OR je.status IS NULL)
            AND (TO_CHAR(je.entry_date, 'YYYY-MM') <= :period OR je.entry_date IS NULL)
            GROUP BY coa.id, coa.account_number, coa.name, coa.account_type, coa.parent_account_id
            ORDER BY coa.account_number
        """)
        
        rows = db.execute(accounts_query, {
            "tenant_id": tenant_id,
            "period": period
        }).fetchall()
        
        assets = []
        liabilities = []
        equity = []
        
        for row in rows:
            account_number = str(row[0])
            account_name = str(row[1])
            account_type = str(row[2])
            parent_account = str(row[3]) if row[3] else None
            total_debit = Decimal(str(row[4])) if row[4] else Decimal("0.00")
            total_credit = Decimal(str(row[5])) if row[5] else Decimal("0.00")
            
            # Calculate balance based on account type
            if account_type == 'ASSET':
                balance = total_debit - total_credit
            elif account_type in ['LIABILITY', 'EQUITY']:
                balance = total_credit - total_debit
            else:
                balance = Decimal("0.00")
            
            # Skip zero balances
            if abs(balance) < Decimal("0.01"):
                continue
            
            item = BalanceSheetItem(
                account_number=account_number,
                account_name=account_name,
                account_type=account_type,
                balance=balance,
                parent_account=parent_account,
                level=0
            )
            
            if account_type == 'ASSET':
                assets.append(item)
            elif account_type == 'LIABILITY':
                liabilities.append(item)
            elif account_type == 'EQUITY':
                equity.append(item)
        
        total_assets = sum(item.balance for item in assets)
        total_liabilities = sum(item.balance for item in liabilities)
        total_equity = sum(item.balance for item in equity)
        is_balanced = abs(total_assets - (total_liabilities + total_equity)) < Decimal("0.01")
        
        return BalanceSheet(
            period=period,
            as_of_date=as_of_date,
            assets=assets,
            liabilities=liabilities,
            equity=equity,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            total_equity=total_equity,
            is_balanced=is_balanced
        )
        
    except Exception as e:
        logger.error(f"Error generating balance sheet: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate balance sheet: {str(e)}")


@router.get("/profit-loss", response_model=ProfitLoss)
async def get_profit_loss(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get profit & loss statement for a period.
    """
    try:
        # Get revenue accounts (typically 4xxx, 5xxx, 6xxx, 7xxx, 8xxx)
        revenue_query = text("""
            SELECT 
                coa.account_number,
                coa.name,
                'REVENUE' as account_type,
                COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) as total_credit,
                COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) as total_debit
            FROM domain_erp.chart_of_accounts coa
            LEFT JOIN domain_erp.journal_entry_lines jel ON coa.id = jel.account_id
            LEFT JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE coa.tenant_id = :tenant_id
            AND coa.account_number LIKE '4%'
            AND (je.tenant_id = :tenant_id OR je.tenant_id IS NULL)
            AND (je.status = 'posted' OR je.status IS NULL)
            AND TO_CHAR(je.entry_date, 'YYYY-MM') = :period
            GROUP BY coa.id, coa.account_number, coa.name
            HAVING ABS(COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) - 
                       COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0)) >= 0.01
            ORDER BY coa.account_number
        """)
        
        revenue_rows = db.execute(revenue_query, {
            "tenant_id": tenant_id,
            "period": period
        }).fetchall()
        
        revenue = []
        for row in revenue_rows:
            total_credit = Decimal(str(row[3])) if row[3] else Decimal("0.00")
            total_debit = Decimal(str(row[4])) if row[4] else Decimal("0.00")
            amount = total_credit - total_debit  # Revenue is credit - debit
            
            if abs(amount) >= Decimal("0.01"):
                revenue.append(ProfitLossItem(
                    account_number=str(row[0]),
                    account_name=str(row[1]),
                    account_type='REVENUE',
                    amount=amount,
                    level=0
                ))
        
        # Get expense accounts (typically 5xxx, 6xxx, 7xxx, 8xxx)
        expense_query = text("""
            SELECT 
                coa.account_number,
                coa.name,
                'EXPENSE' as account_type,
                COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) as total_debit,
                COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0) as total_credit
            FROM domain_erp.chart_of_accounts coa
            LEFT JOIN domain_erp.journal_entry_lines jel ON coa.id = jel.account_id
            LEFT JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE coa.tenant_id = :tenant_id
            AND (coa.account_number LIKE '5%' OR coa.account_number LIKE '6%' OR 
                 coa.account_number LIKE '7%' OR coa.account_number LIKE '8%')
            AND (je.tenant_id = :tenant_id OR je.tenant_id IS NULL)
            AND (je.status = 'posted' OR je.status IS NULL)
            AND TO_CHAR(je.entry_date, 'YYYY-MM') = :period
            GROUP BY coa.id, coa.account_number, coa.name
            HAVING ABS(COALESCE(SUM(CASE WHEN jel.debit_amount > 0 THEN jel.debit_amount ELSE 0 END), 0) - 
                       COALESCE(SUM(CASE WHEN jel.credit_amount > 0 THEN jel.credit_amount ELSE 0 END), 0)) >= 0.01
            ORDER BY coa.account_number
        """)
        
        expense_rows = db.execute(expense_query, {
            "tenant_id": tenant_id,
            "period": period
        }).fetchall()
        
        expenses = []
        for row in expense_rows:
            total_debit = Decimal(str(row[3])) if row[3] else Decimal("0.00")
            total_credit = Decimal(str(row[4])) if row[4] else Decimal("0.00")
            amount = total_debit - total_credit  # Expenses are debit - credit
            
            if abs(amount) >= Decimal("0.01"):
                expenses.append(ProfitLossItem(
                    account_number=str(row[0]),
                    account_name=str(row[1]),
                    account_type='EXPENSE',
                    amount=amount,
                    level=0
                ))
        
        total_revenue = sum(item.amount for item in revenue)
        total_expenses = sum(item.amount for item in expenses)
        net_income = total_revenue - total_expenses
        
        return ProfitLoss(
            period=period,
            revenue=revenue,
            expenses=expenses,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_income=net_income
        )
        
    except Exception as e:
        logger.error(f"Error generating profit & loss: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate profit & loss: {str(e)}")


@router.get("/bwa", response_model=BWA)
async def get_bwa(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get BWA (Betriebswirtschaftliche Auswertung) for a period.
    """
    try:
        year, month = period.split('-')
        year_int = int(year)
        month_int = int(month)
        
        # Get current period data
        current_period_data = await get_profit_loss(period, tenant_id, db)
        
        # Get previous period
        if month_int == 1:
            prev_period = f"{year_int - 1}-12"
        else:
            prev_period = f"{year_int}-{month_int - 1:02d}"
        
        previous_period_data = await get_profit_loss(prev_period, tenant_id, db)
        
        # Get year-to-date data
        ytd_period = f"{year_int}-12"
        ytd_data = await get_profit_loss(ytd_period, tenant_id, db)
        
        items = []
        
        # Revenue positions
        items.append(BWAItem(
            position="1",
            description="Umsatzerlöse",
            current_period=current_period_data.total_revenue,
            previous_period=previous_period_data.total_revenue,
            year_to_date=ytd_data.total_revenue,
            percentage=Decimal("100.00")
        ))
        
        # Material costs
        material_expenses = sum(item.amount for item in current_period_data.expenses 
                               if item.account_number.startswith('5'))
        items.append(BWAItem(
            position="2",
            description="Materialaufwand",
            current_period=material_expenses,
            previous_period=sum(item.amount for item in previous_period_data.expenses 
                               if item.account_number.startswith('5')),
            year_to_date=sum(item.amount for item in ytd_data.expenses 
                           if item.account_number.startswith('5')),
            percentage=(material_expenses / current_period_data.total_revenue * 100) 
                       if current_period_data.total_revenue > 0 else Decimal("0.00")
        ))
        
        # Personnel costs
        personnel_expenses = sum(item.amount for item in current_period_data.expenses 
                               if item.account_number.startswith('6'))
        items.append(BWAItem(
            position="3",
            description="Personalaufwand",
            current_period=personnel_expenses,
            previous_period=sum(item.amount for item in previous_period_data.expenses 
                               if item.account_number.startswith('6')),
            year_to_date=sum(item.amount for item in ytd_data.expenses 
                           if item.account_number.startswith('6')),
            percentage=(personnel_expenses / current_period_data.total_revenue * 100) 
                       if current_period_data.total_revenue > 0 else Decimal("0.00")
        ))
        
        # Other expenses
        other_expenses = sum(item.amount for item in current_period_data.expenses 
                           if not item.account_number.startswith('5') and 
                              not item.account_number.startswith('6'))
        items.append(BWAItem(
            position="4",
            description="Sonstige Aufwendungen",
            current_period=other_expenses,
            previous_period=sum(item.amount for item in previous_period_data.expenses 
                               if not item.account_number.startswith('5') and 
                                  not item.account_number.startswith('6')),
            year_to_date=sum(item.amount for item in ytd_data.expenses 
                           if not item.account_number.startswith('5') and 
                              not item.account_number.startswith('6')),
            percentage=(other_expenses / current_period_data.total_revenue * 100) 
                       if current_period_data.total_revenue > 0 else Decimal("0.00")
        ))
        
        total_costs = material_expenses + personnel_expenses + other_expenses
        net_result = current_period_data.total_revenue - total_costs
        
        items.append(BWAItem(
            position="5",
            description="Jahresüberschuss/-fehlbetrag",
            current_period=net_result,
            previous_period=previous_period_data.net_income,
            year_to_date=ytd_data.net_income,
            percentage=(net_result / current_period_data.total_revenue * 100) 
                       if current_period_data.total_revenue > 0 else Decimal("0.00")
        ))
        
        return BWA(
            period=period,
            items=items,
            total_revenue=current_period_data.total_revenue,
            total_costs=total_costs,
            net_result=net_result
        )
        
    except Exception as e:
        logger.error(f"Error generating BWA: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate BWA: {str(e)}")


@router.get("/export/{report_type}")
async def export_report(
    report_type: str,
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    format: str = Query("pdf", description="Export format (pdf, excel)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Export financial report in PDF or Excel format.
    """
    try:
        if report_type == "balance-sheet":
            data = await get_balance_sheet(period, None, tenant_id, db)
        elif report_type == "profit-loss":
            data = await get_profit_loss(period, tenant_id, db)
        elif report_type == "bwa":
            data = await get_bwa(period, tenant_id, db)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown report type: {report_type}")
        
        # For now, return JSON (PDF/Excel generation would require additional libraries)
        # In production, you would use libraries like reportlab (PDF) or openpyxl (Excel)
        return {
            "report_type": report_type,
            "period": period,
            "format": format,
            "data": data.dict() if hasattr(data, 'dict') else data,
            "exported_at": datetime.now().isoformat(),
            "note": "PDF/Excel export requires additional libraries. Currently returning JSON."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")

