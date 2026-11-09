"""
Retouren (SALES-DLV-02/03/04). Gutschriften liegen seit BELEG-052 in DocFlow.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.customer_sales_eligibility import (
    assert_customer_allowed_for_delivery,
)
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import StatusResponse
from app.documents.router_helpers import eigener_beleg, get_repository, save_to_store
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter(prefix="/sales", tags=["sales", "credit-notes", "returns"])


def _resolve_sales_payload_tenant(payload_tenant_id: Optional[str], tenant_id: str) -> str:
    requested_tenant = (payload_tenant_id or "").strip()
    if requested_tenant and requested_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Payload belongs to a different tenant")
    return tenant_id


# Gutschriften: seit BELEG-052 (09.11.2026) in DocFlow (Belegart sales_credit_memo, app/services/gutschrift_docflow.py);
# Buchungsvorschlaege der Agenten in gutschrift_vorschlaege.py. Hier bleiben die Retouren.


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


@router.post("/returns", response_model=ReturnOut, status_code=201, summary="Return anlegen", dependencies=SCHREIBEN["VERKAUF"])
async def create_return(
    payload: ReturnCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a return/Retoure."""
    tid = _resolve_sales_payload_tenant(payload.tenant_id, tenant_id)
    assert_customer_allowed_for_delivery(db, tid, payload.customer_id)
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

    # Belegbruch schließen: Lieferschein und Rechnung als retourniert markieren
    if payload.delivery_note_reference:
        try:
            db.execute(
                text("""
                    UPDATE domain_sales.delivery_notes
                    SET status = 'returned', updated_at = NOW()
                    WHERE (id = :ref OR delivery_note_number = :ref)
                      AND tenant_id = :tid
                      AND status NOT IN ('returned', 'BERECHNET')
                """),
                {"ref": payload.delivery_note_reference, "tid": tid},
            )
            db.commit()
        except Exception:  # noqa: BLE001 — Lieferschein-Update nicht kritisch
            pass

    if payload.invoice_reference:
        try:
            repo = get_repository(db)
            inv = eigener_beleg("sales_invoice", payload.invoice_reference, tid, repo)
            if inv and inv.get("status") not in ("STORNIERT", "GUTGESCHRIEBEN"):
                inv["status"] = "GUTGESCHRIEBEN"
                save_to_store("sales_invoice", payload.invoice_reference, inv, repo)
        except Exception:  # noqa: BLE001 — Rechnungsstatus-Update nicht kritisch
            pass

    return ReturnOut(id=ret_id, tenant_id=tid, **payload.model_dump(exclude={"tenant_id"}))


@router.get("/returns", response_model=List[ReturnOut], summary="Returns auflisten")
async def list_returns(
    tenant_id: str = Depends(get_tenant_id),
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
        """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
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


@router.delete("/returns/{return_id}", status_code=204, response_class=Response, response_model=None, summary="Return löschen", dependencies=SCHREIBEN["VERKAUF"])
async def delete_return(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("SELECT id, status FROM domain_sales.sales_returns WHERE id = :id AND tenant_id = :tid"),
        {"id": return_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Retoure nicht gefunden")
    if row[1] == "completed":
        raise HTTPException(status_code=400, detail="Abgeschlossene Retouren können nicht gelöscht werden")
    db.execute(
        text("DELETE FROM domain_sales.sales_returns WHERE id = :id AND tenant_id = :tid"),
        {"id": return_id, "tid": tenant_id},
    )
    db.commit()


@router.patch("/returns/{return_id}/status", response_model=StatusResponse, summary="Return status aktualisieren", dependencies=SCHREIBEN["VERKAUF"])
async def update_return_status(
    return_id: str,
    new_status: str = Query(..., description="New status: open, processing, completed, cancelled"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update return status."""
    valid = {"open", "processing", "completed", "cancelled"}
    if new_status not in valid:
        raise HTTPException(status_code=400, detail=f"Status muss einer von {valid} sein")
    existing = db.execute(
        text("SELECT id FROM domain_sales.sales_returns WHERE id = :id AND tenant_id = :tid"),
        {"id": return_id, "tid": tenant_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Retoure nicht gefunden")
    db.execute(
        text(
            "UPDATE domain_sales.sales_returns SET status = :s, updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": return_id, "s": new_status, "tid": tenant_id},
    )
    db.commit()
    return {"ok": True, "return_id": return_id, "status": new_status}
