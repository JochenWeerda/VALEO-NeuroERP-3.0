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
                             file_iban: str | None = None,
                             statement_currency: str | None = None,
                             *, statement_date: date) -> tuple[str, str, dict | None]:
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
    if (statement_currency is not None and statement_currency != currency) or any(entry.get('currency', 'EUR') != currency for entry in entries):
        raise HTTPException(status_code=422, detail="Statement currency does not match bank account")
    context = json.dumps([tenant_id, account_id, format.upper()], separators=(',', ':')).encode()
    fingerprint = hashlib.sha256(context + b"\0" + content).hexdigest()
    statement_id = f"STMT-IMP-{fingerprint}"
    # Lock before the lookup: a SELECT FOR UPDATE cannot lock an absent row.
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
               {"key": f"bank-import:{statement_id}"})
    existing = db.execute(text("""
        SELECT id,tenant_id,bank_account_id,account_iban,opening_balance,closing_balance,
               total_lines,imported_lines,format,status,statement_date
        FROM domain_erp.bank_statements WHERE id=:id FOR UPDATE
    """), {"id": statement_id}).mappings().first()
    if existing is not None:
        if (existing['tenant_id'] != tenant_id or existing['bank_account_id'] != account_id
                or existing['format'] != format.upper() or existing['account_iban'] != iban
                or existing['status'] != 'imported'):
            raise HTTPException(status_code=409, detail="Stored statement identity is inconsistent")
        if existing['statement_date'] != statement_date:
            raise HTTPException(status_code=409, detail="Stored statement cutoff is inconsistent")
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
    """Booked single-transaction CAMT.053.001.02 profile, without guessed data."""
    ns = '{urn:iso:std:iso:20022:tech:xsd:camt.053.001.02}'

    def nodes(parent, path):
        return parent.findall('/'.join(ns + part for part in path.split('/')))

    def one(parent, path, required=False):
        current = parent
        for part in path.split('/'):
            found = nodes(current, part)
            if len(found) > 1 or (required and not found):
                raise ValueError(f'CAMT requires a unique {path}')
            if not found:
                return None
            current = found[0]
        return current

    def value(parent, path, required=False):
        element = one(parent, path, required)
        result = element.text.strip() if element is not None and element.text else None
        if required and not result:
            raise ValueError(f'CAMT requires {path}')
        return result

    def dated(parent, path):
        choice = one(parent, path, True)
        dates = nodes(choice, 'Dt') + nodes(choice, 'DtTm')
        if len(dates) != 1 or not dates[0].text:
            raise ValueError(f'CAMT requires an explicit {path} date')
        raw = dates[0].text.strip()
        if dates[0].tag == ns + 'Dt':
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
                raise ValueError('Invalid CAMT date')
            return datetime.strptime(raw, '%Y-%m-%d').date()
        if 'T' not in raw:
            raise ValueError('Invalid CAMT datetime')
        return datetime.fromisoformat(raw.replace('Z', '+00:00')).date()

    def money(parent, path='Amt'):
        element = one(parent, path, True)
        raw = (element.text or '').strip()
        currency = element.get('Ccy')
        if not re.fullmatch(r'\d+(?:\.\d{1,2})?', raw) or len(raw.replace('.', '')) > 18:
            raise ValueError('CAMT amount must be unsigned finite exact cents')
        if not currency or not re.fullmatch(r'[A-Z]{3}', currency):
            raise ValueError('CAMT amount requires currency')
        amount = Decimal(raw).quantize(Decimal('0.01'))
        if amount >= Decimal('10000000000000'):
            raise ValueError('CAMT amount exceeds bank statement storage precision')
        return amount, currency

    def signed(parent):
        amount, currency = money(parent)
        direction = value(parent, 'CdtDbtInd', True)
        if direction not in {'CRDT', 'DBIT'}:
            raise ValueError('Invalid CAMT credit/debit indicator')
        return amount if direction == 'CRDT' else -amount, currency

    try:
        xml = content.decode('utf-8-sig')
        if '<!DOCTYPE' in xml or '<!ENTITY' in xml:
            raise ValueError('CAMT DTD/entities are not supported')
        root = ET.fromstring(xml)
        if root.tag != ns + 'Document':
            raise ValueError('Unsupported CAMT namespace or root')
        report = one(root, 'BkToCstmrStmt', True)
        stmt = one(report, 'Stmt', True)
        if len(root.findall('.//' + ns + 'Stmt')) != 1:
            raise ValueError('Exactly one CAMT statement is required')
        account = one(stmt, 'Acct', True)
        iban = value(account, 'Id/IBAN')
        balances = {}
        for bal in nodes(stmt, 'Bal'):
            code = value(bal, 'Tp/CdOrPrtry/Cd')
            if code in {'OPBD', 'CLBD'}:
                if code in balances:
                    raise ValueError(f'Duplicate CAMT {code} balance')
                amount, currency = signed(bal)
                balances[code] = (amount, currency, dated(bal, 'Dt'))
        if set(balances) != {'OPBD', 'CLBD'}:
            raise ValueError('CAMT requires OPBD and CLBD balances')
        opening, closing = balances['OPBD'], balances['CLBD']
        currency = opening[1]
        if closing[1] != currency or closing[2] < opening[2]:
            raise ValueError('Inconsistent CAMT balance currency or dates')
        account_currency = value(account, 'Ccy')
        if account_currency is not None and account_currency != currency:
            raise ValueError('CAMT account and balance currencies differ')
        entries = []
        entry_nodes = nodes(stmt, 'Ntry')
        if len(root.findall('.//' + ns + 'Ntry')) != len(entry_nodes):
            raise ValueError('CAMT entries must belong directly to the statement')
        for ntry in entry_nodes:
            if value(ntry, 'Sts', True) != 'BOOK':
                raise ValueError('Only booked CAMT entries are supported')
            if value(ntry, 'RvslInd') not in {None, 'false', '0'}:
                raise ValueError('CAMT reversal requires a reversal contract')
            amount, entry_currency = signed(ntry)
            if amount == 0 or entry_currency != currency:
                raise ValueError('CAMT entry amount/currency is inconsistent')
            txs = nodes(ntry, 'NtryDtls/TxDtls')
            if len(txs) > 1 or nodes(ntry, 'NtryDtls/Btch') or len(ntry.findall('.//' + ns + 'TxDtls')) != len(txs):
                raise ValueError('CAMT batch allocation is not supported')
            tx = txs[0] if txs else ET.Element(ns + 'TxDtls')
            if tx.findall('.//' + ns + 'CcyXchg') or nodes(tx, 'RtrInf'):
                raise ValueError('CAMT FX/return requires a separate contract')
            tx_amount = one(tx, 'AmtDtls/TxAmt')
            if tx_amount is not None:
                detail_amount, detail_currency = money(tx_amount)
                if detail_amount != abs(amount) or detail_currency != currency:
                    raise ValueError('CAMT transaction amount differs from entry')
            reference = (value(ntry, 'AcctSvcrRef') or value(tx, 'Refs/AcctSvcrRef')
                         or value(tx, 'Refs/EndToEndId') or value(ntry, 'NtryRef'))
            texts = nodes(tx, 'RmtInf/Ustrd') + nodes(tx, 'RmtInf/Strd/CdtrRefInf/Ref')
            remittance = '\n'.join(element.text.strip() for element in texts if element.text and element.text.strip())
            booking_date = dated(ntry, 'BookgDt')
            if not opening[2] <= booking_date <= closing[2]:
                raise ValueError('CAMT booking date is outside statement balances')
            entries.append({
                'line_number': len(entries) + 1, 'booking_date': booking_date,
                'value_date': dated(ntry, 'ValDt'), 'amount': amount, 'currency': currency,
                'reference': reference, 'remittance_info': remittance or None,
                'creditor_name': value(tx, 'RltdPties/Cdtr/Nm'),
                'creditor_iban': value(tx, 'RltdPties/CdtrAcct/Id/IBAN'),
                'debtor_name': value(tx, 'RltdPties/Dbtr/Nm'),
                'debtor_iban': value(tx, 'RltdPties/DbtrAcct/Id/IBAN'),
            })
        if opening[0] + sum((entry['amount'] for entry in entries), Decimal('0')) != closing[0]:
            raise ValueError('CAMT closing balance does not reconcile with entries')
        return {'account_iban': iban, 'currency': currency, 'statement_date': closing[2], 'opening_balance': opening[0],
                'closing_balance': closing[0], 'entries': entries}
    except (ValueError, InvalidOperation, ET.ParseError) as exc:
        raise ValueError(f'Failed to parse CAMT.053: {exc}') from exc


def parse_mt940(content: bytes) -> dict:
    """Parse one IBAN statement; unsupported variants fail before persistence."""
    def balance(value: str) -> tuple[date, str, Decimal]:
        match = re.fullmatch(r'([CD])(\d{6})([A-Z]{3})(\d+,\d{0,2})', value)
        if not match or len(match[4]) > 15:
            raise ValueError('Invalid MT940 balance')
        amount = Decimal(match[4].replace(',', '.'))
        return datetime.strptime(match[2], '%y%m%d').date(), match[3], amount if match[1] == 'C' else -amount

    try:
        account_iban = None
        opening = closing = None
        entries = []
        last_tag = None
        for raw in content.decode('utf-8-sig').splitlines():
            line = raw.strip()
            if not line:
                continue
            tag_match = re.fullmatch(r':(\d{2}[A-Z]?):(.*)', line)
            if not tag_match:
                if last_tag == '86' and entries:
                    entries[-1]['remittance_info'] += '\n' + line
                    continue
                raise ValueError('Unsupported MT940 continuation or envelope')
            tag, value = tag_match.groups()
            if tag == '25':
                if account_iban is not None or opening is not None:
                    raise ValueError('Exactly one MT940 account is required')
                account_iban = value
            elif tag in {'60F', '60M'}:
                if opening is not None or account_iban is None or closing is not None:
                    raise ValueError('Invalid or repeated MT940 opening balance')
                opening = balance(value)
            elif tag in {'62F', '62M'}:
                if opening is None or closing is not None:
                    raise ValueError('Invalid or repeated MT940 closing balance')
                closing = balance(value)
            elif tag == '61':
                if opening is None or closing is not None:
                    raise ValueError('MT940 entry outside opening/closing balances')
                # MMDD is optional; :86: is optional and never controls entry creation.
                match = re.fullmatch(r'(\d{6})(\d{4})?([CD])([A-Z])?(\d+,\d{0,2})([NSF][A-Z0-9]{3})([^/]{1,16})(?://(.{1,16}))?', value)
                if not match or len(match[5]) > 15:
                    raise ValueError('Invalid or unsupported MT940 entry (including reversal)')
                value_date = datetime.strptime(match[1], '%y%m%d').date()
                booking_date = value_date
                if match[2]:
                    candidates = []
                    for year in (value_date.year - 1, value_date.year, value_date.year + 1):
                        try:
                            candidates.append(date(year, int(match[2][:2]), int(match[2][2:])))
                        except ValueError:
                            continue
                    if not candidates:
                        raise ValueError('Invalid MT940 booking date')
                    candidates.sort(key=lambda candidate: abs((candidate - value_date).days))
                    if len(candidates) > 1 and abs((candidates[0] - value_date).days) == abs((candidates[1] - value_date).days):
                        raise ValueError('Ambiguous MT940 booking year')
                    booking_date = candidates[0]
                    if abs((booking_date - value_date).days) > 183:
                        raise ValueError('Ambiguous MT940 booking year')
                if match[4] and match[4] != opening[1][-1]:
                    raise ValueError('MT940 funds code does not match statement currency')
                amount = Decimal(match[5].replace(',', '.'))
                entries.append({
                    'line_number': len(entries) + 1, 'booking_date': booking_date,
                    'value_date': value_date, 'amount': amount if match[3] == 'C' else -amount,
                    'currency': opening[1], 'reference': match[8] or match[7],
                    'remittance_info': None,
                })
            elif tag == '86':
                if last_tag != '61' or not entries or closing is not None:
                    raise ValueError('Orphan or repeated MT940 transaction description')
                entries[-1]['remittance_info'] = value
            elif tag not in {'20', '21', '28C', '64', '65'}:
                raise ValueError(f'Unsupported MT940 field {tag}')
            last_tag = tag
        if account_iban is None or opening is None or closing is None:
            raise ValueError('MT940 account, opening and closing balance are required')
        if closing[0] < opening[0] or closing[1] != opening[1]:
            raise ValueError('Inconsistent MT940 balance dates or currency')
        if any(not opening[0] <= entry['booking_date'] <= closing[0] for entry in entries):
            raise ValueError('MT940 booking date is outside statement balances')
        if opening[2] + sum((entry['amount'] for entry in entries), Decimal('0')) != closing[2]:
            raise ValueError('MT940 closing balance does not reconcile with entries')
        return {'account_iban': account_iban, 'currency': opening[1], 'statement_date': closing[0], 'opening_balance': opening[2],
                'closing_balance': closing[2], 'entries': entries}
    except (ValueError, InvalidOperation, UnicodeError) as exc:
        raise ValueError(f'Failed to parse MT940: {exc}') from exc


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

        if not entries:
            raise HTTPException(status_code=422, detail='CSV has no booking dates for a statement cutoff')
        # CSV has no bank-supplied closing date: use an explicit synthetic cutoff.
        closing_balance = opening_balance + sum(entry['amount'] for entry in entries)
        
        return {
            'account_iban': None,  # CSV doesn't always have IBAN
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'statement_date': max(entry['booking_date'] for entry in entries),
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
            None if format.upper() == 'CSV' else parsed['account_iban'] or '',
            statement_currency=parsed.get('currency'), statement_date=parsed['statement_date'])
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
            "iban": parsed['account_iban'], "date": parsed['statement_date'],
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

