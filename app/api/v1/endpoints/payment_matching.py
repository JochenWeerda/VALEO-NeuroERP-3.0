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
from app.core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_payment_import_datensatz,
)

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema


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


def _build_payment_import_datensatz(
    booking_date: object,
    amount: object,
    currency: object = "EUR",
    reference: object | None = None,
) -> dict:
    return {
        "booking_date": booking_date,
        "amount": amount,
        "currency": currency or "EUR",
        "reference": reference,
    }


@router.post("/import/csv", response_model=List[PaymentEntry], summary="Payments csv importieren")
async def import_payments_csv(
    file: UploadFile = File(...),
    tenant_id: str = Query("default"),
    bank_account: str = Query(...),
    db: Session = Depends(get_db)
):
    """Import payments from CSV and persist to bank_statement_lines for matching."""
    try:
        content = await file.read()
        text_content = content.decode('utf-8-sig')
        csv_reader = csv.DictReader(io.StringIO(text_content))
        
        raw_rows = list(csv_reader)
        if not raw_rows:
            return []

        dq_context = []
        for row in raw_rows:
            booking_date_raw = row.get('date', row.get('booking_date', ''))
            amount_raw = str(row.get('amount', '0')).replace(',', '.')
            currency = row.get('currency', row.get('waehrung', 'EUR'))
            reference = row.get('reference', '')
            dq_context.append(
                _build_payment_import_datensatz(
                    booking_date=booking_date_raw,
                    amount=amount_raw,
                    currency=currency,
                    reference=reference,
                )
            )

        entries: list[dict] = []
        for row_number, row in enumerate(raw_rows, start=2):
            booking_date_raw = row.get('date', row.get('booking_date', ''))
            amount_raw = str(row.get('amount', '0')).replace(',', '.')
            currency = row.get('currency', row.get('waehrung', 'EUR'))
            dq_result = evaluate_payment_import_datensatz(
                _build_payment_import_datensatz(
                    booking_date=booking_date_raw,
                    amount=amount_raw,
                    currency=currency,
                    reference=row.get('reference', ''),
                ),
                dq_context,
            )
            if not dq_result.bestanden:
                raise HTTPException(
                    status_code=422,
                    detail=build_dq_error_detail("Zahlungsimport", dq_result),
                )

            try:
                booking_date = datetime.strptime(booking_date_raw, '%Y-%m-%d').date()
                amount = Decimal(amount_raw)
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Failed to parse CSV row {row_number}: {str(e)}") from e

            reference = row.get('reference', '')
            remittance_info = row.get('remittance_info', '')
            entries.append({
                "booking_date": booking_date,
                "amount": amount,
                "reference": reference,
                "remittance_info": remittance_info,
            })

        if not entries:
            return []

        statement_id = f"STMT-CSV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{bank_account[:8]}"
        try:
            stmt_ins = text("""
                INSERT INTO domain_erp.bank_statements
                (id, tenant_id, bank_account_id, account_iban, statement_date, opening_balance,
                 closing_balance, format, total_lines, imported_lines, status, created_at, updated_at)
                VALUES (:id, :tenant_id, :bank_account_id, :iban, :stmt_date, 0, 0, 'CSV', :total, :imported, 'imported', NOW(), NOW())
            """)
            db.execute(stmt_ins, {
                "id": statement_id,
                "tenant_id": tenant_id,
                "bank_account_id": bank_account,
                "iban": "",
                "stmt_date": entries[0]["booking_date"] if entries else date.today(),
                "total": len(entries),
                "imported": len(entries),
            })
        except Exception as e:
            logger.warning(f"bank_statements insert skipped: {e}")

        line_ins = text("""
            INSERT INTO domain_erp.bank_statement_lines
            (id, tenant_id, statement_id, line_number, booking_date, value_date,
             amount, currency, reference, remittance_info, creditor_name, creditor_iban,
             debtor_name, debtor_iban, status, created_at, updated_at)
            VALUES (:id, :tenant_id, :statement_id, :line_num, :book_date, :val_date,
                    :amount, 'EUR', :reference, :remittance, NULL, NULL, NULL, NULL, 'UNMATCHED', NOW(), NOW())
        """)
        result_entries: list[PaymentEntry] = []
        for idx, e in enumerate(entries):
            line_id = f"{statement_id}-L{idx + 1}"
            try:
                db.execute(line_ins, {
                    "id": line_id,
                    "tenant_id": tenant_id,
                    "statement_id": statement_id,
                    "line_num": idx + 1,
                    "book_date": e["booking_date"],
                    "val_date": e["booking_date"],
                    "amount": e["amount"],
                    "reference": e["reference"],
                    "remittance": e["remittance_info"],
                })
                result_entries.append(PaymentEntry(
                    id=line_id,
                    tenant_id=tenant_id,
                    bank_account=bank_account,
                    booking_date=e["booking_date"],
                    value_date=e["booking_date"],
                    amount=e["amount"],
                    reference=e["reference"],
                    remittance_info=e["remittance_info"],
                    match_status="UNMATCHED",
                ))
            except Exception as ins_err:
                logger.warning(f"Insert line {line_id}: {ins_err}")
        db.commit()
        logger.info(f"Imported {len(result_entries)} payments from CSV into bank_statement_lines")
        return result_entries

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import CSV: {str(e)}")


@router.get("/unmatched", response_model=List[PaymentEntry], summary="Unmatched payments abrufen")
async def get_unmatched_payments(
    tenant_id: str = Query("default"),
    bank_account: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get unmatched payment entries from bank_statement_lines (and optional CSV-import)."""
    try:
        # Query bank_statement_lines; join bank_statements for bank_account_id if present
        query = text("""
            SELECT bsl.id, bsl.tenant_id,
                   COALESCE(bs.bank_account_id::text, bsl.statement_id) AS bank_account,
                   bsl.booking_date, bsl.value_date, bsl.amount, bsl.currency,
                   bsl.reference, bsl.remittance_info, bsl.creditor_name, bsl.debtor_name,
                   COALESCE(bsl.status, 'UNMATCHED')
            FROM domain_erp.bank_statement_lines bsl
            LEFT JOIN domain_erp.bank_statements bs ON bsl.statement_id = bs.id AND bs.tenant_id = bsl.tenant_id
            WHERE bsl.tenant_id = :tenant_id
            AND (bsl.status = 'UNMATCHED' OR bsl.status IS NULL)
            ORDER BY bsl.booking_date DESC, bsl.id
            LIMIT :limit OFFSET :skip
        """)
        params: dict = {"tenant_id": tenant_id, "limit": limit, "skip": skip}
        rows = db.execute(query, params).fetchall()
        return [
            PaymentEntry(
                id=str(r[0]),
                tenant_id=str(r[1]),
                bank_account=str(r[2]) if r[2] else "",
                booking_date=r[3],
                value_date=r[4],
                amount=Decimal(str(r[5])),
                currency=str(r[6]) if r[6] else "EUR",
                reference=r[7],
                remittance_info=r[8],
                creditor_name=r[9],
                debtor_name=r[10],
                matched_op_id=None,
                match_status=str(r[11]) if r[11] else "UNMATCHED",
            )
            for r in rows
        ]
    except Exception as e:
        logger.debug(f"get_unmatched_payments: {e}")
        return []


@router.get("/open-items/{customer_id}", response_model=List[OpenItemMatch], summary="Open items for matching abrufen")
async def get_open_items_for_matching(
    customer_id: str,
    tenant_id: str = Query("default"),
    db: Session = Depends(get_db)
):
    """Get open AR items for a customer for payment matching."""
    try:
        query = """
            SELECT 
                id, rechnungsnr, kunde_id, kunde_name,
                op_betrag, offen, faelligkeit, waehrung, op_status
            FROM domain_erp.offene_posten
            WHERE tenant_id = :tenant_id 
            AND konto_typ = 'debitoren'
            AND kunde_id = :customer_id
            AND op_status IN ('offen', 'teilweise')
            ORDER BY faelligkeit ASC
        """
        
        results = db.execute(
            text(query),
            {"tenant_id": tenant_id, "customer_id": customer_id}
        ).fetchall()
        
        return [
            OpenItemMatch(
                op_id=str(r[0]),
                document_number=str(r[1]),
                customer_id=str(r[2] or ""),
                customer_name=str(r[3] or ""),
                amount=Decimal(str(r[4])),
                open_amount=Decimal(str(r[5])),
                due_date=r[6],
                currency=str(r[7] or "EUR"),
                status=str(r[8] or "offen")
            )
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Error fetching open items: {e}")
        # Return empty list if table doesn't exist yet
        return []


@router.post("/match/{payment_id}", response_model=MatchResult, summary="Payment match")
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
            SELECT id, rechnungsnr, kunde_id, kunde_name,
                   op_betrag, offen, faelligkeit, waehrung, op_status
            FROM domain_erp.offene_posten
            WHERE id = :op_id AND tenant_id = :tenant_id
            AND konto_typ = 'debitoren'
        """
        op_result = db.execute(
            text(op_query),
            {"op_id": op_id, "tenant_id": tenant_id}
        ).fetchone()
        
        if not op_result:
            raise HTTPException(status_code=404, detail="Open item not found")
        
        open_amount = Decimal(str(op_result[5] or 0))
        
        # In production, fetch payment amount and match
        # For now, assume full match
        matched_amount = open_amount
        remaining_amount = Decimal("0.00")
        
        # Update OP status
        if remaining_amount == 0:
            new_status = "geschlossen"
        else:
            new_status = "teilweise"
        
        update_query = """
            UPDATE domain_erp.offene_posten
            SET op_status = :status,
                offen = GREATEST(offen - :matched_amount, 0),
                updated_at = NOW()
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
        # Mark bank statement line as matched (if payment_id is a bank_statement_lines.id)
        try:
            upd_line = text("""
                UPDATE domain_erp.bank_statement_lines
                SET status = :status, matched_op_id = :op_id
                WHERE id = :payment_id AND tenant_id = :tenant_id
            """)
            db.execute(upd_line, {
                "status": "MATCHED" if remaining_amount == 0 else "PARTIAL",
                "op_id": op_id,
                "payment_id": payment_id,
                "tenant_id": tenant_id,
            })
        except Exception as line_err:
            logger.warning(f"Update bank_statement_lines for match: {line_err}")
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


@router.post("/auto-match", response_model=List[MatchResult], summary="Match payments auto")
async def auto_match_payments(
    tenant_id: str = Query("default"),
    bank_account: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Automatically match unmatched payments to open items."""
    try:
        # Get unmatched payments (simplified - in production, query from payment_entries table)
        # For now, we'll match based on bank statement lines
        
        # Get unmatched bank statement lines (filter by bank_account via join with bank_statements)
        unmatched_query = text("""
            SELECT bsl.id, bsl.booking_date, bsl.amount, bsl.reference, bsl.remittance_info, bsl.creditor_name, bsl.debtor_name
            FROM domain_erp.bank_statement_lines bsl
            LEFT JOIN domain_erp.bank_statements bs ON bsl.statement_id = bs.id AND bs.tenant_id = bsl.tenant_id
            WHERE bsl.tenant_id = :tenant_id
            AND (bsl.status = 'UNMATCHED' OR bsl.status IS NULL)
            AND (:bank_account IS NULL OR bs.bank_account_id = :bank_account)
            ORDER BY bsl.booking_date DESC
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
            partner_name = creditor_name or debtor_name
            if partner_name:
                # Kunde per Name über die kanonische Schicht (Phase 2C).
                from app.services.business_partner_service import BusinessPartnerService

                customer_id = BusinessPartnerService(db, tenant_id).find_customer_id_by_name(partner_name)
            
            # Find matching open item
            op_query = text("""
                SELECT id, rechnungsnr, kunde_id, kunde_name, op_betrag, offen, faelligkeit, waehrung, op_status
                FROM domain_erp.offene_posten
                WHERE tenant_id = :tenant_id
                AND konto_typ = 'debitoren'
                AND op_status IN ('offen', 'teilweise')
                AND (
                    (:reference IS NOT NULL AND rechnungsnr ILIKE :reference_pattern)
                    OR (:customer_id IS NOT NULL AND kunde_id = :customer_id AND ABS(offen - :amount) < 0.01)
                )
                ORDER BY 
                    CASE WHEN rechnungsnr ILIKE :reference_pattern THEN 1 ELSE 2 END,
                    ABS(offen - :amount) ASC
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
                open_amount = Decimal(str(best_op[5] or 0))
                
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
                    UPDATE domain_erp.offene_posten
                    SET op_status = CASE WHEN (offen - :matched) <= 0.01 THEN 'geschlossen' ELSE 'teilweise' END,
                        offen = GREATEST(offen - :matched, 0),
                        updated_at = NOW()
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


@router.get("/match-suggestions/{payment_id}", response_model=List[OpenItemMatch], summary="Match suggestions abrufen")
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
        partner_name = creditor_name or debtor_name
        if partner_name:
            from app.services.business_partner_service import BusinessPartnerService

            customer_id = BusinessPartnerService(db, tenant_id).find_customer_id_by_name(partner_name)
        
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
            SELECT id, rechnungsnr, kunde_id, kunde_name, op_betrag, offen, faelligkeit, waehrung, op_status
            FROM domain_erp.offene_posten
            WHERE tenant_id = :tenant_id
            AND konto_typ = 'debitoren'
            AND op_status IN ('offen', 'teilweise')
            AND (
                (:reference_pattern IS NOT NULL AND rechnungsnr ILIKE :reference_pattern)
                OR (:customer_id IS NOT NULL AND kunde_id = :customer_id AND ABS(offen - :amount) < 10.00)
            )
            ORDER BY 
                CASE WHEN rechnungsnr ILIKE :reference_pattern THEN 1 ELSE 2 END,
                ABS(offen - :amount) ASC,
                faelligkeit ASC
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
                customer_id=str(r[2] or ""),
                customer_name=str(r[3] or ""),
                amount=Decimal(str(r[4])),
                open_amount=Decimal(str(r[5])),
                due_date=r[6],
                currency=str(r[7] or "EUR"),
                status=str(r[8] or "offen")
            )
            for r in op_results
        ]
        
    except Exception as e:
        logger.error(f"Error getting match suggestions: {e}")
        # Return empty list if error (table may not exist)
        return []

