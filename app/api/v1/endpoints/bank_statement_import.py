"""
Bank Statement Import API
FIBU-BNK-02: Kontoauszugsimport CAMT/MT940/CSV
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from pydantic import BaseModel
import xml.etree.ElementTree as ET
import csv
import io
import re
import logging
import hashlib
import json

from app.core.tenant import get_tenant_id
from app.core.validation_contracts import validate_iban
from ....core.database import get_db
from ....core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_bank_statement_import_datensatz,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bank-statements", tags=["finance", "bank-statements"])


class BankStatementLine(BaseModel):
    """Single line from bank statement"""
    line_number: int
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
    status: str = "UNMATCHED"  # UNMATCHED, MATCHED, PARTIAL
    errors: Optional[List[str]] = None


class BankStatementImportResult(BaseModel):
    """Result of bank statement import"""
    statement_id: str
    account_iban: str
    opening_balance: Decimal
    closing_balance: Decimal
    total_lines: int
    imported_lines: int
    error_lines: int
    lines: List[BankStatementLine]
    import_errors: Optional[List[str]] = None


def _build_bank_statement_import_datensatz(
    booking_date: object,
    value_date: object,
    amount: object,
    currency: object = "EUR",
    reference: object | None = None,
) -> dict:
    return {
        "booking_date": booking_date,
        "value_date": value_date,
        "amount": amount,
        "currency": currency or "EUR",
        "reference": reference,
    }


def _validate_bank_statement_import_datensatz(
    datensatz: dict,
    kontext_datensaetze: list[dict] | None = None,
) -> None:
    result = evaluate_bank_statement_import_datensatz(datensatz, kontext_datensaetze)
    if not result.bestanden:
        raise HTTPException(
            status_code=422,
            detail=build_dq_error_detail("KontoauszugImport", result),
        )


def _normalized_iban(value: str | None) -> str:
    return "".join((value or "").split()).upper()


def prepare_statement_import(db: Session, tenant_id: str, account_id: str,
                             format: str, content: bytes, entries: list[dict],
                             file_iban: str | None = None) -> tuple[str, str, dict | None]:
    """Validate the real account and serialize byte-identical imports across routes."""
    account = db.execute(text("""
        SELECT iban,currency FROM domain_erp.bank_accounts
        WHERE id=:id AND tenant_id=:tenant AND is_active IS TRUE FOR SHARE
    """), {"id": account_id, "tenant": tenant_id}).mappings().first()
    if account is None:
        raise HTTPException(status_code=404, detail="Active bank account not found")
    iban = _normalized_iban(account['iban'])
    if not iban or not validate_iban(iban).is_valid:
        raise HTTPException(status_code=409, detail="Bank account has no valid IBAN")
    if file_iban is not None:
        claimed_iban = _normalized_iban(file_iban)
        if not validate_iban(claimed_iban).is_valid or claimed_iban != iban:
            raise HTTPException(status_code=422, detail="Statement IBAN does not match selected bank account")
    currency = account['currency']
    if currency not in {'EUR', 'USD', 'CHF', 'GBP'}:
        raise HTTPException(status_code=409, detail="Bank account has no supported currency")
    if any(entry.get('currency', 'EUR') != currency for entry in entries):
        raise HTTPException(status_code=422, detail="Statement currency does not match bank account")
    context = json.dumps([tenant_id, account_id, format.upper()], separators=(',', ':')).encode()
    fingerprint = hashlib.sha256(context + b"\0" + content).hexdigest()
    statement_id = f"STMT-IMP-{fingerprint}"
    # Lock before the lookup: a SELECT FOR UPDATE cannot lock an absent row.
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
               {"key": f"bank-import:{statement_id}"})
    existing = db.execute(text("""
        SELECT id,tenant_id,bank_account_id,account_iban,opening_balance,closing_balance,
               total_lines,imported_lines,format,status
        FROM domain_erp.bank_statements WHERE id=:id FOR UPDATE
    """), {"id": statement_id}).mappings().first()
    if existing is not None:
        if (existing['tenant_id'] != tenant_id or existing['bank_account_id'] != account_id
                or existing['format'] != format.upper() or existing['account_iban'] != iban
                or existing['status'] != 'imported'):
            raise HTTPException(status_code=409, detail="Stored statement identity is inconsistent")
    return statement_id, iban, existing


def stored_statement_lines(db: Session, tenant_id: str, statement: dict) -> list[dict]:
    expected = statement['total_lines']
    if expected < 0 or statement['imported_lines'] != expected:
        raise HTTPException(status_code=409, detail="Stored import counts are inconsistent")
    rows = db.execute(text("""
        SELECT id,line_number,booking_date,value_date,amount,currency,reference,
               remittance_info,creditor_name,creditor_iban,debtor_name,debtor_iban,status,matched_op_id
        FROM domain_erp.bank_statement_lines
        WHERE statement_id=:id AND tenant_id=:tenant ORDER BY line_number,id
    """), {"id": statement['id'], "tenant": tenant_id}).mappings().fetchmany(expected + 1)
    if len(rows) != expected:
        raise HTTPException(status_code=409, detail="Stored import is incomplete")
    return rows


def parse_camt053(content: bytes) -> dict:
    """
    Parse CAMT.053 (Bank Statement) XML format.
    Returns dict with statement data.
    """
    try:
        root = ET.fromstring(content)
        
        # Register namespaces
        namespaces = {
            'camt': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'
        }
        
        if len(root.findall('.//camt:Stmt', namespaces)) != 1:
            raise ValueError('Exactly one CAMT statement is required per import')
        # Extract account info
        acct_elem = root.find('.//camt:Acct', namespaces)
        iban = acct_elem.find('.//camt:Id//camt:IBAN', namespaces)
        account_iban = iban.text if iban is not None else None
        
        # Extract balances
        bal_elem = root.find('.//camt:Bal', namespaces)
        opening_balance = Decimal("0.00")
        closing_balance = Decimal("0.00")
        
        if bal_elem is not None:
            amt_elem = bal_elem.find('.//camt:Amt', namespaces)
            if amt_elem is not None:
                opening_balance = Decimal(amt_elem.text)
        
        # Extract all entries
        entries = []
        ntry_elements = root.findall('.//camt:Ntry', namespaces)
        
        for idx, ntry in enumerate(ntry_elements):
            try:
                # Booking date
                bookg_date_elem = ntry.find('.//camt:BookgDt//camt:Dt', namespaces)
                booking_date = datetime.strptime(bookg_date_elem.text, '%Y-%m-%d').date() if bookg_date_elem is not None else date.today()
                
                # Value date
                val_date_elem = ntry.find('.//camt:ValDt//camt:Dt', namespaces)
                value_date = datetime.strptime(val_date_elem.text, '%Y-%m-%d').date() if val_date_elem is not None else booking_date
                
                # Amount
                amt_elem = ntry.find('.//camt:Amt', namespaces)
                amount = Decimal(amt_elem.text) if amt_elem is not None else Decimal("0.00")
                
                # Credit/Debit indicator
                cdt_dbt_ind = ntry.find('.//camt:CdtDbtInd', namespaces)
                if cdt_dbt_ind is not None and cdt_dbt_ind.text == 'DBIT':
                    amount = -amount
                
                # Reference
                ref_elem = ntry.find('.//camt:Refs//camt:AcctSvcrRef', namespaces)
                reference = ref_elem.text if ref_elem is not None else None
                
                # Remittance info
                rmt_inf_elem = ntry.find('.//camt:RmtInf//camt:Ustrd', namespaces)
                remittance_info = rmt_inf_elem.text if rmt_inf_elem is not None else None
                
                # Creditor/Debtor info
                creditor_name = None
                creditor_iban = None
                debtor_name = None
                debtor_iban = None
                
                cdtr_elem = ntry.find('.//camt:Cdtr', namespaces)
                if cdtr_elem is not None:
                    nm_elem = cdtr_elem.find('.//camt:Nm', namespaces)
                    creditor_name = nm_elem.text if nm_elem is not None else None
                    acct_elem = cdtr_elem.find('.//camt:Acct//camt:Id//camt:IBAN', namespaces)
                    creditor_iban = acct_elem.text if acct_elem is not None else None
                
                dbtr_elem = ntry.find('.//camt:Dbtr', namespaces)
                if dbtr_elem is not None:
                    nm_elem = dbtr_elem.find('.//camt:Nm', namespaces)
                    debtor_name = nm_elem.text if nm_elem is not None else None
                    acct_elem = dbtr_elem.find('.//camt:Acct//camt:Id//camt:IBAN', namespaces)
                    debtor_iban = acct_elem.text if acct_elem is not None else None
                
                entries.append({
                    'line_number': idx + 1,
                    'booking_date': booking_date,
                    'value_date': value_date,
                    'amount': amount,
                    'currency': amt_elem.get('Ccy', 'EUR') if amt_elem is not None else 'EUR',
                    'reference': reference,
                    'remittance_info': remittance_info,
                    'creditor_name': creditor_name,
                    'creditor_iban': creditor_iban,
                    'debtor_name': debtor_name,
                    'debtor_iban': debtor_iban
                })
            except Exception as e:
                raise ValueError(f"Failed to parse CAMT entry {idx + 1}: {str(e)}") from e
        
        # Calculate closing balance
        closing_balance = opening_balance + sum(entry['amount'] for entry in entries)
        
        return {
            'account_iban': account_iban,
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'entries': entries
        }
    except Exception as e:
        raise ValueError(f"Failed to parse CAMT.053: {str(e)}")


def parse_mt940(content: bytes) -> dict:
    """
    Parse MT940 (SWIFT) format.
    Returns dict with statement data.
    """
    try:
        text_content = content.decode('utf-8', errors='ignore')
        lines = text_content.split('\n')
        
        account_iban = None
        opening_balance = Decimal("0.00")
        closing_balance = Decimal("0.00")
        currency = "EUR"
        entries = []
        current_entry = {}
        line_number = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Account identification (IBAN)
            if line.startswith(':25:'):
                account_iban = line[4:].strip()
            
            # Opening balance
            elif line.startswith(':60F:') or line.startswith(':60M:'):
                # Format: :60F:CYYMMDDEUR1234,56
                balance_str = line[5:].strip()
                if len(balance_str) >= 10:
                    currency = balance_str[7:10].upper()
                    amount_str = balance_str[10:].replace(',', '.')
                    opening_balance = Decimal(amount_str)
            
            # Statement line
            elif line.startswith(':61:'):
                # Format: :61:YYMMDDMMDDD1234,56NTRFNONREF//1234567890
                # Parse date, amount, reference
                data = line[4:].strip()
                if len(data) >= 6:
                    try:
                        value_date = datetime.strptime(data[0:6], '%y%m%d').date()
                        booking_date = value_date
                        if len(data) >= 12:
                            booking_date = datetime.strptime(data[6:12], '%y%m%d').date()
                        
                        # Find amount (starts after dates, ends before transaction code)
                        amount_match = re.search(r'([\d,]+\.?\d*)', data[12:])
                        if amount_match:
                            amount_str = amount_match.group(1).replace(',', '.')
                            amount = Decimal(amount_str)
                            
                            # Check debit/credit indicator
                            if 'D' in data[12:20]:
                                amount = -amount
                            
                            # Extract reference (after //)
                            ref_match = re.search(r'//(.+)', data)
                            reference = ref_match.group(1) if ref_match else None
                            
                            line_number += 1
                            current_entry = {
                                'line_number': line_number,
                                'booking_date': booking_date,
                                'value_date': value_date,
                                'amount': amount,
                                'currency': currency,
                                'reference': reference,
                                'remittance_info': None
                            }
                    except Exception as e:
                        raise ValueError(f"Failed to parse MT940 line '{line}': {str(e)}") from e
            
            # Transaction details
            elif line.startswith(':86:') and current_entry:
                # Remittance info
                remittance_info = line[4:].strip()
                current_entry['remittance_info'] = remittance_info
                entries.append(current_entry)
                current_entry = {}
        
        # Calculate closing balance
        closing_balance = opening_balance + sum(entry['amount'] for entry in entries)
        
        return {
            'account_iban': account_iban,
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'entries': entries
        }
    except Exception as e:
        raise ValueError(f"Failed to parse MT940: {str(e)}")


def parse_csv(content: bytes) -> dict:
    """
    Parse CSV format.
    Expected columns: date, amount, reference, remittance_info, creditor_name, debtor_name
    """
    try:
        text_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(text_content))
        
        entries = []
        opening_balance = Decimal("0.00")
        closing_balance = Decimal("0.00")
        
        for idx, row in enumerate(csv_reader, start=2):
            date_str = row.get('date', row.get('datum', ''))
            value_date_str = row.get('value_date', row.get('valutadatum', date_str))
            amount_str = str(row.get('amount', row.get('betrag', '0'))).replace(',', '.')
            currency = row.get('currency', row.get('waehrung', 'EUR'))

            try:
                booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                value_date = datetime.strptime(value_date_str, '%Y-%m-%d').date()
                amount = Decimal(amount_str)
            except Exception as e:
                raise ValueError(f"Failed to parse CSV row {idx}: {str(e)}") from e

            reference = row.get('reference', row.get('referenz', ''))
            remittance_info = row.get('remittance_info', row.get('verwendungszweck', ''))
            creditor_name = row.get('creditor_name', row.get('empfaenger', ''))
            debtor_name = row.get('debtor_name', row.get('auftraggeber', ''))

            entries.append({
                'line_number': idx - 1,
                'booking_date': booking_date,
                'value_date': value_date,
                'amount': amount,
                'currency': currency or "EUR",
                'reference': reference,
                'remittance_info': remittance_info,
                'creditor_name': creditor_name,
                'debtor_iban': None,
                'debtor_name': debtor_name,
                'creditor_iban': None
            })

        dq_context = [
            _build_bank_statement_import_datensatz(
                booking_date=entry['booking_date'].isoformat(),
                value_date=entry['value_date'].isoformat(),
                amount=entry['amount'],
                currency=entry.get('currency', 'EUR'),
                reference=entry.get('reference'),
            )
            for entry in entries
        ]
        for current_datensatz in dq_context:
            _validate_bank_statement_import_datensatz(current_datensatz, dq_context)

        # Calculate closing balance (if opening balance provided)
        if entries:
            closing_balance = opening_balance + sum(entry['amount'] for entry in entries)
        
        return {
            'account_iban': None,  # CSV doesn't always have IBAN
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'entries': entries
        }
    except HTTPException:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}")


@router.post("/import", response_model=BankStatementImportResult, summary="Bank statement importieren")
async def import_bank_statement(
    file: UploadFile = File(...),
    format: str = Query(..., description="File format: CAMT, MT940, or CSV"),
    bank_account_id: str = Query(..., description="Bank account ID"),
    tenant_id: str = Depends(get_tenant_id),
    auto_match: bool = Query(False, description="Auto-match transactions"),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Import bank statement from CAMT.053, MT940, or CSV file.
    """
    db_started = False
    try:
        content = await file.read()
        
        # Parse based on format
        if format.upper() == 'CAMT':
            parsed = parse_camt053(content)
        elif format.upper() == 'MT940':
            parsed = parse_mt940(content)
        elif format.upper() == 'CSV':
            parsed = parse_csv(content)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        dq_context = [
            _build_bank_statement_import_datensatz(
                booking_date=entry.get('booking_date').isoformat() if hasattr(entry.get('booking_date'), 'isoformat') else entry.get('booking_date'),
                value_date=entry.get('value_date').isoformat() if hasattr(entry.get('value_date'), 'isoformat') else entry.get('value_date'),
                amount=entry.get('amount'),
                currency=entry.get('currency', 'EUR'),
                reference=entry.get('reference'),
            )
            for entry in parsed['entries']
        ]

        for entry, current_datensatz in zip(parsed['entries'], dq_context):
            _validate_bank_statement_import_datensatz(current_datensatz, dq_context)
            amount = Decimal(str(entry['amount']))
            try:
                exact_cents = amount.is_finite() and amount == amount.quantize(Decimal("0.01"))
            except InvalidOperation:
                exact_cents = False
            if not exact_cents:
                raise HTTPException(status_code=422, detail="Amount must be finite and use at most two decimal places")
            if entry.get('currency', 'EUR') not in {"EUR", "USD", "CHF", "GBP"}:
                raise HTTPException(status_code=422, detail="Unsupported currency")

        db_started = True
        statement_id, account_iban, existing = prepare_statement_import(
            db, tenant_id, bank_account_id, format, content, parsed['entries'],
            None if format.upper() == 'CSV' else parsed['account_iban'] or '')
        parsed['account_iban'] = account_iban
        if existing is not None:
            stored = stored_statement_lines(db, tenant_id, existing)
            result = BankStatementImportResult(
                statement_id=statement_id, account_iban=account_iban,
                opening_balance=existing['opening_balance'], closing_balance=existing['closing_balance'],
                total_lines=existing['total_lines'], imported_lines=existing['imported_lines'],
                error_lines=0, lines=[BankStatementLine(**row) for row in stored], import_errors=None,
            )
            db.commit()  # Release the import lock; replay does not match or write again.
            return result
        # Persist the complete statement in the same transaction as its identity.
        db.execute(text("""
            INSERT INTO domain_erp.bank_statements
            (id, tenant_id, bank_account_id, account_iban, statement_date, opening_balance,
             closing_balance, format, total_lines, imported_lines, status, created_at, updated_at)
            VALUES (:id, :tenant_id, :account_id, :iban, :date, :opening, :closing,
                    :format, :total, :imported, :status, NOW(), NOW())
        """), {
            "id": statement_id, "tenant_id": tenant_id, "account_id": bank_account_id,
            "iban": parsed['account_iban'], "date": date.today(),
            "opening": parsed['opening_balance'], "closing": parsed['closing_balance'],
            "format": format.upper(), "total": len(parsed['entries']),
            "imported": len(parsed['entries']), "status": "imported",
        })
        imported_lines = []
        for entry in parsed['entries']:
            db.execute(text("""
                INSERT INTO domain_erp.bank_statement_lines
                (id, tenant_id, statement_id, line_number, booking_date, value_date,
                 amount, currency, reference, remittance_info, creditor_name, creditor_iban,
                 debtor_name, debtor_iban, status, created_at, updated_at)
                VALUES (:id, :tenant_id, :statement_id, :line_num, :book_date, :val_date,
                        :amount, :currency, :reference, :remittance, :creditor_name, :creditor_iban,
                        :debtor_name, :debtor_iban, :status, NOW(), NOW())
            """), {
                "id": f"{statement_id}-L{entry['line_number']}", "tenant_id": tenant_id,
                "statement_id": statement_id, "line_num": entry['line_number'],
                "book_date": entry['booking_date'], "val_date": entry['value_date'],
                "amount": entry['amount'], "currency": entry.get('currency', 'EUR'),
                "reference": entry.get('reference'), "remittance": entry.get('remittance_info'),
                "creditor_name": entry.get('creditor_name'), "creditor_iban": entry.get('creditor_iban'),
                "debtor_name": entry.get('debtor_name'), "debtor_iban": entry.get('debtor_iban'),
                "status": "UNMATCHED",
            })
            imported_lines.append(BankStatementLine(**entry, status="UNMATCHED"))
        if auto_match:
            from app.api.v1.endpoints.payment_matching import match_statement_lines

            matches = match_statement_lines(db, tenant_id, statement_id=statement_id, request=request)
            matched_ids = {match.payment_id for match in matches}
            for entry, line in zip(parsed['entries'], imported_lines):
                if f"{statement_id}-L{entry['line_number']}" in matched_ids:
                    line.status = "MATCHED"
        # Validate the response before committing so serialization errors cannot
        # turn a committed import into a failed request.
        result = BankStatementImportResult(
            statement_id=statement_id, account_iban=parsed['account_iban'] or '',
            opening_balance=parsed['opening_balance'], closing_balance=parsed['closing_balance'],
            total_lines=len(parsed['entries']), imported_lines=len(imported_lines),
            error_lines=0, lines=imported_lines, import_errors=None,
        )
        db.commit()

        return result

    except HTTPException:
        if db_started:
            db.rollback()
        raise
    except ValueError as e:
        if db_started:
            db.rollback()
            logger.exception("Failed to construct bank statement import")
            raise HTTPException(status_code=500, detail="Failed to import bank statement") from e
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing bank statement: {e}")
        raise HTTPException(status_code=500, detail="Failed to import bank statement")


@router.get("/{statement_id}/lines", response_model=List[BankStatementLine], summary="Statement lines abrufen")
async def get_statement_lines(
    statement_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get all lines for a bank statement."""
    try:
        query = text("""
            SELECT line_number, booking_date, value_date, amount, currency, reference,
                   remittance_info, creditor_name, creditor_iban, debtor_name, debtor_iban, status
            FROM domain_erp.bank_statement_lines
            WHERE statement_id = :statement_id AND tenant_id = :tenant_id
            ORDER BY line_number
        """)
        
        rows = db.execute(query, {
            "statement_id": statement_id,
            "tenant_id": tenant_id
        }).fetchall()
        
        return [
            BankStatementLine(
                line_number=row[0],
                booking_date=row[1],
                value_date=row[2],
                amount=Decimal(str(row[3])),
                currency=row[4] or "EUR",
                reference=row[5],
                remittance_info=row[6],
                creditor_name=row[7],
                creditor_iban=row[8],
                debtor_name=row[9],
                debtor_iban=row[10],
                status=row[11] or "UNMATCHED"
            )
            for row in rows
        ]
    except Exception as e:
        # SPEC-P0-03: Finance darf bei DB-Fehlern nie still leere Daten liefern.
        from app.core.critical_data_path import raise_critical_data_unavailable

        logger.error("Error fetching statement lines: %s", e)
        raise_critical_data_unavailable(
            endpoint="bank_statement_lines",
            exc=e,
            label="Kontoauszugszeilen",
        )

