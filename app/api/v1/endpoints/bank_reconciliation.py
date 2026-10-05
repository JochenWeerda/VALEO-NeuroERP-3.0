"""Read-only bank balance evidence from one PostgreSQL statement snapshot."""
from datetime import date
from decimal import Decimal
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.bank_reconciliation_schemas import (
    BalanceComparison, DifferenceItem, LineCounts, ReconciliationResult,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bank-reconciliation", tags=["finance", "bank-reconciliation"])

# All evidence (including the bounded page) is read in one MVCC snapshot.
_EVIDENCE = text("""
WITH statement AS (
    SELECT bs.*, ba.currency, ba.gl_account_id, ba.iban AS current_iban,
           coa.id AS ledger_id, coa.is_active AS ledger_active,
           coa.account_type AS ledger_type, coa.category AS ledger_category, coa.is_summary AS ledger_summary,
           coa.deleted_at AS ledger_deleted
    FROM domain_erp.bank_statements bs
    JOIN domain_erp.bank_accounts ba ON ba.id=bs.bank_account_id AND ba.tenant_id=bs.tenant_id
    LEFT JOIN domain_erp.chart_of_accounts coa ON coa.id=ba.gl_account_id AND coa.tenant_id=ba.tenant_id
    WHERE bs.id=:statement_id AND bs.tenant_id=:tenant_id
      AND ba.id=:bank_account_id AND ba.is_active=TRUE
), line_stats AS (
    SELECT count(l.id) AS actual_total,
           count(l.id) FILTER (WHERE l.status='MATCHED') AS matched,
           count(l.id) FILTER (WHERE l.status='UNMATCHED') AS unmatched,
           count(l.id) FILTER (WHERE l.status='PARTIAL') AS partial,
           count(l.id) FILTER (WHERE l.status IS NULL OR l.status NOT IN ('MATCHED','UNMATCHED','PARTIAL')) AS unknown,
           coalesce(sum(l.amount),0) AS amount_sum,
           bool_and(CASE WHEN l.id IS NULL THEN TRUE ELSE coalesce(
               l.tenant_id=s.tenant_id AND l.currency=s.currency
               AND l.booking_date IS NOT NULL AND l.booking_date<=s.statement_date
               AND (l.status IS DISTINCT FROM 'MATCHED' OR
                    (l.matched_op_id IS NOT NULL AND op.tenant_id=s.tenant_id AND op.waehrung=s.currency)),FALSE) END) AS lines_valid
    FROM statement s LEFT JOIN domain_erp.bank_statement_lines l ON l.statement_id=s.id
    LEFT JOIN domain_erp.offene_posten op ON op.id=l.matched_op_id
), ledger_entries AS (
    SELECT je.id, je.total_debit, je.total_credit, je.currency, s.currency AS bank_currency,
           count(*) AS legs, sum(l.debit_amount) AS debit_sum, sum(l.credit_amount) AS credit_sum,
           sum(CASE WHEN l.account_id=s.gl_account_id THEN l.debit_amount-l.credit_amount ELSE 0 END) AS bank_net,
           bool_and(coalesce(l.tenant_id=s.tenant_id AND ca.tenant_id=s.tenant_id
               AND l.debit IS NOT DISTINCT FROM l.debit_amount
               AND l.credit IS NOT DISTINCT FROM l.credit_amount
               AND l.debit_amount::text NOT IN ('NaN','Infinity','-Infinity')
               AND l.credit_amount::text NOT IN ('NaN','Infinity','-Infinity')
               AND ((l.debit_amount>0 AND l.credit_amount=0) OR (l.credit_amount>0 AND l.debit_amount=0)),FALSE)) AS valid_legs
    FROM statement s
    JOIN domain_erp.journal_entries je ON je.tenant_id=s.tenant_id AND je.status='posted'
         AND je.entry_date < s.statement_date + 1
    JOIN domain_erp.journal_entry_lines l ON l.journal_entry_id=je.id
    LEFT JOIN domain_erp.chart_of_accounts ca ON ca.id=l.account_id
    WHERE EXISTS (SELECT 1 FROM domain_erp.journal_entry_lines target
                  WHERE target.journal_entry_id=je.id AND target.account_id=s.gl_account_id)
    GROUP BY je.id, je.total_debit, je.total_credit, je.currency, s.currency
), ledger_stats AS (
    SELECT count(*) AS journal_count, sum(bank_net) AS ledger_balance,
           coalesce(bool_and(valid_legs AND legs>=2 AND debit_sum=credit_sum
             AND debit_sum=total_debit AND credit_sum=total_credit AND total_debit>0
             AND currency=bank_currency AND total_debit::text NOT IN ('NaN','Infinity','-Infinity')
             AND total_credit::text NOT IN ('NaN','Infinity','-Infinity')),TRUE) AS ledger_valid
    FROM ledger_entries
), bad_ledger_refs AS (
    SELECT count(*) AS bad_refs FROM statement s
    JOIN domain_erp.journal_entry_lines l ON l.account_id=s.gl_account_id
    LEFT JOIN domain_erp.journal_entries je ON je.id=l.journal_entry_id
    WHERE l.tenant_id IS DISTINCT FROM s.tenant_id OR je.tenant_id IS DISTINCT FROM s.tenant_id
), difference_page AS (
    SELECT l.id, l.booking_date, l.amount, l.reference, l.remittance_info, l.status, l.line_number
    FROM statement s JOIN domain_erp.bank_statement_lines l ON l.statement_id=s.id AND l.tenant_id=s.tenant_id
    WHERE l.status IS DISTINCT FROM 'MATCHED'
    ORDER BY l.booking_date,l.line_number,l.id LIMIT :limit OFFSET :offset
)
SELECT s.*, ls.*, js.*, bad.bad_refs,
       coalesce((SELECT jsonb_agg(jsonb_build_object(
           'id',p.id,'date',p.booking_date,'amount',p.amount::text,
           'reference',p.reference,'description',p.remittance_info,'status',p.status)
           ORDER BY p.booking_date,p.line_number,p.id) FROM difference_page p),'[]'::jsonb) AS difference_rows
FROM statement s CROSS JOIN line_stats ls CROSS JOIN ledger_stats js CROSS JOIN bad_ledger_refs bad
""")


def _money(value):
    if value is None:
        raise HTTPException(409, "Gespeicherter Geldbetrag fehlt")
    amount = Decimal(str(value))
    if not amount.is_finite() or amount != amount.quantize(Decimal("0.01")):
        raise HTTPException(409, "Gespeicherter Geldbetrag ist ungueltig")
    return amount


def _comparison(statement_id: str, bank_account_id: str, tenant_id: str, db: Session,
                *, offset: int = 0, limit: int = 100) -> ReconciliationResult:
    try:
        row = db.execute(_EVIDENCE, {"statement_id": statement_id, "bank_account_id": bank_account_id,
                                  "tenant_id": tenant_id, "offset": offset, "limit": limit}).mappings().one_or_none()
        if row is None:
            raise HTTPException(404, "Kontoauszug fuer dieses Bankkonto nicht gefunden")
        if not row["statement_date"] or not isinstance(row["statement_date"], date):
            raise HTTPException(409, "Kontoauszug hat keinen belegten Stichtag")
        def normalize(value):
            return str(value or "").replace(" ", "").upper()
        if not row["account_iban"] or normalize(row["account_iban"]) != normalize(row["current_iban"]):
            raise HTTPException(409, "Gespeicherter Auszug widerspricht der Konto-IBAN")
        if not row["lines_valid"] or row["total_lines"] != row["actual_total"] or row["imported_lines"] != row["actual_total"]:
            raise HTTPException(409, "Kontoauszug ist unvollstaendig oder enthaelt widerspruechliche Zeilen")
        if row["format"] not in ("CAMT", "MT940", "CSV"):
            raise HTTPException(409, "Unbekannter Auszugsvertrag")
        opening, closing, movements = (_money(row[key]) for key in ("opening_balance", "closing_balance", "amount_sum"))
        if opening + movements != closing:
            raise HTTPException(409, "Auszugssalden widersprechen den gespeicherten Umsaetzen")
        ledger = row["gl_account_id"]
        if ledger and (not row["ledger_id"] or not row["ledger_active"] or row["ledger_deleted"]
                       or row["ledger_summary"] or str(row["ledger_type"]).upper() != "ASSET"
                       or str(row["ledger_category"]).upper() != "BANK"):
            raise HTTPException(409, "Hauptbuchverbindung ist nicht buchbar")
        if row["bad_refs"] or not row["ledger_valid"]:
            raise HTTPException(409, "Hauptbuchnachweis enthaelt widerspruechliche Mandanten, Betraege oder Buchungen")
        accounting_state = "MAPPING_REQUIRED" if not ledger else "AVAILABLE" if row["journal_count"] else "NO_POSTED_ENTRIES"
        balance = BalanceComparison(
            bank_statement_balance=closing if row["format"] != "CSV" else None,
            accounting_balance=_money(row["ledger_balance"]) if accounting_state == "AVAILABLE" else None,
            statement_date=row["statement_date"], comparison_date=business_today(),
            currency=row["currency"], ledger_account_id=ledger,
            bank_balance_state="CSV_SYNTHETIC" if row["format"] == "CSV" else "BANK_PROVIDED",
            accounting_state=accounting_state,
        )
        counts = LineCounts(total=row["actual_total"], matched=row["matched"], unmatched=row["unmatched"],
                            partial=row["partial"], unknown=row["unknown"])
        differences = [DifferenceItem(
            item_type="UNMATCHED_STATEMENT" if item["status"] == "UNMATCHED" else "PARTIAL_STATEMENT" if item["status"] == "PARTIAL" else "UNKNOWN_STATEMENT_STATUS",
            statement_line_id=item["id"], date=item["date"], amount=_money(item["amount"]),
            bank_amount=_money(item["amount"]), reference=item["reference"],
            description=item["description"] or item["reference"] or "Ungeklaerte Bankzeile",
        ) for item in row["difference_rows"]]
        unresolved_count = counts.unmatched+counts.partial+counts.unknown
        balance_mismatch = balance.difference is not None and balance.difference != 0
        if balance_mismatch and offset <= unresolved_count <= offset+len(differences) and len(differences)<limit:
            differences.append(DifferenceItem(item_type="BALANCE_MISMATCH", date=balance.statement_date,
                amount=balance.difference, bank_amount=balance.bank_statement_balance,
                accounting_amount=balance.accounting_balance, description="Bank- und Hauptbuchsaldo weichen ab"))
        return ReconciliationResult(statement_id=statement_id, bank_account_id=bank_account_id,
            balance_comparison=balance, differences=differences,
            total_differences=unresolved_count+int(balance_mismatch),
            line_counts=counts, differences_offset=offset, differences_limit=limit)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Bank comparison evidence could not be read")
        raise HTTPException(500, "Bankvergleich konnte nicht verlaesslich ermittelt werden") from None


@router.get("/{statement_id}/balance-comparison", response_model=BalanceComparison, summary="Bank balance evidence")
async def get_balance_comparison(statement_id: str, bank_account_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _comparison(statement_id, bank_account_id, tenant_id, db).balance_comparison


@router.get("/{statement_id}/differences", response_model=list[DifferenceItem], summary="Unresolved bank lines")
async def get_reconciliation_differences(statement_id: str, bank_account_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
    offset: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 100):
    return _comparison(statement_id, bank_account_id, tenant_id, db, offset=offset, limit=limit).differences


@router.post("/{statement_id}/reconcile", response_model=ReconciliationResult, summary="Read-only bank comparison")
async def reconcile_bank_statement(statement_id: str, bank_account_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    auto_book: Annotated[bool, Query(description="Retired: direct booking is not supported")] = False,
    db: Session = Depends(get_db)):
    if auto_book is not False:
        raise HTTPException(409, "Direct bank reconciliation booking has been retired; use the journal posting workflow")
    return _comparison(statement_id, bank_account_id, tenant_id, db)


@router.get("/{statement_id}/summary", response_model=ReconciliationResult, summary="Canonical bank comparison summary")
async def get_reconciliation_summary(statement_id: str, bank_account_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _comparison(statement_id, bank_account_id, tenant_id, db)
