"""
Bankkontenstamm API
FIBU-BNK-01: Bankstamm-UI – CRUD für Bankkonten inkl. Verknüpfung zum Kontenplan (Gegenkonto)
"""

from typing import List, Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
import logging

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.uuid7 import uuid7

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

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/bank-accounts", tags=["finance", "bank-accounts"])


@router.get("/new", response_model=CompatFlexOut, summary="New bank account template abrufen")
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
        "gl_account_number": "",
        "is_active": True,
    }


class BankAccountBase(BaseModel):
    account_number: str
    bank_name: str
    iban: Optional[str] = None
    bic: Optional[str] = None
    currency: str = "EUR"
    gl_account_number: Optional[str] = None  # Gegenkonto im Kontenplan (falls abweichend von account_number)
    is_active: bool = True


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountUpdate(BaseModel):
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    currency: Optional[str] = None
    gl_account_number: Optional[str] = None
    is_active: Optional[bool] = None


class BankAccountResponse(BankAccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: Optional[str] = None
    balance: Optional[Decimal] = None


def _ensure_gl_account(
    db: Session,
    tenant_id: str,
    account_number: str,
    account_name: str,
) -> None:
    """Erstellt einen Kontenplan-Eintrag für das Bankkonto, falls nicht vorhanden."""
    row = db.execute(
        text(
            """
            SELECT id FROM domain_erp.chart_of_accounts
            WHERE tenant_id = :tenant_id AND account_number = :account_number
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "account_number": account_number},
    ).fetchone()
    if row:
        return
    acc_id = uuid7()
    db.execute(
        text(
            """
            INSERT INTO domain_erp.chart_of_accounts
            (id, tenant_id, account_number, account_name, account_type, category, is_active, created_at, updated_at)
            VALUES (:id, :tenant_id, :account_number, :account_name, 'ASSET', 'bank', TRUE, NOW(), NOW())
            """
        ),
        {
            "id": acc_id,
            "tenant_id": tenant_id,
            "account_number": account_number,
            "account_name": account_name,
        },
    )


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
                   COALESCE(coa.account_number, ba.account_number) as gl_account_number
            FROM domain_erp.bank_accounts ba
            LEFT JOIN domain_erp.chart_of_accounts coa
              ON coa.tenant_id = ba.tenant_id AND coa.account_number = ba.account_number
            {where}
            ORDER BY ba.account_number
            LIMIT :limit
            """
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
                currency=r[6] or "EUR",
                balance=Decimal(str(r[7])) if r[7] is not None else None,
                is_active=bool(r[8]) if r[8] is not None else True,
                gl_account_number=str(r[9]) if r[9] else str(r[2]),
            )
            for r in rows
        ]
    except Exception as e:
        logger.error(f"Error listing bank accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}", response_model=BankAccountResponse, summary="Bank account abrufen")
async def get_bank_account(
    account_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelnes Bankkonto abrufen."""
    q = text(
        """
        SELECT id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active
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
        currency=row[6] or "EUR",
        balance=Decimal(str(row[7])) if row[7] is not None else None,
        is_active=bool(row[8]) if row[8] is not None else True,
        gl_account_number=str(row[2]),
    )


@router.post("", response_model=BankAccountResponse, status_code=201, summary="Bank account anlegen")
async def create_bank_account(
    payload: BankAccountCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neues Bankkonto anlegen. Legt bei Bedarf einen Kontenplan-Eintrag (Gegenkonto) an."""
    try:
        _validate_iban(payload.iban)
        gl_number = payload.gl_account_number or payload.account_number
        _ensure_gl_account(db, tenant_id, gl_number, payload.bank_name or f"Bank {payload.account_number}")
        acc_id = uuid7()
        db.execute(
            text(
                """
                INSERT INTO domain_erp.bank_accounts
                (id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, created_at, updated_at)
                VALUES (:id, :tenant_id, :account_number, :bank_name, :iban, :bic, :currency, 0, :is_active, NOW(), NOW())
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
            },
        )
        db.commit()
        return await get_bank_account(acc_id, tenant_id, db)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating bank account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
        if not updates:
            return await get_bank_account(account_id, tenant_id, db)
        db.execute(
            text(
                f"UPDATE domain_erp.bank_accounts SET {', '.join(updates)}, updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"
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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))
