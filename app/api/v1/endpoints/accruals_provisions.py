"""
Accruals and Provisions API
FIBU-CLS-03: Abgrenzungen / Rückstellungen
"""

from app.auth.finance_roles import finance_admin, finance_read, finance_write
from typing import List, Optional
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.exceptions import DomainError
from app.core.uuid7 import uuid7
from app.services import finance_freigabe
from app.services.finance_transaction_service import FinanceTransactionService

from app.api.v1.schemas.base import StatusResponse


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


@router.get("", response_model=List[AccrualItem], summary="Accruals provisions auflisten", dependencies=[Depends(finance_read)])
async def list_accruals_provisions(
    period: Optional[str] = Query(None, description="Filter by period YYYY-MM"),
    accrual_type: Optional[str] = Query(None, description="Filter: rechnungsabgrenzungsposten or rueckstellung"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """List accruals and provisions for a period."""
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
        """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
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


@router.post("", response_model=AccrualItem, status_code=201, summary="Accrual provision anlegen", dependencies=[Depends(finance_write)])
async def create_accrual_provision(
    item: AccrualItemCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create accrual or provision entry (draft)."""
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


@router.get("/{item_id}", response_model=AccrualItem, summary="Accrual provision abrufen", dependencies=[Depends(finance_read)])
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


@router.put("/{item_id}", response_model=AccrualItem, summary="Accrual provision aktualisieren", dependencies=[Depends(finance_write)])
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
    _ALLOWED_COLUMNS = frozenset(AccrualItemUpdate.model_fields.keys())
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if k in _ALLOWED_COLUMNS}
    if not updates:
        return existing
    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = item_id
    updates["tid"] = tenant_id
    db.execute(
        text(f"UPDATE domain_erp.accruals_provisions SET {set_clauses} WHERE id = :id AND tenant_id = :tid"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        updates,
    )
    db.commit()
    return _fetch_accrual_or_404(db, item_id, tenant_id)


@router.delete("/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Accrual provision löschen", dependencies=[Depends(finance_admin)])
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


@router.post("/{item_id}/post", response_model=StatusResponse, summary="Accrual provision erstellen", dependencies=[Depends(finance_write)])
async def post_accrual_provision(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: dict = Depends(finance_write),
):
    """Bucht die Abgrenzung/Rueckstellung: Soll ``account_number``, Haben ``counterpart_account``, Stichtag Periodenende.

    Gebucht wird ueber den kanonischen Buchungsdienst (Periodensperre, Konten, Sequenz und Hash-Kette) und mit der
    Kontrollpruefung der manuellen Hauptbuchbuchung. Vorher entstand hier ein Journalkopf mit Status ``posted``, aber
    ohne eine einzige Buchungszeile, ohne Periodenpruefung und ohne Hash - eine Buchung, die kein Konto bewegte.
    """
    item = _fetch_accrual_or_404(db, item_id, tenant_id)
    if item.status == "posted":
        raise HTTPException(status_code=400, detail="Already posted")
    try:
        year, month = (int(teil) for teil in item.period.split("-")[:2])
        stichtag = date(year, month, monthrange(year, month)[1])
    except (ValueError, TypeError) as fehler:
        raise HTTPException(status_code=422, detail=f"Periode {item.period!r} ist kein Monat (JJJJ-MM)") from fehler

    akteur = str(nutzer.get("sub") or "") if isinstance(nutzer, dict) else None
    buchung = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    try:
        eintrag = buchung.create(
            entry_number=f"AP-{item.period}-{item_id[:8]}",
            description=item.description[:200],
            entry_date=stichtag,
            reference=f"ABGR-{item_id}",
            source="accrual_provision",
            lines=[
                {"account_id": buchung.account_id_for_number(item.account_number),
                 "debit_amount": item.amount, "credit_amount": Decimal("0"), "description": item.description[:200]},
                {"account_id": buchung.account_id_for_number(item.counterpart_account),
                 "debit_amount": Decimal("0"), "credit_amount": item.amount, "description": item.description[:200]},
            ],
        )
        finance_freigabe.verlange_hauptbuchbuchung(db, tenant_id, str(eintrag.id), akteur)
        buchung.post(str(eintrag.id), posted_by=akteur)
        db.execute(
            text("UPDATE domain_erp.accruals_provisions SET status = 'posted' WHERE id = :id AND tenant_id = :tid"),
            {"id": item_id, "tid": tenant_id},
        )
        db.commit()
    except DomainError as fehler:
        db.rollback()
        raise HTTPException(status_code=fehler.http_status, detail=str(fehler)) from fehler
    except Exception:
        db.rollback()
        raise
    return {"ok": True, "journal_entry_id": str(eintrag.id)}
