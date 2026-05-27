"""
Subsidiary Ledger Reconciliation API
FIBU-CLS-02: Nebenbuch-Abstimmung implementieren
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.tenant import get_tenant_id
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


def _resolve_open_items_table(db: Session) -> str:
    for candidate in ("domain_erp.offene_posten", "offene_posten"):
        if db.execute(text("SELECT to_regclass(:name)"), {"name": candidate}).scalar():
            return candidate
    raise RuntimeError("offene_posten table not found")


def _sum_gl_balance(
    db: Session,
    account_id: str,
    tenant_id: str,
    period: str,
    liability_mode: bool = False,
) -> Decimal:
    row = db.execute(
        text(
            """
            SELECT
                COALESCE(SUM(CASE WHEN jel.debit > 0 THEN jel.debit ELSE 0 END), 0) as total_debit,
                COALESCE(SUM(CASE WHEN jel.credit > 0 THEN jel.credit ELSE 0 END), 0) as total_credit
            FROM domain_erp.journal_entry_lines jel
            JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
            WHERE jel.account_id = :account_id
              AND je.tenant_id = :tenant_id
              AND je.status = 'posted'
              AND TO_CHAR(je.entry_date::date, 'YYYY-MM') = :period
            """
        ),
        {"account_id": account_id, "tenant_id": tenant_id, "period": period},
    ).fetchone()

    total_debit = Decimal(str(row[0] if row and row[0] is not None else 0))
    total_credit = Decimal(str(row[1] if row and row[1] is not None else 0))
    return (total_credit - total_debit) if liability_mode else (total_debit - total_credit)


@router.get("/ar", response_model=ReconciliationResult, summary="Ar reconcile")
async def reconcile_ar(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Reconcile Accounts Receivable (Debitoren) with General Ledger."""
    try:
        ar_account = db.execute(
            text(
                """
                SELECT id, account_number, COALESCE(account_name, account_number)
                FROM domain_erp.chart_of_accounts
                WHERE tenant_id = :tenant_id
                  AND account_number LIKE '14%'
                  AND LOWER(account_type) = 'asset'
                ORDER BY account_number
                LIMIT 1
                """
            ),
            {"tenant_id": tenant_id},
        ).fetchone()

        if not ar_account:
            return ReconciliationResult(
                ledger_type="AR",
                period=period,
                reconciliation_date=date.today(),
                total_accounts=0,
                balanced_accounts=0,
                unbalanced_accounts=0,
                total_difference=Decimal("0.00"),
                entries=[],
            )

        account_id = str(ar_account[0])
        account_number = str(ar_account[1])
        account_name = str(ar_account[2])
        gl_balance = _sum_gl_balance(db, account_id, tenant_id, period, liability_mode=False)

        op_table = _resolve_open_items_table(db)
        row = db.execute(
            text(
                f"""
                SELECT COALESCE(SUM(offen), 0) as total_open,
                       COUNT(*) as entry_count,
                       SUM(CASE WHEN COALESCE(op_status, 'offen') IN ('offen','teilweise') THEN 1 ELSE 0 END) as unmatched_entries
                FROM {op_table}
                WHERE tenant_id = :tenant_id
                  AND konto_typ = 'debitoren'
                  AND TO_CHAR(COALESCE(rechnungsdatum, datum)::date, 'YYYY-MM') <= :period
                """
            ),
            {"tenant_id": tenant_id, "period": period},
        ).fetchone()

        subsidiary_balance = Decimal(str(row[0] if row and row[0] is not None else 0))
        entry_count = int(row[1] if row and row[1] is not None else 0)
        unmatched = int(row[2] if row and row[2] is not None else 0)

        difference = subsidiary_balance - gl_balance
        is_balanced = abs(difference) < Decimal("0.01")

        entries = [
            ReconciliationEntry(
                account_number=account_number,
                account_name=account_name,
                subsidiary_balance=subsidiary_balance,
                general_ledger_balance=gl_balance,
                difference=difference,
                is_balanced=is_balanced,
                entry_count=entry_count,
                unmatched_entries=unmatched,
            )
        ]

        return ReconciliationResult(
            ledger_type="AR",
            period=period,
            reconciliation_date=date.today(),
            total_accounts=1,
            balanced_accounts=1 if is_balanced else 0,
            unbalanced_accounts=0 if is_balanced else 1,
            total_difference=difference,
            entries=entries,
        )
    except Exception as e:
        logger.error("Error reconciling AR: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to reconcile AR: {str(e)}")


@router.get("/ap", response_model=ReconciliationResult, summary="Ap reconcile")
async def reconcile_ap(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Reconcile Accounts Payable (Kreditoren) with General Ledger."""
    try:
        ap_account = db.execute(
            text(
                """
                SELECT id, account_number, COALESCE(account_name, account_number)
                FROM domain_erp.chart_of_accounts
                WHERE tenant_id = :tenant_id
                  AND account_number LIKE '44%'
                  AND LOWER(account_type) = 'liability'
                ORDER BY account_number
                LIMIT 1
                """
            ),
            {"tenant_id": tenant_id},
        ).fetchone()

        if not ap_account:
            return ReconciliationResult(
                ledger_type="AP",
                period=period,
                reconciliation_date=date.today(),
                total_accounts=0,
                balanced_accounts=0,
                unbalanced_accounts=0,
                total_difference=Decimal("0.00"),
                entries=[],
            )

        account_id = str(ap_account[0])
        account_number = str(ap_account[1])
        account_name = str(ap_account[2])
        gl_balance = _sum_gl_balance(db, account_id, tenant_id, period, liability_mode=True)

        op_table = _resolve_open_items_table(db)
        row = db.execute(
            text(
                f"""
                SELECT COALESCE(SUM(offen), 0) as total_open,
                       COUNT(*) as entry_count,
                       SUM(CASE WHEN COALESCE(op_status, 'offen') IN ('offen','teilweise') THEN 1 ELSE 0 END) as unmatched_entries
                FROM {op_table}
                WHERE tenant_id = :tenant_id
                  AND konto_typ = 'kreditoren'
                  AND TO_CHAR(COALESCE(rechnungsdatum, datum)::date, 'YYYY-MM') <= :period
                """
            ),
            {"tenant_id": tenant_id, "period": period},
        ).fetchone()

        subsidiary_balance = Decimal(str(row[0] if row and row[0] is not None else 0))
        entry_count = int(row[1] if row and row[1] is not None else 0)
        unmatched = int(row[2] if row and row[2] is not None else 0)

        difference = subsidiary_balance - gl_balance
        is_balanced = abs(difference) < Decimal("0.01")

        entries = [
            ReconciliationEntry(
                account_number=account_number,
                account_name=account_name,
                subsidiary_balance=subsidiary_balance,
                general_ledger_balance=gl_balance,
                difference=difference,
                is_balanced=is_balanced,
                entry_count=entry_count,
                unmatched_entries=unmatched,
            )
        ]

        return ReconciliationResult(
            ledger_type="AP",
            period=period,
            reconciliation_date=date.today(),
            total_accounts=1,
            balanced_accounts=1 if is_balanced else 0,
            unbalanced_accounts=0 if is_balanced else 1,
            total_difference=difference,
            entries=entries,
        )
    except Exception as e:
        logger.error("Error reconciling AP: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to reconcile AP: {str(e)}")


@router.get("/bank", response_model=ReconciliationResult, summary="Bank reconcile")
async def reconcile_bank(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Reconcile Bank accounts with General Ledger."""
    try:
        bank_accounts = db.execute(
            text(
                """
                SELECT ba.id, ba.account_number, COALESCE(coa.account_name, ba.bank_name), COALESCE(ba.balance, 0)
                FROM domain_erp.bank_accounts ba
                LEFT JOIN domain_erp.chart_of_accounts coa
                  ON ba.account_number = coa.account_number
                 AND coa.tenant_id = ba.tenant_id
                WHERE ba.tenant_id = :tenant_id
                ORDER BY ba.account_number
                """
            ),
            {"tenant_id": tenant_id},
        ).fetchall()

        if not bank_accounts:
            return ReconciliationResult(
                ledger_type="BANK",
                period=period,
                reconciliation_date=date.today(),
                total_accounts=0,
                balanced_accounts=0,
                unbalanced_accounts=0,
                total_difference=Decimal("0.00"),
                entries=[],
            )

        entries: List[ReconciliationEntry] = []
        total_difference = Decimal("0.00")
        balanced_count = 0

        for _, account_number_raw, account_name_raw, bank_balance_raw in bank_accounts:
            account_number = str(account_number_raw)
            account_name = str(account_name_raw)
            bank_balance = Decimal(str(bank_balance_raw))

            coa_row = db.execute(
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

            if coa_row:
                gl_balance = _sum_gl_balance(db, str(coa_row[0]), tenant_id, period, liability_mode=False)
            else:
                gl_balance = Decimal("0.00")

            difference = bank_balance - gl_balance
            is_balanced = abs(difference) < Decimal("0.01")
            if is_balanced:
                balanced_count += 1

            total_difference += abs(difference)
            entries.append(
                ReconciliationEntry(
                    account_number=account_number,
                    account_name=account_name,
                    subsidiary_balance=bank_balance,
                    general_ledger_balance=gl_balance,
                    difference=difference,
                    is_balanced=is_balanced,
                    entry_count=0,
                    unmatched_entries=0,
                )
            )

        return ReconciliationResult(
            ledger_type="BANK",
            period=period,
            reconciliation_date=date.today(),
            total_accounts=len(entries),
            balanced_accounts=balanced_count,
            unbalanced_accounts=len(entries) - balanced_count,
            total_difference=total_difference,
            entries=entries,
        )
    except Exception as e:
        logger.error("Error reconciling BANK: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to reconcile BANK: {str(e)}")


@router.get("/{ledger_type}/details", response_model=List[ReconciliationDetail], summary="Reconciliation details abrufen")
async def get_reconciliation_details(
    ledger_type: str,
    account_number: str = Query(..., description="Account number"),
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get detailed entries for drilldown into differences."""
    try:
        details: List[ReconciliationDetail] = []
        op_table = _resolve_open_items_table(db)

        if ledger_type.lower() == "ar":
            rows = db.execute(
                text(
                    f"""
                    SELECT id, rechnungsnr, COALESCE(rechnungsdatum, datum) as entry_date,
                           COALESCE(offen, 0) as amount, COALESCE(op_text, '') as description,
                           COALESCE(op_status, 'offen') as status
                    FROM {op_table}
                    WHERE tenant_id = :tenant_id
                      AND konto_typ = 'debitoren'
                      AND TO_CHAR(COALESCE(rechnungsdatum, datum)::date, 'YYYY-MM') <= :period
                    ORDER BY COALESCE(rechnungsdatum, datum) DESC
                    """
                ),
                {"tenant_id": tenant_id, "period": period},
            ).fetchall()
            for row in rows:
                details.append(
                    ReconciliationDetail(
                        entry_id=str(row[0]),
                        entry_number=str(row[1] or ""),
                        entry_date=row[2],
                        amount=Decimal(str(row[3] or 0)),
                        description=str(row[4] or ""),
                        source="AR",
                        status=str(row[5] or "offen"),
                        matched=str(row[5] or "offen") == "geschlossen",
                    )
                )

        elif ledger_type.lower() == "ap":
            rows = db.execute(
                text(
                    f"""
                    SELECT id, rechnungsnr, COALESCE(rechnungsdatum, datum) as entry_date,
                           COALESCE(offen, 0) as amount, COALESCE(op_text, '') as description,
                           COALESCE(op_status, 'offen') as status
                    FROM {op_table}
                    WHERE tenant_id = :tenant_id
                      AND konto_typ = 'kreditoren'
                      AND TO_CHAR(COALESCE(rechnungsdatum, datum)::date, 'YYYY-MM') <= :period
                    ORDER BY COALESCE(rechnungsdatum, datum) DESC
                    """
                ),
                {"tenant_id": tenant_id, "period": period},
            ).fetchall()
            for row in rows:
                details.append(
                    ReconciliationDetail(
                        entry_id=str(row[0]),
                        entry_number=str(row[1] or ""),
                        entry_date=row[2],
                        amount=Decimal(str(row[3] or 0)),
                        description=str(row[4] or ""),
                        source="AP",
                        status=str(row[5] or "offen"),
                        matched=str(row[5] or "offen") == "geschlossen",
                    )
                )

        elif ledger_type.lower() == "bank":
            rows = db.execute(
                text(
                    """
                    SELECT jel.id, je.entry_number, je.entry_date,
                           (COALESCE(jel.debit,0) - COALESCE(jel.credit,0)) as amount,
                           COALESCE(jel.description, je.description, '') as description,
                           COALESCE(je.status, 'posted') as status
                    FROM domain_erp.journal_entry_lines jel
                    JOIN domain_erp.journal_entries je ON jel.journal_entry_id = je.id
                    JOIN domain_erp.chart_of_accounts coa ON jel.account_id = coa.id
                    WHERE coa.account_number = :account_number
                      AND coa.tenant_id = :tenant_id
                      AND je.tenant_id = :tenant_id
                      AND TO_CHAR(je.entry_date::date, 'YYYY-MM') = :period
                    ORDER BY je.entry_date DESC
                    """
                ),
                {"account_number": account_number, "tenant_id": tenant_id, "period": period},
            ).fetchall()
            for row in rows:
                details.append(
                    ReconciliationDetail(
                        entry_id=str(row[0]),
                        entry_number=str(row[1] or ""),
                        entry_date=row[2],
                        amount=Decimal(str(row[3] or 0)),
                        description=str(row[4] or ""),
                        source="BANK",
                        status=str(row[5] or "posted"),
                        matched=True,
                    )
                )

        return details
    except Exception as e:
        logger.error("Error getting reconciliation details: %s", e)
        return []


@router.get("/{ledger_type}/export", summary="Reconciliation csv exportieren")
async def export_reconciliation_csv(
    ledger_type: str,
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Export reconciliation result as CSV for closing documentation."""
    try:
        ledger_key = ledger_type.lower()
        if ledger_key == "ar":
            result = await reconcile_ar(period=period, tenant_id=tenant_id, db=db)
        elif ledger_key == "ap":
            result = await reconcile_ap(period=period, tenant_id=tenant_id, db=db)
        elif ledger_key == "bank":
            result = await reconcile_bank(period=period, tenant_id=tenant_id, db=db)
        else:
            raise HTTPException(status_code=400, detail="ledger_type must be AR, AP, or BANK")

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow([
            "ledger_type",
            "period",
            "account_number",
            "account_name",
            "subsidiary_balance",
            "general_ledger_balance",
            "difference",
            "is_balanced",
            "entry_count",
            "unmatched_entries",
        ])
        for entry in result.entries:
            writer.writerow([
                result.ledger_type,
                result.period,
                entry.account_number,
                entry.account_name,
                f"{entry.subsidiary_balance:.2f}",
                f"{entry.general_ledger_balance:.2f}",
                f"{entry.difference:.2f}",
                "JA" if entry.is_balanced else "NEIN",
                entry.entry_count,
                entry.unmatched_entries,
            ])

        csv_content = buffer.getvalue()
        buffer.close()

        filename = f"nebenbuch_abstimmung_{result.ledger_type.lower()}_{period}.csv"
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error exporting reconciliation CSV: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to export reconciliation CSV: {str(e)}")


@router.get("/summary", response_model=Dict[str, Any], summary="Reconciliation summary abrufen")
async def get_reconciliation_summary(
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get summary of all subsidiary ledger reconciliations."""
    try:
        ar_result = await reconcile_ar(period, tenant_id, db)
        ap_result = await reconcile_ap(period, tenant_id, db)
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
                    "total_difference": float(ar_result.total_difference),
                },
                "AP": {
                    "total_accounts": ap_result.total_accounts,
                    "balanced_accounts": ap_result.balanced_accounts,
                    "unbalanced_accounts": ap_result.unbalanced_accounts,
                    "total_difference": float(ap_result.total_difference),
                },
                "BANK": {
                    "total_accounts": bank_result.total_accounts,
                    "balanced_accounts": bank_result.balanced_accounts,
                    "unbalanced_accounts": bank_result.unbalanced_accounts,
                    "total_difference": float(bank_result.total_difference),
                },
            },
        }
    except Exception as e:
        logger.error("Error getting reconciliation summary: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")
