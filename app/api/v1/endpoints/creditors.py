"""
Creditor (Kreditoren) master data management endpoints.
FIBU-AP-01: CRUD + Dublettencheck (creditor_number pro Tenant).
"""

from typing import Optional
import re
import json
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db
from ....core.uuid7 import uuid7
from ..schemas.finance import Creditor, CreditorCreate, CreditorUpdate
from ..schemas.base import PaginatedResponse

router = APIRouter(prefix="/creditors", tags=["finance", "creditors"])

_VAT_PATTERNS = {
    "DE": re.compile(r"^DE\d{9}$"),
    "AT": re.compile(r"^ATU\d{8}$"),
    "NL": re.compile(r"^NL\d{9}B\d{2}$"),
    "FR": re.compile(r"^FR[A-HJ-NP-Z0-9]{2}\d{9}$"),
    "BE": re.compile(r"^BE0?\d{9}$"),
    "CH": re.compile(r"^CHE\d{9}$"),
    "IT": re.compile(r"^IT\d{11}$"),
    "ES": re.compile(r"^ES[A-Z0-9]\d{7}[A-Z0-9]$", re.IGNORECASE),
    "PL": re.compile(r"^PL\d{10}$"),
}


def _validate_vat_id_format(vat_id: Optional[str]) -> None:
    if not vat_id or not (raw := vat_id.replace(" ", "").replace("-", "").strip().upper()):
        return
    prefix = raw[:2]
    pattern = _VAT_PATTERNS.get(prefix)
    if not pattern:
        raise HTTPException(status_code=400, detail=f"USt-ID: unbekanntes Format für '{prefix}'.")
    if not pattern.match(raw):
        raise HTTPException(status_code=400, detail=f"USt-ID: ungültiges Format für {prefix}.")


def _validate_iban(iban: Optional[str]) -> None:
    if not iban or not (raw := iban.replace(" ", "").replace("-", "").strip().upper()):
        return
    if len(raw) < 15 or len(raw) > 34:
        raise HTTPException(status_code=400, detail="IBAN: ungültige Länge (15–34 Zeichen).")
    if not (len(raw) >= 4 and raw[:2].isalpha() and raw[2:4].isdigit() and all(c.isalnum() for c in raw[4:])):
        raise HTTPException(status_code=400, detail="IBAN: Format LL00… (2 Buchstaben, 2 Ziffern, alphanumerisch).")
    rearranged = raw[4:] + raw[:4]
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    remainder = 0
    for ch in numeric:
        remainder = (remainder * 10 + int(ch)) % 97
    if remainder != 1:
        raise HTTPException(status_code=400, detail="IBAN: Prüfziffer ungültig (Mod-97).")


def _parse_address_jsonb(address_jsonb) -> dict:
    if address_jsonb is None:
        return {}
    if isinstance(address_jsonb, str):
        return json.loads(address_jsonb)
    return address_jsonb


def _build_address_jsonb(data) -> str:
    address_data = {
        "contact_person": getattr(data, "contact_person", None),
        "street": getattr(data, "street", ""),
        "postal_code": getattr(data, "postal_code", ""),
        "city": getattr(data, "city", ""),
        "country": getattr(data, "country", "DE"),
        "phone": getattr(data, "phone", None),
        "email": getattr(data, "email", None),
        "vat_id": getattr(data, "vat_id", None),
        "tax_number": getattr(data, "tax_number", None),
        "iban": getattr(data, "iban", None),
        "bic": getattr(data, "bic", None),
        "bank_name": getattr(data, "bank_name", None),
        "account_holder": getattr(data, "account_holder", None),
        "payment_terms_days": getattr(data, "payment_terms_days", 30),
        "discount_days": getattr(data, "discount_days", 0),
        "discount_percent": float(getattr(data, "discount_percent", 0) or 0),
        "credit_limit": float(getattr(data, "credit_limit", 0) or 0),
        "notes": getattr(data, "notes", None),
    }
    return json.dumps(address_data)


def _row_to_creditor(row) -> Creditor:
    address_data = _parse_address_jsonb(row[4])
    return Creditor(
        id=str(row[0]),
        tenant_id=row[1],
        creditor_number=row[2],
        company_name=row[3],
        contact_person=address_data.get("contact_person"),
        street=address_data.get("street", ""),
        postal_code=address_data.get("postal_code", ""),
        city=address_data.get("city", ""),
        country=address_data.get("country", "DE"),
        phone=address_data.get("phone"),
        email=address_data.get("email"),
        vat_id=address_data.get("vat_id"),
        tax_number=address_data.get("tax_number"),
        iban=address_data.get("iban"),
        bic=address_data.get("bic"),
        bank_name=address_data.get("bank_name"),
        account_holder=address_data.get("account_holder"),
        payment_terms_days=address_data.get("payment_terms_days", 30),
        discount_days=address_data.get("discount_days", 0),
        discount_percent=Decimal(str(address_data.get("discount_percent", 0))),
        credit_limit=Decimal(str(address_data.get("credit_limit", 0))),
        is_active=bool(row[7]) if row[7] is not None else True,
        notes=address_data.get("notes"),
        current_balance=Decimal(str(row[6])) if row[6] is not None else None,
        created_at=row[8].isoformat() if row[8] else None,
        updated_at=row[9].isoformat() if row[9] else None,
    )


@router.post("/", response_model=Creditor, status_code=201)
async def create_creditor(
    payload: CreditorCreate,
    db: Session = Depends(get_db),
):
    """Create a new creditor. Duplicate creditor_number per tenant is rejected."""
    try:
        _validate_vat_id_format(payload.vat_id)
        _validate_iban(payload.iban)
        check = db.execute(
            text(
                "SELECT id FROM domain_erp.creditors WHERE creditor_number = :cn AND (tenant_id = :tid OR (tenant_id IS NULL AND :tid = 'system'))"
            ),
            {"cn": payload.creditor_number, "tid": payload.tenant_id},
        ).fetchone()
        if check:
            raise HTTPException(status_code=400, detail=f"Kreditor mit Nummer {payload.creditor_number} existiert bereits.")

        address_json = _build_address_jsonb(payload)
        payment_terms = f"{payload.payment_terms_days or 30}_days"
        acc_id = uuid7()
        db.execute(
            text(
                """
                INSERT INTO domain_erp.creditors
                (id, tenant_id, creditor_number, name, address, payment_terms, current_balance, is_active)
                VALUES (:id, :tenant_id, :creditor_number, :company_name, :address::jsonb, :payment_terms, 0, :is_active)
                """
            ),
            {
                "id": acc_id,
                "tenant_id": payload.tenant_id,
                "creditor_number": payload.creditor_number,
                "company_name": payload.company_name,
                "address": address_json,
                "payment_terms": payment_terms,
                "is_active": payload.is_active if payload.is_active is not None else True,
            },
        )
        db.commit()
        row = db.execute(
            text(
                "SELECT id, tenant_id, creditor_number, name, address, payment_terms, current_balance, is_active, created_at, updated_at FROM domain_erp.creditors WHERE id = :id"
            ),
            {"id": acc_id},
        ).fetchone()
        return _row_to_creditor(row)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Anlegen des Kreditors: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Creditor])
async def list_creditors(
    tenant_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List creditors with pagination and optional filters."""
    try:
        tid = tenant_id or "system"
        where = ["(tenant_id = :tenant_id OR (tenant_id IS NULL AND :tenant_id = 'system'))"]
        params = {"tenant_id": tid}
        if is_active is not None:
            where.append("is_active = :is_active")
            params["is_active"] = is_active
        if search:
            where.append("(name ILIKE :search OR creditor_number ILIKE :search)")
            params["search"] = f"%{search}%"
        where_sql = " AND ".join(where)
        total = db.execute(text(f"SELECT COUNT(*) FROM domain_erp.creditors WHERE {where_sql}"), params).scalar()
        params["limit"] = limit
        params["skip"] = skip
        rows = db.execute(
            text(
                f"""
                SELECT id, tenant_id, creditor_number, name, address, payment_terms, current_balance, is_active, created_at, updated_at
                FROM domain_erp.creditors WHERE {where_sql}
                ORDER BY creditor_number
                LIMIT :limit OFFSET :skip
                """
            ),
            params,
        ).fetchall()
        items = [_row_to_creditor(r) for r in rows]
        return PaginatedResponse[Creditor](
            items=items,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit if total else 1,
            has_next=(skip + limit) < total,
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{creditor_id}", response_model=Creditor)
async def get_creditor(
    creditor_id: str,
    db: Session = Depends(get_db),
):
    """Get creditor by ID."""
    row = db.execute(
        text(
            "SELECT id, tenant_id, creditor_number, name, address, payment_terms, current_balance, is_active, created_at, updated_at FROM domain_erp.creditors WHERE id = :id"
        ),
        {"id": creditor_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Kreditor nicht gefunden")
    return _row_to_creditor(row)


@router.put("/{creditor_id}", response_model=Creditor)
async def update_creditor(
    creditor_id: str,
    payload: CreditorUpdate,
    db: Session = Depends(get_db),
):
    """Update creditor."""
    try:
        _validate_vat_id_format(payload.vat_id)
        _validate_iban(payload.iban)
        existing = db.execute(
            text("SELECT id, name, address FROM domain_erp.creditors WHERE id = :id"),
            {"id": creditor_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Kreditor nicht gefunden")
        address = _parse_address_jsonb(existing[2])
        if payload.contact_person is not None:
            address["contact_person"] = payload.contact_person
        if payload.street is not None:
            address["street"] = payload.street
        if payload.postal_code is not None:
            address["postal_code"] = payload.postal_code
        if payload.city is not None:
            address["city"] = payload.city
        if payload.country is not None:
            address["country"] = payload.country
        if payload.phone is not None:
            address["phone"] = payload.phone
        if payload.email is not None:
            address["email"] = payload.email
        if payload.vat_id is not None:
            address["vat_id"] = payload.vat_id
        if payload.tax_number is not None:
            address["tax_number"] = payload.tax_number
        if payload.iban is not None:
            address["iban"] = payload.iban
        if payload.bic is not None:
            address["bic"] = payload.bic
        if payload.bank_name is not None:
            address["bank_name"] = payload.bank_name
        if payload.account_holder is not None:
            address["account_holder"] = payload.account_holder
        if payload.payment_terms_days is not None:
            address["payment_terms_days"] = payload.payment_terms_days
        if payload.discount_days is not None:
            address["discount_days"] = payload.discount_days
        if payload.discount_percent is not None:
            address["discount_percent"] = float(payload.discount_percent)
        if payload.credit_limit is not None:
            address["credit_limit"] = float(payload.credit_limit)
        if payload.notes is not None:
            address["notes"] = payload.notes
        payment_terms_days = address.get("payment_terms_days", 30)
        db.execute(
            text(
                """
                UPDATE domain_erp.creditors
                SET address = :address::jsonb, payment_terms = :payment_terms, updated_at = NOW()
                """ + (", is_active = :is_active" if payload.is_active is not None else "") + """
                WHERE id = :id
                """
            ),
            {
                "id": creditor_id,
                "address": json.dumps(address),
                "payment_terms": f"{payment_terms_days}_days",
                **({"is_active": payload.is_active} if payload.is_active is not None else {}),
            },
        )
        db.commit()
        row = db.execute(
            text(
                "SELECT id, tenant_id, creditor_number, name, address, payment_terms, current_balance, is_active, created_at, updated_at FROM domain_erp.creditors WHERE id = :id"
            ),
            {"id": creditor_id},
        ).fetchone()
        return _row_to_creditor(row)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{creditor_id}", status_code=204)
async def delete_creditor(
    creditor_id: str,
    db: Session = Depends(get_db),
):
    """Soft-delete creditor (set is_active = false)."""
    existing = db.execute(text("SELECT id FROM domain_erp.creditors WHERE id = :id"), {"id": creditor_id}).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Kreditor nicht gefunden")
    db.execute(text("UPDATE domain_erp.creditors SET is_active = false, updated_at = NOW() WHERE id = :id"), {"id": creditor_id})
    db.commit()
