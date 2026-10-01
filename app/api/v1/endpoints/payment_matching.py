"""
Payment Matching API
FIBU-AR-03: Zahlungseingänge & Matching
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
import logging
import csv
import io
import re
import json

from app.core.tenant import get_tenant_id
from app.documents.repository import DocumentRepository
from app.core.database import get_db
from app.core.uuid7 import uuid7
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
    tenant_id: str = Depends(get_tenant_id),
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
                dq_context[row_number - 2],
                dq_context,
            )
            if not dq_result.bestanden:
                raise HTTPException(
                    status_code=422,
                    detail=build_dq_error_detail("Zahlungsimport", dq_result),
                )

            if any(violation.regel_id == "PI-004" for violation in dq_result.verletzungen):
                raise HTTPException(status_code=422, detail=f"Unsupported payment currency in CSV row {row_number}")

            try:
                booking_date = datetime.strptime(booking_date_raw, '%Y-%m-%d').date()
                amount = Decimal(amount_raw)
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Failed to parse CSV row {row_number}: {str(e)}") from e

            if not amount.is_finite() or amount != amount.quantize(Decimal("0.01")):
                raise HTTPException(status_code=422, detail=f"Payment amount in CSV row {row_number} must use at most two decimal places")

            reference = row.get('reference', '')
            remittance_info = row.get('remittance_info', '')
            entries.append({
                "booking_date": booking_date,
                "amount": amount,
                "currency": currency or "EUR",
                "reference": reference,
                "remittance_info": remittance_info,
            })

        if not entries:
            return []

        statement_id = f"STMT-CSV-{uuid7()}"
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
        line_ins = text("""
            INSERT INTO domain_erp.bank_statement_lines
            (id, tenant_id, statement_id, line_number, booking_date, value_date,
             amount, currency, reference, remittance_info, creditor_name, creditor_iban,
             debtor_name, debtor_iban, status, created_at, updated_at)
            VALUES (:id, :tenant_id, :statement_id, :line_num, :book_date, :val_date,
                    :amount, :currency, :reference, :remittance, NULL, NULL, NULL, NULL, 'UNMATCHED', NOW(), NOW())
        """)
        result_entries: list[PaymentEntry] = []
        for idx, e in enumerate(entries):
            line_id = f"{statement_id}-L{idx + 1}"
            db.execute(line_ins, {
                "id": line_id,
                "tenant_id": tenant_id,
                "statement_id": statement_id,
                "line_num": idx + 1,
                "book_date": e["booking_date"],
                "val_date": e["booking_date"],
                "amount": e["amount"],
                "currency": e["currency"],
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
                currency=e["currency"],
                reference=e["reference"],
                remittance_info=e["remittance_info"],
                match_status="UNMATCHED",
            ))
        db.commit()
        logger.info(f"Imported {len(result_entries)} payments from CSV into bank_statement_lines")
        return result_entries

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to import CSV")


@router.get("/unmatched", response_model=List[PaymentEntry], summary="Unmatched payments abrufen")
async def get_unmatched_payments(
    tenant_id: str = Depends(get_tenant_id),
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
        # SPEC-P0-03: Finance darf bei DB-Fehlern nie still leere Daten liefern.
        from app.core.critical_data_path import raise_critical_data_unavailable

        logger.error("get_unmatched_payments failed: %s", e)
        raise_critical_data_unavailable(
            endpoint="payments_unmatched",
            exc=e,
            label="Unmatched-Zahlungen",
        )


@router.get("/open-items/{customer_id}", response_model=List[OpenItemMatch], summary="Open items for matching abrufen")
async def get_open_items_for_matching(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get open AR items for a customer for payment matching."""
    try:
        query = """
            SELECT 
                id, rechnungsnr, kunde_id, kunde_name,
                betrag, offen, faelligkeit, waehrung, op_status
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
        # SPEC-P0-03: Finance darf bei DB-Fehlern nie still leere Daten liefern.
        from app.core.critical_data_path import raise_critical_data_unavailable

        logger.error("Error fetching open items for matching: %s", e)
        raise_critical_data_unavailable(
            endpoint="payments_open_items_match",
            exc=e,
            label="Offene Posten fuer Matching",
        )


def _lock_matching_tenant(db: Session, tenant_id: str) -> None:
    # All three writers use the same transaction lock before reading candidates.
    # Row locks still protect OP against payment-run/other settlement writers.
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
               {"key": f"bank-matching:{tenant_id}"})


def _apply_bank_line_match(db: Session, tenant_id: str, line: dict, op_id: str,
                           request: Request | None = None) -> MatchResult:
    op = db.execute(text("""
        SELECT id,rechnungsnr,konto_typ,offen,waehrung,op_status
        FROM domain_erp.offene_posten
        WHERE id=:op_id AND tenant_id=:tenant FOR UPDATE
    """), {"op_id": op_id, "tenant": tenant_id}).mappings().first()
    if op is None:
        raise HTTPException(status_code=404, detail="Open item not found")
    amount = abs(Decimal(str(line['amount'])))
    if line['status'] == 'MATCHED':
        if line['matched_op_id'] != op_id:
            raise HTTPException(status_code=409, detail="Payment already assigned to another open item")
        return MatchResult(payment_id=line['id'], matched_op_id=op_id,
            match_type="FULL" if Decimal(str(op['offen'])) == 0 else "PARTIAL",
            matched_amount=amount, remaining_amount=Decimal("0"), confidence=1,
            match_reason="Already matched")
    if line['status'] not in (None, 'UNMATCHED') or line['matched_op_id']:
        raise HTTPException(status_code=409, detail="Payment has an existing or incomplete assignment")
    if not amount.is_finite():
        raise HTTPException(status_code=409, detail="Payment amount must be finite")
    direction = 'debitoren' if Decimal(str(line['amount'])) > 0 else 'kreditoren'
    if amount == 0 or op['konto_typ'] != direction or op['waehrung'] != line['currency']:
        raise HTTPException(status_code=409, detail="Payment direction or currency does not match open item")
    open_amount = Decimal(str(op['offen']))
    if op['op_status'] not in ('offen', 'teilweise') or amount > open_amount:
        raise HTTPException(status_code=409, detail="Payment exceeds or cannot settle this open item")
    remaining_open = open_amount - amount
    if remaining_open == 0 and op['rechnungsnr']:
        doc_type = 'sales_invoice' if direction == 'debitoren' else 'ap_invoice'
        document = db.execute(text("""
            SELECT data FROM documents
            WHERE doc_type=:kind AND doc_number=:number FOR UPDATE
        """), {"kind": doc_type, "number": op['rechnungsnr']}).scalar_one_or_none()
        if document is not None:
            tenants = [document[key] for key in ('tenantId', 'tenant_id') if document.get(key)]
            if not tenants or any(value != tenant_id for value in tenants):
                raise HTTPException(status_code=409, detail="Invoice tenant cannot be verified")
            if document.get('status') in ('STORNIERT', 'GUTGESCHRIEBEN'):
                raise HTTPException(status_code=409, detail="Cancelled or credited invoice cannot be settled")
            document = dict(document)
            document['status'] = 'BEZAHLT'
            DocumentRepository(db).save_document(doc_type, op['rechnungsnr'], document, commit=False)
    updated = db.execute(text("""
        UPDATE domain_erp.offene_posten
        SET offen=offen-:amount,
            op_status=CASE WHEN offen=:amount THEN 'geschlossen' ELSE 'teilweise' END,
            zahlbar=CASE WHEN offen=:amount THEN FALSE ELSE zahlbar END,
            updated_at=NOW()
        WHERE id=:op_id AND tenant_id=:tenant
          AND op_status IN ('offen','teilweise') AND offen>=:amount
          AND konto_typ=:direction AND waehrung=:currency
        RETURNING id
    """), {"op_id": op_id, "tenant": tenant_id, "amount": amount,
            "direction": direction, "currency": line['currency']}).first()
    if updated is None:
        raise HTTPException(status_code=409, detail="Open item changed during matching")
    assigned = db.execute(text("""
        UPDATE domain_erp.bank_statement_lines
        SET status='MATCHED', matched_op_id=:op_id, updated_at=NOW()
        WHERE id=:line_id AND tenant_id=:tenant AND matched_op_id IS NULL
          AND (status IS NULL OR status='UNMATCHED')
        RETURNING id
    """), {"op_id": op_id, "line_id": line['id'], "tenant": tenant_id}).first()
    if assigned is None:
        raise HTTPException(status_code=409, detail="Payment changed during matching")
    # Financial evidence is mandatory and shares the settlement transaction.
    # Identity comes from verified claims attached by the security dependency,
    # never from an unverified X-User-ID header.
    claims = getattr(request.state, 'token_claims', {}) if request is not None else {}
    actor = claims.get('sub') or '00000000-0000-0000-0000-000000000001'
    db.execute(text("""
        INSERT INTO domain_shared.audit_logs
        (id,user_id,user_email,tenant_id,action,entity_type,entity_id,changes)
        VALUES (:id,:actor,:email,:tenant,'match_bank_payment','bank_statement_line',
                :payment,CAST(:changes AS jsonb))
    """), {"id": str(uuid7()), "actor": actor, "email": 'bank-matching@internal',
            "tenant": tenant_id, "payment": line['id'], "changes": json.dumps({
                "op_id": op_id, "invoice_number": op['rechnungsnr'],
                "previous_open_amount": str(open_amount), "matched_amount": str(amount),
                "new_open_amount": str(remaining_open), "currency": line['currency'],
                "signed_bank_amount": str(line['amount']),
            })})
    return MatchResult(payment_id=line['id'], matched_op_id=op_id,
        match_type="FULL" if remaining_open == 0 else "PARTIAL", matched_amount=amount,
        remaining_amount=Decimal("0"), confidence=1, match_reason="Verified bank payment")


def match_statement_lines(db: Session, tenant_id: str,
                          bank_account: str | None = None, statement_id: str | None = None,
                          request: Request | None = None) -> list[MatchResult]:
    """Bounded automatic matching; transaction and commit belong to the caller."""
    _lock_matching_tenant(db, tenant_id)
    lines = db.execute(text("""
        SELECT bsl.id,bsl.amount,bsl.currency,bsl.reference,bsl.remittance_info,
               bsl.status,bsl.matched_op_id
        FROM domain_erp.bank_statement_lines bsl
        JOIN domain_erp.bank_statements bs ON bs.id=bsl.statement_id AND bs.tenant_id=bsl.tenant_id
        WHERE bsl.tenant_id=:tenant AND (bsl.status IS NULL OR bsl.status='UNMATCHED')
          AND bsl.matched_op_id IS NULL
          AND (:account IS NULL OR bs.bank_account_id=:account)
          AND (:statement IS NULL OR bs.id=:statement)
        ORDER BY bsl.id LIMIT 100 FOR UPDATE OF bsl
    """), {"tenant": tenant_id, "account": bank_account, "statement": statement_id}).mappings().fetchmany(100)
    results = []
    for line in lines:
        amount = Decimal(str(line['amount']))
        if amount == 0:
            continue
        texts = [value for value in (line['reference'], line['remittance_info']) if value]
        if any(len(value) > 4096 for value in texts):
            continue
        references = set(texts)
        for value in texts:
            references.update(re.findall(r"[A-Za-z0-9]+(?:[-_/.][A-Za-z0-9]+)*", value))
        if not references or len(references) > 128:
            continue
        candidates = db.execute(text("""
            SELECT id,offen FROM domain_erp.offene_posten
            WHERE tenant_id=:tenant AND konto_typ=:direction AND waehrung=:currency
              AND op_status IN ('offen','teilweise') AND offen>0
              AND rechnungsnr=ANY(:references)
            ORDER BY id LIMIT 2 FOR UPDATE
        """), {"tenant": tenant_id, "direction": 'debitoren' if amount > 0 else 'kreditoren',
                "currency": line['currency'], "references": sorted(references)}).mappings().fetchmany(2)
        # Never pick the first plausible OP or allocate an untracked overpayment.
        if len(candidates) != 1 or abs(amount) > Decimal(str(candidates[0]['offen'])):
            continue
        results.append(_apply_bank_line_match(db, tenant_id, line, candidates[0]['id'], request=request))
    return results


@router.post("/match/{payment_id}", response_model=MatchResult, summary="Payment match")
async def match_payment(
    payment_id: str,
    op_id: Optional[str] = Query(None),
    match_type: str = Query("AUTO"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Assign a real tenant-owned bank payment exactly once."""
    if not op_id:
        raise HTTPException(status_code=400, detail="op_id is required for matching")
    try:
        _lock_matching_tenant(db, tenant_id)
        line = db.execute(text("""
            SELECT bsl.id,bsl.amount,bsl.currency,bsl.status,bsl.matched_op_id
            FROM domain_erp.bank_statement_lines bsl
            JOIN domain_erp.bank_statements bs ON bs.id=bsl.statement_id AND bs.tenant_id=bsl.tenant_id
            WHERE bsl.id=:payment AND bsl.tenant_id=:tenant FOR UPDATE OF bsl
        """), {"payment": payment_id, "tenant": tenant_id}).mappings().first()
        if line is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        result = _apply_bank_line_match(db, tenant_id, line, op_id, request=request)
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to match bank payment")
        raise HTTPException(status_code=500, detail="Failed to match payment") from exc


@router.post("/auto-match", response_model=List[MatchResult], summary="Match payments auto")
async def auto_match_payments(
    tenant_id: str = Depends(get_tenant_id),
    bank_account: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Match only unambiguous real bank payments in the tenant transaction."""
    try:
        results = match_statement_lines(db, tenant_id, bank_account=bank_account, request=request)
        db.commit()
        return results
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to auto-match bank payments")
        raise HTTPException(status_code=500, detail="Failed to auto-match payments") from exc


@router.get("/match-suggestions/{payment_id}", response_model=List[OpenItemMatch], summary="Match suggestions abrufen")
async def get_match_suggestions(
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id),
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
            SELECT id, rechnungsnr, kunde_id, kunde_name, betrag, offen, faelligkeit, waehrung, op_status
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
        # SPEC-P0-03: Finance darf bei DB-Fehlern nie still leere Daten liefern.
        from app.core.critical_data_path import raise_critical_data_unavailable

        logger.error("Error getting match suggestions: %s", e)
        raise_critical_data_unavailable(
            endpoint="payments_match_suggestions",
            exc=e,
            label="Matching-Vorschlaege",
        )

