"""
Sales Credit Notes (Gutschriften) and Returns (Retouren) endpoints.
SALES-DLV-02/03/04: Retouren, Gutschriften, Versand
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.uuid7 import uuid7
from app.core.fibu_audit import log_fibu_audit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sales", tags=["sales", "credit-notes", "returns"])

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


# ---------------------------------------------------------------------------
# Credit Notes
# ---------------------------------------------------------------------------

class CreditNoteLineInput(BaseModel):
    article_number: Optional[str] = None
    description: str
    quantity: Decimal = Field(ge=Decimal("0"))
    unit_price: Decimal = Field(ge=Decimal("0"))
    tax_rate: Decimal = Field(default=Decimal("19"))


class CreditNoteLineOut(CreditNoteLineInput):
    id: str
    line_total: Decimal


class CreditNoteBase(BaseModel):
    credit_note_number: str = Field(..., min_length=1, max_length=64)
    customer_id: str
    customer_name: Optional[str] = None
    invoice_reference: Optional[str] = None
    reason: str = Field(..., min_length=1, max_length=500)
    total_amount: Decimal = Decimal("0")
    currency: str = "EUR"
    status: str = "draft"
    notes: Optional[str] = None
    lines: List[CreditNoteLineInput] = Field(default_factory=list)


class CreditNoteCreate(CreditNoteBase):
    tenant_id: Optional[str] = None


class CreditNoteOut(CreditNoteBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@router.post("/credit-notes", response_model=CreditNoteOut, status_code=201)
async def create_credit_note(
    payload: CreditNoteCreate,
    request: Request,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Create a sales credit note (Gutschrift)."""
    tid = payload.tenant_id or tenant_id
    cn_id = uuid7()

    total = sum(
        line.quantity * line.unit_price for line in payload.lines
    ) if payload.lines else payload.total_amount

    db.execute(
        text("""
            INSERT INTO domain_sales.sales_credit_notes
            (id, tenant_id, credit_note_number, customer_id, customer_name,
             invoice_reference, reason, total_amount, currency, status, notes,
             created_at, updated_at)
            VALUES (:id, :tid, :cn, :cid, :cname, :iref, :reason,
                    :total, :cur, :status, :notes, NOW(), NOW())
        """),
        {
            "id": cn_id, "tid": tid, "cn": payload.credit_note_number,
            "cid": payload.customer_id, "cname": payload.customer_name,
            "iref": payload.invoice_reference, "reason": payload.reason,
            "total": total, "cur": payload.currency,
            "status": payload.status, "notes": payload.notes,
        },
    )

    for i, line in enumerate(payload.lines, 1):
        line_id = uuid7()
        db.execute(
            text("""
                INSERT INTO domain_sales.sales_credit_note_lines
                (id, credit_note_id, line_number, article_number, description,
                 quantity, unit_price, tax_rate, line_total)
                VALUES (:id, :cnid, :ln, :anr, :desc, :qty, :up, :tax,
                        :total)
            """),
            {
                "id": line_id, "cnid": cn_id, "ln": i,
                "anr": line.article_number, "desc": line.description,
                "qty": line.quantity, "up": line.unit_price,
                "tax": line.tax_rate,
                "total": line.quantity * line.unit_price,
            },
        )

    db.commit()
    log_fibu_audit(
        db, tid, "create", "sales_credit_note", cn_id,
        {"credit_note_number": payload.credit_note_number, "total": float(total)},
        request=request,
    )
    return CreditNoteOut(
        id=cn_id, tenant_id=tid,
        credit_note_number=payload.credit_note_number,
        customer_id=payload.customer_id, customer_name=payload.customer_name,
        invoice_reference=payload.invoice_reference, reason=payload.reason,
        total_amount=total, currency=payload.currency,
        status=payload.status, notes=payload.notes, lines=payload.lines,
    )


@router.get("/credit-notes", response_model=List[CreditNoteOut])
async def list_credit_notes(
    tenant_id: str = Query(DEFAULT_TENANT),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List sales credit notes."""
    where = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if status:
        where.append("status = :status")
        params["status"] = status
    if customer_id:
        where.append("customer_id = :cid")
        params["cid"] = customer_id

    rows = db.execute(
        text(f"""
            SELECT id, tenant_id, credit_note_number, customer_id, customer_name,
                   invoice_reference, reason, total_amount, currency, status, notes,
                   created_at, updated_at
            FROM domain_sales.sales_credit_notes
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
        """),
        params,
    ).fetchall()
    return [
        CreditNoteOut(
            id=str(r[0]), tenant_id=r[1], credit_note_number=r[2],
            customer_id=r[3], customer_name=r[4], invoice_reference=r[5],
            reason=r[6], total_amount=Decimal(str(r[7])),
            currency=r[8], status=r[9], notes=r[10],
            created_at=r[11], updated_at=r[12],
        )
        for r in rows
    ]


@router.post("/credit-notes/{cn_id}/post", response_model=dict)
async def post_credit_note(
    cn_id: str,
    request: Request,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Post a credit note — creates GL reversal entry and updates OP."""
    row = db.execute(
        text("SELECT id, tenant_id, credit_note_number, customer_id, total_amount, status FROM domain_sales.sales_credit_notes WHERE id = :id"),
        {"id": cn_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Gutschrift nicht gefunden")
    if row[5] == "posted":
        raise HTTPException(status_code=400, detail="Gutschrift bereits gebucht")

    total = Decimal(str(row[4]))
    je_id = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, description,
             source, status, total_debit, total_credit, reference, created_at, updated_at)
            VALUES (:id, :tid, :en, NOW(), NOW(), :desc,
                    'sales_credit_note', 'posted', :total, :total, :ref, NOW(), NOW())
        """),
        {
            "id": je_id, "tid": row[1],
            "en": f"GS-{row[2]}", "desc": f"Gutschrift {row[2]}",
            "total": total, "ref": row[2],
        },
    )

    db.execute(
        text("UPDATE domain_sales.sales_credit_notes SET status = 'posted', updated_at = NOW() WHERE id = :id"),
        {"id": cn_id},
    )
    db.commit()
    log_fibu_audit(db, row[1], "post", "sales_credit_note", cn_id, {"total": float(total)}, request=request)
    return {"ok": True, "journal_entry_id": je_id}


# ---------------------------------------------------------------------------
# Returns / Retouren
# ---------------------------------------------------------------------------

class ReturnBase(BaseModel):
    return_number: str = Field(..., min_length=1, max_length=64)
    customer_id: str
    customer_name: Optional[str] = None
    delivery_note_reference: Optional[str] = None
    invoice_reference: Optional[str] = None
    reason: str = Field(..., min_length=1, max_length=500)
    return_type: str = "full"
    status: str = "open"
    notes: Optional[str] = None


class ReturnCreate(ReturnBase):
    tenant_id: Optional[str] = None


class ReturnOut(ReturnBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@router.post("/returns", response_model=ReturnOut, status_code=201)
async def create_return(
    payload: ReturnCreate,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Create a return/Retoure."""
    tid = payload.tenant_id or tenant_id
    ret_id = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_sales.sales_returns
            (id, tenant_id, return_number, customer_id, customer_name,
             delivery_note_reference, invoice_reference, reason,
             return_type, status, notes, created_at, updated_at)
            VALUES (:id, :tid, :rn, :cid, :cname, :dnref, :iref, :reason,
                    :rtype, :status, :notes, NOW(), NOW())
        """),
        {
            "id": ret_id, "tid": tid, "rn": payload.return_number,
            "cid": payload.customer_id, "cname": payload.customer_name,
            "dnref": payload.delivery_note_reference,
            "iref": payload.invoice_reference,
            "reason": payload.reason, "rtype": payload.return_type,
            "status": payload.status, "notes": payload.notes,
        },
    )
    db.commit()
    return ReturnOut(id=ret_id, tenant_id=tid, **payload.model_dump(exclude={"tenant_id"}))


@router.get("/returns", response_model=List[ReturnOut])
async def list_returns(
    tenant_id: str = Query(DEFAULT_TENANT),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List returns."""
    where = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if status:
        where.append("status = :status")
        params["status"] = status

    rows = db.execute(
        text(f"""
            SELECT id, tenant_id, return_number, customer_id, customer_name,
                   delivery_note_reference, invoice_reference, reason,
                   return_type, status, notes, created_at, updated_at
            FROM domain_sales.sales_returns
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
        """),
        params,
    ).fetchall()
    return [
        ReturnOut(
            id=str(r[0]), tenant_id=r[1], return_number=r[2],
            customer_id=r[3], customer_name=r[4],
            delivery_note_reference=r[5], invoice_reference=r[6],
            reason=r[7], return_type=r[8], status=r[9], notes=r[10],
            created_at=r[11], updated_at=r[12],
        )
        for r in rows
    ]


@router.patch("/returns/{return_id}/status", response_model=dict)
async def update_return_status(
    return_id: str,
    new_status: str = Query(..., description="New status: open, processing, completed, cancelled"),
    db: Session = Depends(get_db),
):
    """Update return status."""
    valid = {"open", "processing", "completed", "cancelled"}
    if new_status not in valid:
        raise HTTPException(status_code=400, detail=f"Status muss einer von {valid} sein")
    existing = db.execute(
        text("SELECT id FROM domain_sales.sales_returns WHERE id = :id"),
        {"id": return_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Retoure nicht gefunden")
    db.execute(
        text("UPDATE domain_sales.sales_returns SET status = :s, updated_at = NOW() WHERE id = :id"),
        {"id": return_id, "s": new_status},
    )
    db.commit()
    return {"ok": True, "return_id": return_id, "status": new_status}
