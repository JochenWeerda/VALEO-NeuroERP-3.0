"""Kreditlimit-Verwaltung und Kreditstatus-Prüfung — thin-router, sqlalchemy.text()."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema


router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class CreditStatusOut(BaseModel):
    customer_id: str
    credit_limit: float
    current_exposure: float
    utilization_percent: float
    status: str  # OK | WARNING | BLOCKED
    warning_threshold_percent: float
    block_threshold_percent: float


class CreditLimitSet(BaseModel):
    credit_limit_eur: float = Field(..., gt=0)
    warning_threshold_percent: float = Field(default=80.0, ge=0, le=100)
    block_threshold_percent: float = Field(default=100.0, ge=0, le=200)


class CreditOverride(BaseModel):
    approved_by: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    valid_until: datetime


class CreditLimitOut(BaseModel):
    id: str
    customer_id: str
    credit_limit_eur: float
    warning_threshold_percent: float
    block_threshold_percent: float
    tenant_id: str


class BlockedCustomerOut(BaseModel):
    customer_id: str
    credit_limit: float
    current_exposure: float
    utilization_percent: float


# ---------------------------------------------------------------------------
# Internal helper (also called from sales_orders.py)
# ---------------------------------------------------------------------------

def get_credit_status_data(db: Session, customer_id: str, tenant_id: str) -> CreditStatusOut:
    """Compute credit status — usable from other endpoints."""
    # 1. credit limit
    cl_row = db.execute(
        text(
            """
            SELECT credit_limit_eur, warning_threshold_percent, block_threshold_percent
            FROM domain_crm.credit_limits
            WHERE customer_id = :cid AND tenant_id = :tid
            ORDER BY id DESC LIMIT 1
            """
        ),
        {"cid": customer_id, "tid": tenant_id},
    ).mappings().first()

    if cl_row:
        credit_limit = float(cl_row["credit_limit_eur"])
        warn_pct = float(cl_row["warning_threshold_percent"])
        block_pct = float(cl_row["block_threshold_percent"])
    else:
        # Fallback: customer.credit_limit column
        cust = db.execute(
            text("SELECT credit_limit FROM domain_crm.customers WHERE id = :cid AND tenant_id = :tid"),
            {"cid": customer_id, "tid": tenant_id},
        ).mappings().first()
        credit_limit = float(cust["credit_limit"]) if cust and cust.get("credit_limit") else 0.0
        warn_pct = 80.0
        block_pct = 100.0

    # 2. open invoices
    open_invoices = db.execute(
        text(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM domain_finance.finance_invoices
            WHERE customer_id = :cid AND tenant_id = :tid
              AND status NOT IN ('BEZAHLT', 'STORNIERT')
            """
        ),
        {"cid": customer_id, "tid": tenant_id},
    ).scalar() or 0.0

    # 3. open sales orders (not yet invoiced)
    open_orders = db.execute(
        text(
            """
            SELECT COALESCE(SUM(total_amount), 0)
            FROM domain_crm.sales_orders
            WHERE customer_id = :cid AND tenant_id = :tid
              AND status NOT IN ('storniert', 'abgeschlossen', 'invoiced')
              AND deleted_at IS NULL
            """
        ),
        {"cid": customer_id, "tid": tenant_id},
    ).scalar() or 0.0

    exposure = float(open_invoices) + float(open_orders)
    if credit_limit > 0:
        utilization = exposure / credit_limit * 100
    else:
        utilization = 0.0

    if credit_limit <= 0:
        credit_status = "OK"
    elif utilization >= block_pct:
        credit_status = "BLOCKED"
    elif utilization >= warn_pct:
        credit_status = "WARNING"
    else:
        credit_status = "OK"

    return CreditStatusOut(
        customer_id=customer_id,
        credit_limit=credit_limit,
        current_exposure=round(exposure, 2),
        utilization_percent=round(utilization, 2),
        status=credit_status,
        warning_threshold_percent=warn_pct,
        block_threshold_percent=block_pct,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/customers/{customer_id}/credit-status", response_model=CreditStatusOut, summary="Status credit")
async def credit_status(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return get_credit_status_data(db, customer_id, tenant_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")


@router.post("/customers/{customer_id}/credit-limit", response_model=CreditLimitOut, status_code=status.HTTP_200_OK, summary="Credit limit setzen")
async def set_credit_limit(
    customer_id: str,
    payload: CreditLimitSet,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        existing = db.execute(
            text(
                "SELECT id FROM domain_crm.credit_limits WHERE customer_id = :cid AND tenant_id = :tid ORDER BY id DESC LIMIT 1"
            ),
            {"cid": customer_id, "tid": tenant_id},
        ).mappings().first()

        now = datetime.now(timezone.utc)
        if existing:
            db.execute(
                text(
                    """
                    UPDATE domain_crm.credit_limits
                    SET credit_limit_eur = :limit, warning_threshold_percent = :warn, block_threshold_percent = :block
                    WHERE id = :id
                    """
                ),
                {
                    "limit": payload.credit_limit_eur,
                    "warn": payload.warning_threshold_percent,
                    "block": payload.block_threshold_percent,
                    "id": str(existing["id"]),
                },
            )
            record_id = str(existing["id"])
        else:
            record_id = str(uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO domain_crm.credit_limits
                      (id, customer_id, credit_limit_eur, warning_threshold_percent, block_threshold_percent, tenant_id, created_at)
                    VALUES
                      (:id, :cid, :limit, :warn, :block, :tid, :now)
                    """
                ),
                {
                    "id": record_id,
                    "cid": customer_id,
                    "limit": payload.credit_limit_eur,
                    "warn": payload.warning_threshold_percent,
                    "block": payload.block_threshold_percent,
                    "tid": tenant_id,
                    "now": now,
                },
            )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")

    return CreditLimitOut(
        id=record_id,
        customer_id=customer_id,
        credit_limit_eur=payload.credit_limit_eur,
        warning_threshold_percent=payload.warning_threshold_percent,
        block_threshold_percent=payload.block_threshold_percent,
        tenant_id=tenant_id,
    )


@router.post("/customers/{customer_id}/credit-override", status_code=status.HTTP_201_CREATED, summary="Override credit",
    response_model=IDResponse
)
async def credit_override(
    customer_id: str,
    payload: CreditOverride,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    oid = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_crm.credit_overrides
                  (id, customer_id, tenant_id, approved_by, reason, valid_until, created_at)
                VALUES
                  (:id, :cid, :tid, :approved_by, :reason, :valid_until, :now)
                """
            ),
            {
                "id": oid,
                "cid": customer_id,
                "tid": tenant_id,
                "approved_by": payload.approved_by,
                "reason": payload.reason,
                "valid_until": payload.valid_until,
                "now": now,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return {"id": oid, "customer_id": customer_id, "status": "override_granted", "valid_until": payload.valid_until}


@router.get("/credit-blocked-customers", response_model=list[BlockedCustomerOut], summary="Blocked customers auflisten")
async def list_blocked_customers(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        cust_rows = db.execute(
            text("SELECT id FROM domain_crm.customers WHERE tenant_id = :tid AND deleted_at IS NULL"),
            {"tid": tenant_id},
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")

    blocked = []
    for row in cust_rows:
        try:
            cs = get_credit_status_data(db, str(row["id"]), tenant_id)
            if cs.status == "BLOCKED":
                blocked.append(
                    BlockedCustomerOut(
                        customer_id=cs.customer_id,
                        credit_limit=cs.credit_limit,
                        current_exposure=cs.current_exposure,
                        utilization_percent=cs.utilization_percent,
                    )
                )
        except Exception:
            continue
    return blocked
