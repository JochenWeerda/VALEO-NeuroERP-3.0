"""
Bankkontenstamm API
FIBU-BNK-01: Bankstamm-UI – CRUD für Bankkonten inkl. Verknüpfung zum Kontenplan (Gegenkonto)
"""

from typing import List, Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
import logging

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.uuid7 import uuid7
from app.api.v1.schemas.bank_accounts_schemas import (
    BankAccountsOut, BankAccountCreate, BankAccountUpdate, BankAccountResponse, BankLedgerOption,
)

logger = logging.getLogger(__name__)


def _validate_iban(iban: Optional[str]) -> None:
    """Raises HTTPException 400 if iban is non-empty and invalid (mod-97)."""
    if not iban or not (raw := iban.replace(" ", "").replace("-", "").strip().upper()):
        return
    if len(raw) < 15 or len(raw) > 34:
        raise HTTPException(status_code=400, detail="IBAN: ungültige Länge (15–34 Zeichen).")
    if not (
        len(raw) >= 4
        and raw[:2].isalpha()
        and raw[2:4].isdigit()
        and all(c.isalnum() for c in raw[4:])
    ):
        raise HTTPException(status_code=400, detail="IBAN: Format LL00… (2 Buchstaben, 2 Ziffern, alphanumerisch).")
    rearranged = raw[4:] + raw[:4]
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    remainder = 0
    for ch in numeric:
        remainder = (remainder * 10 + int(ch)) % 97
    if remainder != 1:
        raise HTTPException(status_code=400, detail="IBAN: Prüfziffer ungültig (Mod-97).")



router = APIRouter(prefix="/bank-accounts", tags=["finance", "bank-accounts"])


@router.get("/new", response_model=BankAccountsOut, summary="New bank account template abrufen")
async def get_new_bank_account_template(tenant_id: str = Depends(get_tenant_id)):
    """Return default values for bank account create forms."""
    return {
        "id": None,
        "tenant_id": tenant_id,
        "account_number": "",
        "bank_name": "",
        "iban": "",
        "bic": "",
        "currency": "EUR",
        "gl_account_id": None,
        "is_active": True,
    }


def _validate_gl_account(db: Session, tenant_id: str, account_id: Optional[str]) -> None:
    if account_id is None:
        return
    row = db.execute(text("""
        SELECT is_active, account_type, category, is_summary, deleted_at
        FROM domain_erp.chart_of_accounts WHERE id=:id AND tenant_id=:tenant
    """), {"id": account_id, "tenant": tenant_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Hauptbuchkonto nicht gefunden")
    if not row["is_active"] or row["deleted_at"] or row["is_summary"] or str(row["account_type"]).upper() != "ASSET" or str(row["category"]).upper() != "BANK":
        raise HTTPException(409, "Hauptbuchkonto muss ein aktives buchbares Aktivkonto sein")


@router.get("", response_model=List[BankAccountResponse], summary="Bank accounts auflisten")
async def list_bank_accounts(
    tenant_id: str = Depends(get_tenant_id),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Liste aller Bankkonten des Mandanten."""
    try:
        where = "WHERE ba.tenant_id = :tenant_id"
        params: dict = {"tenant_id": tenant_id, "limit": limit}
        if is_active is not None:
            where += " AND ba.is_active = :is_active"
            params["is_active"] = is_active
        q = text(
            f"""
            SELECT ba.id, ba.tenant_id, ba.account_number, ba.bank_name, ba.iban, ba.bic,
                   ba.currency, ba.balance, ba.is_active,
                   ba.gl_account_id
            FROM domain_erp.bank_accounts ba
            {where}
            ORDER BY ba.account_number
            LIMIT :limit
            """  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
        )
        rows = db.execute(q, params).fetchall()
        return [
            BankAccountResponse(
                id=str(r[0]),
                tenant_id=r[1],
                account_number=str(r[2]),
                bank_name=str(r[3]),
                iban=r[4],
                bic=r[5],
                currency=r[6],
                balance=Decimal(str(r[7])) if r[7] is not None else None,
                is_active=r[8] is True,
                gl_account_id=str(r[9]) if r[9] else None,
            )
            for r in rows
        ]
    except Exception as e:
        logger.error(f"Error listing bank accounts: {e}")
        raise HTTPException(status_code=500, detail="Bankkonto konnte nicht verlaesslich verarbeitet werden")


@router.get("/ledger-options", response_model=List[BankLedgerOption], summary="Own bookable bank ledger accounts")
async def list_ledger_options(tenant_id: str = Depends(get_tenant_id),
    limit: int = Query(100, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT id,account_number,account_name FROM domain_erp.chart_of_accounts
        WHERE tenant_id=:t AND is_active=TRUE AND coalesce(is_summary,FALSE)=FALSE
          AND deleted_at IS NULL AND upper(account_type)='ASSET' AND upper(category)='BANK'
        ORDER BY account_number,id LIMIT :limit OFFSET :offset
    """), {"t": tenant_id, "limit": limit, "offset": offset}).mappings().all()
    return [BankLedgerOption(**row) for row in rows]


@router.get("/{account_id}", response_model=BankAccountResponse, summary="Bank account abrufen")
async def get_bank_account(
    account_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelnes Bankkonto abrufen."""
    q = text(
        """
        SELECT id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, gl_account_id
        FROM domain_erp.bank_accounts
        WHERE id = :id AND tenant_id = :tenant_id
        """
    )
    row = db.execute(q, {"id": account_id, "tenant_id": tenant_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Bankkonto nicht gefunden")
    return BankAccountResponse(
        id=str(row[0]),
        tenant_id=row[1],
        account_number=str(row[2]),
        bank_name=str(row[3]),
        iban=row[4],
        bic=row[5],
        currency=row[6],
        balance=Decimal(str(row[7])) if row[7] is not None else None,
        is_active=row[8] is True,
        gl_account_id=str(row[9]) if row[9] else None,
    )


@router.post("", response_model=BankAccountResponse, status_code=201, summary="Bank account anlegen")
async def create_bank_account(
    payload: BankAccountCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neues Bankkonto anlegen. Verknuepft nur ein explizit ausgewaehltes Hauptbuchkonto."""
    try:
        _validate_iban(payload.iban)
        _validate_gl_account(db, tenant_id, payload.gl_account_id)
        acc_id = uuid7()
        db.execute(
            text(
                """
                INSERT INTO domain_erp.bank_accounts
                (id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, gl_account_id, created_at, updated_at)
                VALUES (:id, :tenant_id, :account_number, :bank_name, :iban, :bic, :currency, 0, :is_active, :gl_account_id, NOW(), NOW())
                """
            ),
            {
                "id": acc_id,
                "tenant_id": tenant_id,
                "account_number": payload.account_number,
                "bank_name": payload.bank_name,
                "iban": payload.iban,
                "bic": payload.bic,
                "currency": payload.currency or "EUR",
                "is_active": payload.is_active,
                "gl_account_id": payload.gl_account_id,
            },
        )
        db.commit()
        return await get_bank_account(acc_id, tenant_id, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating bank account: {e}")
        raise HTTPException(status_code=500, detail="Bankkonto konnte nicht verlaesslich verarbeitet werden")


@router.put("/{account_id}", response_model=BankAccountResponse, summary="Bank account aktualisieren")
async def update_bank_account(
    account_id: str,
    payload: BankAccountUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Bankkonto aktualisieren (Name, IBAN, BIC, Währung, Aktiv)."""
    try:
        _validate_iban(payload.iban)
        row = db.execute(
            text(
                "SELECT id, account_number FROM domain_erp.bank_accounts WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": account_id, "tenant_id": tenant_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Bankkonto nicht gefunden")
        if "gl_account_id" in payload.model_fields_set:
            _validate_gl_account(db, tenant_id, payload.gl_account_id)
        updates = []
        params: dict = {"id": account_id, "tenant_id": tenant_id}
        if payload.bank_name is not None:
            updates.append("bank_name = :bank_name")
            params["bank_name"] = payload.bank_name
        if payload.iban is not None:
            updates.append("iban = :iban")
            params["iban"] = payload.iban
        if payload.bic is not None:
            updates.append("bic = :bic")
            params["bic"] = payload.bic
        if payload.currency is not None:
            updates.append("currency = :currency")
            params["currency"] = payload.currency
        if payload.is_active is not None:
            updates.append("is_active = :is_active")
            params["is_active"] = payload.is_active
        if "gl_account_id" in payload.model_fields_set:
            updates.append("gl_account_id = :gl_account_id")
            params["gl_account_id"] = payload.gl_account_id
        if not updates:
            return await get_bank_account(account_id, tenant_id, db)
        db.execute(
            text(
                f"UPDATE domain_erp.bank_accounts SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
            ),
            params,
        )
        db.commit()
        return await get_bank_account(account_id, tenant_id, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating bank account: {e}")
        raise HTTPException(status_code=500, detail="Bankkonto konnte nicht verlaesslich verarbeitet werden")


@router.delete("/{account_id}", status_code=204, response_class=Response, response_model=None, summary="Bank account löschen")
async def delete_bank_account(
    account_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Bankkonto deaktivieren (Soft-Delete über is_active=FALSE)."""
    try:
        row = db.execute(
            text("SELECT id FROM domain_erp.bank_accounts WHERE id = :id AND tenant_id = :tid"),
            {"id": account_id, "tid": tenant_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Bankkonto nicht gefunden")
        db.execute(
            text(
                "UPDATE domain_erp.bank_accounts SET is_active = FALSE, updated_at = NOW() "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": account_id, "tid": tenant_id},
        )
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting bank account: {e}")
        raise HTTPException(status_code=500, detail="Bankkonto konnte nicht verlaesslich verarbeitet werden")
