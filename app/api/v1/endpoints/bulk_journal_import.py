"""
Bulk Journal Entry Import API
FIBU-GL-04: Sammel-/Massenbuchungen Import
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
import csv
import io
import logging
import uuid

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bulk-journal-import", tags=["finance", "import"])


class ImportError(BaseModel):
    """Import error for a single row"""
    row_number: int
    field: Optional[str] = None
    error_message: str
    row_data: Dict[str, Any]


class ImportResult(BaseModel):
    """Result of bulk import"""
    total_rows: int
    successful: int
    failed: int
    errors: List[ImportError]
    created_entry_ids: List[str]
    import_id: str
    imported_at: datetime


class JournalEntryImportRow(BaseModel):
    """Single journal entry row from import"""
    entry_date: date
    entry_number: Optional[str] = None
    description: str
    account_number: str
    debit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    reference: Optional[str] = None

    @field_validator('debit_amount', 'credit_amount')
    @classmethod
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v


def parse_csv_file(file_content: bytes, delimiter: str = ',') -> List[Dict[str, Any]]:
    """Parse CSV file content"""
    try:
        # Try to detect encoding
        content = file_content.decode('utf-8-sig')  # Handle BOM
        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        rows = []
        for row in reader:
            # Clean up keys (remove BOM, whitespace)
            cleaned_row = {k.strip().strip('\ufeff'): v.strip() if v else '' for k, v in row.items()}
            rows.append(cleaned_row)
        return rows
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")


def validate_and_parse_row(row_data: Dict[str, Any], row_number: int) -> tuple[Optional[JournalEntryImportRow], Optional[ImportError]]:
    """Validate and parse a single import row"""
    errors = []
    
    # Required fields
    if 'entry_date' not in row_data and 'buchungsdatum' not in row_data:
        return None, ImportError(
            row_number=row_number,
            field='entry_date',
            error_message='Missing required field: entry_date or buchungsdatum',
            row_data=row_data
        )
    
    if 'account_number' not in row_data and 'konto' not in row_data:
        return None, ImportError(
            row_number=row_number,
            field='account_number',
            error_message='Missing required field: account_number or konto',
            row_data=row_data
        )
    
    if 'description' not in row_data and 'buchungstext' not in row_data:
        return None, ImportError(
            row_number=row_number,
            field='description',
            error_message='Missing required field: description or buchungstext',
            row_data=row_data
        )
    
    # Parse date
    date_str = row_data.get('entry_date') or row_data.get('buchungsdatum', '')
    try:
        # Try different date formats
        if len(date_str) == 10:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        elif len(date_str) == 8:
            entry_date = datetime.strptime(date_str, '%Y%m%d').date()
        else:
            entry_date = datetime.strptime(date_str, '%d.%m.%Y').date()
    except ValueError:
        return None, ImportError(
            row_number=row_number,
            field='entry_date',
            error_message=f'Invalid date format: {date_str}. Expected YYYY-MM-DD, YYYYMMDD, or DD.MM.YYYY',
            row_data=row_data
        )
    
    # Parse amounts
    debit_str = row_data.get('debit_amount') or row_data.get('soll', '0')
    credit_str = row_data.get('credit_amount') or row_data.get('haben', '0')
    
    try:
        debit_amount = Decimal(str(debit_str).replace(',', '.')) if debit_str else Decimal("0.00")
        credit_amount = Decimal(str(credit_str).replace(',', '.')) if credit_str else Decimal("0.00")
    except (InvalidOperation, ValueError):
        return None, ImportError(
            row_number=row_number,
            field='amount',
            error_message=f'Invalid amount format: debit={debit_str}, credit={credit_str}',
            row_data=row_data
        )
    
    # At least one amount must be > 0
    if debit_amount == Decimal("0.00") and credit_amount == Decimal("0.00"):
        return None, ImportError(
            row_number=row_number,
            field='amount',
            error_message='Either debit_amount or credit_amount must be greater than 0',
            row_data=row_data
        )
    
    account_number = row_data.get('account_number') or row_data.get('konto', '')
    description = row_data.get('description') or row_data.get('buchungstext', '')
    
    entry = JournalEntryImportRow(
        entry_date=entry_date,
        entry_number=row_data.get('entry_number') or row_data.get('belegnummer'),
        description=description,
        account_number=account_number,
        debit_amount=debit_amount,
        credit_amount=credit_amount,
        tax_code=row_data.get('tax_code') or row_data.get('steuerschluessel'),
        cost_center=row_data.get('cost_center') or row_data.get('kostenstelle'),
        profit_center=row_data.get('profit_center') or row_data.get('kostentraeger'),
        reference=row_data.get('reference') or row_data.get('beleg')
    )
    
    return entry, None


@router.post("/csv", response_model=ImportResult)
async def import_journal_entries_csv(
    file: UploadFile = File(...),
    period: str = Query(..., description="Accounting period (YYYY-MM)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    delimiter: str = Query(",", description="CSV delimiter"),
    dry_run: bool = Query(False, description="Dry run mode (validate only, don't import)"),
    db: Session = Depends(get_db)
):
    """
    Import journal entries from CSV file.
    
    Expected CSV format:
    - entry_date (or buchungsdatum): YYYY-MM-DD, YYYYMMDD, or DD.MM.YYYY
    - account_number (or konto): Account number
    - description (or buchungstext): Description
    - debit_amount (or soll): Debit amount
    - credit_amount (or haben): Credit amount
    - entry_number (or belegnummer): Optional entry number
    - tax_code (or steuerschluessel): Optional tax code
    - cost_center (or kostenstelle): Optional cost center
    - profit_center (or kostentraeger): Optional profit center
    - reference (or beleg): Optional reference
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse CSV
        rows = parse_csv_file(file_content, delimiter)
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty or invalid")
        
        errors: List[ImportError] = []
        successful_entries: List[JournalEntryImportRow] = []
        created_entry_ids: List[str] = []
        
        # Group rows by entry (same entry_date and entry_number)
        entries_dict: Dict[str, List[JournalEntryImportRow]] = {}
        
        for idx, row_data in enumerate(rows, start=2):  # Start at 2 (header is row 1)
            entry, error = validate_and_parse_row(row_data, idx)
            
            if error:
                errors.append(error)
                continue
            
            if entry:
                # Group by entry_date and entry_number
                key = f"{entry.entry_date.isoformat()}_{entry.entry_number or 'default'}"
                if key not in entries_dict:
                    entries_dict[key] = []
                entries_dict[key].append(entry)
                successful_entries.append(entry)
        
        if not dry_run:
            # Create journal entries
            for entry_key, entry_lines in entries_dict.items():
                if not entry_lines:
                    continue
                
                # Get first line for entry metadata
                first_line = entry_lines[0]
                entry_date = first_line.entry_date
                
                # Calculate totals
                total_debit = sum(line.debit_amount for line in entry_lines)
                total_credit = sum(line.credit_amount for line in entry_lines)
                
                # Validate balance
                if abs(total_debit - total_credit) >= Decimal("0.01"):
                    errors.append(ImportError(
                        row_number=0,
                        field='balance',
                        error_message=f'Entry {entry_key} is not balanced: debit={total_debit}, credit={total_credit}',
                        row_data={'entry_key': entry_key}
                    ))
                    continue
                
                # Generate entry number if not provided
                entry_number = first_line.entry_number
                if not entry_number:
                    entry_number = f"IMP-{entry_date.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                
                # Create journal entry
                entry_id = str(uuid.uuid4())
                journal_entry_insert = text("""
                    INSERT INTO domain_erp.journal_entries
                    (id, tenant_id, entry_number, entry_date, posting_date, description,
                     source, currency, status, total_debit, total_credit, created_at, updated_at)
                    VALUES (:id, :tenant_id, :entry_number, :entry_date, :posting_date, :description,
                            :source, :currency, :status, :total_debit, :total_credit, NOW(), NOW())
                    RETURNING id
                """)
                
                db.execute(journal_entry_insert, {
                    "id": entry_id,
                    "tenant_id": tenant_id,
                    "entry_number": entry_number,
                    "entry_date": entry_date,
                    "posting_date": entry_date,
                    "description": first_line.description,
                    "source": "bulk_import",
                    "currency": "EUR",
                    "status": "draft",  # Imported entries start as draft
                    "total_debit": total_debit,
                    "total_credit": total_credit
                })
                
                # Create journal entry lines
                for line_idx, line in enumerate(entry_lines, start=1):
                    # Get account ID
                    account_query = text("""
                        SELECT id FROM domain_erp.chart_of_accounts
                        WHERE account_number = :account_number AND tenant_id = :tenant_id
                        LIMIT 1
                    """)
                    
                    account_row = db.execute(account_query, {
                        "account_number": line.account_number,
                        "tenant_id": tenant_id
                    }).fetchone()
                    
                    if not account_row:
                        errors.append(ImportError(
                            row_number=0,
                            field='account_number',
                            error_message=f'Account not found: {line.account_number}',
                            row_data={'account_number': line.account_number}
                        ))
                        db.rollback()
                        continue
                    
                    account_id = str(account_row[0])
                    
                    # Insert journal entry line
                    line_id = f"{entry_id}-L{line_idx}"
                    journal_line_insert = text("""
                        INSERT INTO domain_erp.journal_entry_lines
                        (id, tenant_id, journal_entry_id, account_id, debit_amount, credit_amount,
                         line_number, description, tax_code, cost_center, profit_center, reference,
                         created_at, updated_at)
                        VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit_amount, :credit_amount,
                                :line_number, :description, :tax_code, :cost_center, :profit_center, :reference,
                                NOW(), NOW())
                    """)
                    
                    db.execute(journal_line_insert, {
                        "id": line_id,
                        "tenant_id": tenant_id,
                        "journal_entry_id": entry_id,
                        "account_id": account_id,
                        "debit_amount": line.debit_amount,
                        "credit_amount": line.credit_amount,
                        "line_number": line_idx,
                        "description": line.description,
                        "tax_code": line.tax_code,
                        "cost_center": line.cost_center,
                        "profit_center": line.profit_center,
                        "reference": line.reference
                    })
                
                created_entry_ids.append(entry_id)
            
            if errors:
                db.rollback()
            else:
                db.commit()
        
        import_id = str(uuid.uuid4())
        
        return ImportResult(
            total_rows=len(rows),
            successful=len(successful_entries),
            failed=len(errors),
            errors=errors,
            created_entry_ids=created_entry_ids if not dry_run else [],
            import_id=import_id,
            imported_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing journal entries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import journal entries: {str(e)}")


@router.get("/template")
async def get_import_template():
    """
    Get CSV template for journal entry import.
    """
    template = """entry_date,account_number,description,debit_amount,credit_amount,entry_number,tax_code,cost_center,profit_center,reference
2024-01-15,1400,Forderung aus Lieferungen und Leistungen,1000.00,0.00,RE-2024-001,1,CC001,PT001,INV-001
2024-01-15,8400,Erlöse,0.00,1000.00,RE-2024-001,1,CC001,PT001,INV-001
2024-01-20,4400,Verbindlichkeiten aus Lieferungen und Leistungen,0.00,500.00,AP-2024-001,1,CC002,PT002,SUP-001
2024-01-20,5000,Materialaufwand,500.00,0.00,AP-2024-001,1,CC002,PT002,SUP-001"""
    
    return {
        "template": template,
        "format": "CSV",
        "delimiter": ",",
        "encoding": "UTF-8",
        "columns": {
            "entry_date": "Required. Date format: YYYY-MM-DD, YYYYMMDD, or DD.MM.YYYY",
            "account_number": "Required. Account number from chart of accounts",
            "description": "Required. Description of the journal entry",
            "debit_amount": "Required if credit_amount is 0. Debit amount",
            "credit_amount": "Required if debit_amount is 0. Credit amount",
            "entry_number": "Optional. Entry number (will be auto-generated if not provided)",
            "tax_code": "Optional. Tax code",
            "cost_center": "Optional. Cost center",
            "profit_center": "Optional. Profit center",
            "reference": "Optional. Reference document"
        }
    }

