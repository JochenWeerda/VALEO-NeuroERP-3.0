"""
Accruals and Provisions API
FIBU-CLS-03: Abgrenzungen / Rückstellungen
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/accruals-provisions", tags=["finance", "closing"])


class AccrualItemBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., ge=0)
    account_number: str = Field(..., min_length=1, max_length=20)
    counterpart_account: str = Field(..., min_length=1, max_length=20)
    period: str = Field(..., description="YYYY-MM")
    accrual_type: str = Field(..., description="rechnungsabgrenzungsposten or rueckstellung")


class AccrualItemCreate(AccrualItemBase):
    pass


class AccrualItem(AccrualItemBase):
    id: str
    tenant_id: str
    status: str = "draft"
    created_at: Optional[datetime] = None


@router.get("", response_model=List[AccrualItem])
async def list_accruals_provisions(
    period: Optional[str] = Query(None, description="Filter by period YYYY-MM"),
    accrual_type: Optional[str] = Query(None, description="Filter: rechnungsabgrenzungsposten or rueckstellung"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """List accruals and provisions for a period."""
    try:
        db.execute(text("CREATE TABLE IF NOT EXISTS domain_erp.accruals_provisions ("
                        "id VARCHAR(36) PRIMARY KEY, tenant_id VARCHAR(64), description VARCHAR(500), "
                        "amount NUMERIC(18,4), account_number VARCHAR(20), counterpart_account VARCHAR(20), "
                        "period VARCHAR(7), accrual_type VARCHAR(50), status VARCHAR(20) DEFAULT 'draft', "
                        "created_at TIMESTAMPTZ DEFAULT NOW())"))
        db.commit()
    except Exception:
        db.rollback()

    where = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if period:
        where.append("period = :period")
        params["period"] = period
    if accrual_type:
        where.append("accrual_type = :atype")
        params["atype"] = accrual_type

    rows = db.execute(
        text(f"""
            SELECT id, tenant_id, description, amount, account_number, counterpart_account,
                   period, accrual_type, status, created_at
            FROM domain_erp.accruals_provisions
            WHERE {' AND '.join(where)}
            ORDER BY period DESC, created_at DESC
        """),
        params,
    ).fetchall()
    return [
        AccrualItem(
            id=str(r[0]), tenant_id=r[1], description=r[2],
            amount=Decimal(str(r[3])), account_number=r[4], counterpart_account=r[5],
            period=r[6], accrual_type=r[7], status=r[8], created_at=r[9],
        )
        for r in rows
    ]


@router.post("", response_model=AccrualItem, status_code=201)
async def create_accrual_provision(
    item: AccrualItemCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create accrual or provision entry (draft)."""
    try:
        db.execute(text("CREATE TABLE IF NOT EXISTS domain_erp.accruals_provisions ("
                        "id VARCHAR(36) PRIMARY KEY, tenant_id VARCHAR(64), description VARCHAR(500), "
                        "amount NUMERIC(18,4), account_number VARCHAR(20), counterpart_account VARCHAR(20), "
                        "period VARCHAR(7), accrual_type VARCHAR(50), status VARCHAR(20) DEFAULT 'draft', "
                        "created_at TIMESTAMPTZ DEFAULT NOW())"))
        db.commit()
    except Exception:
        db.rollback()

    item_id = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_erp.accruals_provisions
            (id, tenant_id, description, amount, account_number, counterpart_account,
             period, accrual_type, status, created_at)
            VALUES (:id, :tid, :desc, :amt, :acct, :counter, :period, :atype, 'draft', NOW())
        """),
        {
            "id": item_id, "tid": tenant_id, "desc": item.description,
            "amt": item.amount, "acct": item.account_number,
            "counter": item.counterpart_account, "period": item.period,
            "atype": item.accrual_type,
        },
    )
    db.commit()
    return AccrualItem(
        id=item_id, tenant_id=tenant_id, **item.model_dump(), status="draft",
    )


def _fetch_accrual_or_404(db: Session, item_id: str, tenant_id: str) -> AccrualItem:
    row = db.execute(
        text("""
            SELECT id, tenant_id, description, amount, account_number, counterpart_account,
                   period, accrual_type, status, created_at
            FROM domain_erp.accruals_provisions
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": item_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Accrual/Provision not found")
    return AccrualItem(
        id=str(row[0]), tenant_id=row[1], description=row[2],
        amount=Decimal(str(row[3])), account_number=row[4], counterpart_account=row[5],
        period=row[6], accrual_type=row[7], status=row[8], created_at=row[9],
    )


@router.get("/{item_id}", response_model=AccrualItem)
async def get_accrual_provision(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get a single accrual/provision by ID."""
    return _fetch_accrual_or_404(db, item_id, tenant_id)


class AccrualItemUpdate(BaseModel):
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    amount: Optional[Decimal] = Field(default=None, ge=0)
    account_number: Optional[str] = Field(default=None, min_length=1, max_length=20)
    counterpart_account: Optional[str] = Field(default=None, min_length=1, max_length=20)
    period: Optional[str] = None
    accrual_type: Optional[str] = None


@router.put("/{item_id}", response_model=AccrualItem)
async def update_accrual_provision(
    item_id: str,
    payload: AccrualItemUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update a draft accrual/provision."""
    existing = _fetch_accrual_or_404(db, item_id, tenant_id)
    if existing.status == "posted":
        raise HTTPException(status_code=400, detail="Posted items cannot be edited")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return existing
    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = item_id
    updates["tid"] = tenant_id
    db.execute(
        text(f"UPDATE domain_erp.accruals_provisions SET {set_clauses} WHERE id = :id AND tenant_id = :tid"),
        updates,
    )
    db.commit()
    return _fetch_accrual_or_404(db, item_id, tenant_id)


@router.delete("/{item_id}", status_code=204)
async def delete_accrual_provision(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete a draft accrual/provision."""
    existing = _fetch_accrual_or_404(db, item_id, tenant_id)
    if existing.status == "posted":
        raise HTTPException(status_code=400, detail="Posted items cannot be deleted")
    db.execute(
        text("DELETE FROM domain_erp.accruals_provisions WHERE id = :id AND tenant_id = :tid"),
        {"id": item_id, "tid": tenant_id},
    )
    db.commit()


@router.post("/{item_id}/post", response_model=dict)
async def post_accrual_provision(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Post accrual/provision — creates GL journal entry."""
    row = db.execute(
        text("SELECT id, status FROM domain_erp.accruals_provisions WHERE id = :id AND tenant_id = :tid"),
        {"id": item_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Accrual/Provision not found")
    if row[1] == "posted":
        raise HTTPException(status_code=400, detail="Already posted")

    full = db.execute(
        text("SELECT * FROM domain_erp.accruals_provisions WHERE id = :id AND tenant_id = :tid"),
        {"id": item_id, "tid": tenant_id},
    ).fetchone()
    if not full:
        raise HTTPException(status_code=404, detail="Not found")

    je_id = uuid7()
    period = full[6]
    year, month = period.split("-")[:2]
    from calendar import monthrange
    last_day = monthrange(int(year), int(month))[1]
    entry_date = date(int(year), int(month), last_day)

    db.execute(
        text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, description,
             source, status, total_debit, total_credit, reference, created_at, updated_at)
            VALUES (:id, :tid, :en, :ed, :ed, :desc, 'accrual_provision', 'posted',
                    :amt, :amt, :ref, NOW(), NOW())
        """),
        {
            "id": je_id, "tid": tenant_id,
            "en": f"AP-{period}-{item_id[:8]}", "ed": entry_date,
            "desc": full[2], "amt": full[3], "ref": f"Abgrenzung {full[2][:30]}",
        },
    )
    db.execute(
        text("UPDATE domain_erp.accruals_provisions SET status = 'posted' WHERE id = :id AND tenant_id = :tid"),
        {"id": item_id, "tid": tenant_id},
    )
    db.commit()
    return {"ok": True, "journal_entry_id": je_id}
