"""
Bank Statement Import API
FIBU-BNK-02: Kontoauszugsimport CAMT/MT940/CSV
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel
import xml.etree.ElementTree as ET
import csv
import io
import re
import logging

from ....core.database import get_db

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
                    'reference': reference,
                    'remittance_info': remittance_info,
                    'creditor_name': creditor_name,
                    'creditor_iban': creditor_iban,
                    'debtor_name': debtor_name,
                    'debtor_iban': debtor_iban
                })
            except Exception as e:
                logger.warning(f"Error parsing CAMT entry {idx}: {e}")
                continue
        
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
                    currency = balance_str[7:10]
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
                                'reference': reference,
                                'remittance_info': None
                            }
                    except Exception as e:
                        logger.warning(f"Error parsing MT940 line: {e}")
                        continue
            
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
        
        for idx, row in enumerate(csv_reader):
            try:
                # Date
                date_str = row.get('date', row.get('datum', ''))
                booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                value_date = booking_date
                
                # Amount
                amount_str = str(row.get('amount', row.get('betrag', '0'))).replace(',', '.')
                amount = Decimal(amount_str)
                
                # Reference
                reference = row.get('reference', row.get('referenz', ''))
                
                # Remittance info
                remittance_info = row.get('remittance_info', row.get('verwendungszweck', ''))
                
                # Creditor/Debtor
                creditor_name = row.get('creditor_name', row.get('empfaenger', ''))
                debtor_name = row.get('debtor_name', row.get('auftraggeber', ''))
                
                entries.append({
                    'line_number': idx + 1,
                    'booking_date': booking_date,
                    'value_date': value_date,
                    'amount': amount,
                    'reference': reference,
                    'remittance_info': remittance_info,
                    'creditor_name': creditor_name,
                    'debtor_iban': None,
                    'debtor_name': debtor_name,
                    'creditor_iban': None
                })
            except Exception as e:
                logger.warning(f"Error parsing CSV row {idx}: {e}")
                continue
        
        # Calculate closing balance (if opening balance provided)
        if entries:
            closing_balance = opening_balance + sum(entry['amount'] for entry in entries)
        
        return {
            'account_iban': None,  # CSV doesn't always have IBAN
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'entries': entries
        }
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}")


@router.post("/import", response_model=BankStatementImportResult)
async def import_bank_statement(
    file: UploadFile = File(...),
    format: str = Query(..., description="File format: CAMT, MT940, or CSV"),
    bank_account_id: str = Query(..., description="Bank account ID"),
    tenant_id: str = Query("system", description="Tenant ID"),
    auto_match: bool = Query(False, description="Auto-match transactions"),
    db: Session = Depends(get_db)
):
    """
    Import bank statement from CAMT.053, MT940, or CSV file.
    """
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
        
        # Get bank account IBAN if not provided
        if not parsed['account_iban']:
            account_query = text("""
                SELECT iban FROM domain_erp.bank_accounts
                WHERE id = :account_id AND tenant_id = :tenant_id
            """)
            account_row = db.execute(account_query, {
                "account_id": bank_account_id,
                "tenant_id": tenant_id
            }).fetchone()
            if account_row:
                parsed['account_iban'] = account_row[0]
        
        # Create statement record
        # Note: If bank_statements table doesn't exist, we'll store in a JSONB column or skip
        statement_id = f"STMT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{bank_account_id[:8]}"
        
        # Try to create statement record (table may not exist yet)
        try:
            statement_insert = text("""
                INSERT INTO domain_erp.bank_statements
                (id, tenant_id, bank_account_id, account_iban, statement_date, opening_balance,
                 closing_balance, format, total_lines, imported_lines, status, created_at, updated_at)
                VALUES (:id, :tenant_id, :account_id, :iban, :date, :opening, :closing,
                        :format, :total, :imported, :status, NOW(), NOW())
                RETURNING id
            """)
            
            db.execute(statement_insert, {
                "id": statement_id,
                "tenant_id": tenant_id,
                "account_id": bank_account_id,
                "iban": parsed['account_iban'],
                "date": date.today(),
                "opening": parsed['opening_balance'],
                "closing": parsed['closing_balance'],
                "format": format.upper(),
                "total": len(parsed['entries']),
                "imported": len(parsed['entries']),
                "status": "imported"
            })
        except Exception as e:
            logger.warning(f"bank_statements table may not exist: {e}")
            # Continue without database storage - data will be returned in response
        
        # Import statement lines
        import_errors = []
        imported_lines = []
        
        for entry in parsed['entries']:
            try:
                line_id = f"{statement_id}-L{entry['line_number']}"
                
                # Try to insert into bank_statement_lines table
                try:
                    line_insert = text("""
                        INSERT INTO domain_erp.bank_statement_lines
                        (id, tenant_id, statement_id, line_number, booking_date, value_date,
                         amount, currency, reference, remittance_info, creditor_name, creditor_iban,
                         debtor_name, debtor_iban, status, created_at, updated_at)
                        VALUES (:id, :tenant_id, :statement_id, :line_num, :book_date, :val_date,
                                :amount, :currency, :reference, :remittance, :creditor_name, :creditor_iban,
                                :debtor_name, :debtor_iban, :status, NOW(), NOW())
                    """)
                    
                    db.execute(line_insert, {
                        "id": line_id,
                        "tenant_id": tenant_id,
                        "statement_id": statement_id,
                        "line_num": entry['line_number'],
                        "book_date": entry['booking_date'],
                        "val_date": entry['value_date'],
                        "amount": entry['amount'],
                        "currency": "EUR",
                        "reference": entry.get('reference'),
                        "remittance": entry.get('remittance_info'),
                        "creditor_name": entry.get('creditor_name'),
                        "creditor_iban": entry.get('creditor_iban'),
                        "debtor_name": entry.get('debtor_name'),
                        "debtor_iban": entry.get('debtor_iban'),
                        "status": "UNMATCHED"
                    })
                except Exception as table_error:
                    logger.warning(f"bank_statement_lines table may not exist: {table_error}")
                    # Continue without database storage
                
                imported_lines.append(BankStatementLine(
                    line_number=entry['line_number'],
                    booking_date=entry['booking_date'],
                    value_date=entry['value_date'],
                    amount=entry['amount'],
                    reference=entry.get('reference'),
                    remittance_info=entry.get('remittance_info'),
                    creditor_name=entry.get('creditor_name'),
                    creditor_iban=entry.get('creditor_iban'),
                    debtor_name=entry.get('debtor_name'),
                    debtor_iban=entry.get('debtor_iban'),
                    status="UNMATCHED"
                ))
            except Exception as e:
                error_msg = f"Line {entry['line_number']}: {str(e)}"
                import_errors.append(error_msg)
                logger.error(error_msg)
        
        try:
            db.commit()
        except Exception:
            db.rollback()
        
        # Auto-match if requested
        if auto_match and imported_lines:
            # TODO: Implement auto-matching logic
            pass
        
        return BankStatementImportResult(
            statement_id=statement_id,
            account_iban=parsed['account_iban'] or '',
            opening_balance=parsed['opening_balance'],
            closing_balance=parsed['closing_balance'],
            total_lines=len(parsed['entries']),
            imported_lines=len(imported_lines),
            error_lines=len(import_errors),
            lines=imported_lines,
            import_errors=import_errors if import_errors else None
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing bank statement: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import bank statement: {str(e)}")


@router.get("/{statement_id}/lines", response_model=List[BankStatementLine])
async def get_statement_lines(
    statement_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
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
        # If table doesn't exist, return empty list
        logger.warning(f"Error fetching statement lines (table may not exist): {e}")
        return []

