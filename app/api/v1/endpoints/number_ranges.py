"""Admin API for configurable number ranges (Debitor/Kreditor accounts, partner numbers)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant_context import get_current_tenant_id
from app.services.number_range_service import NumberRangeService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin", "number-ranges"])


class NumberRangeOut(BaseModel):
    id: str
    tenant_id: str
    range_type: str
    prefix: str
    start_number: int
    current_value: int
    digit_count: int
    reserved_prefix_digits: int
    is_active: bool
    next_number: Optional[str] = None


class NumberRangeConfigRequest(BaseModel):
    range_type: str = Field(..., description="z.B. debtor_account, creditor_account, partner_number")
    prefix: str = Field(default="", max_length=20)
    start_number: int = Field(default=10000, ge=1)
    digit_count: int = Field(default=5, ge=1, le=10)
    reserved_prefix_digits: int = Field(default=1, ge=0, le=3)


def _to_out(nr, svc: NumberRangeService, tenant_id: str) -> dict[str, Any]:
    return {
        "id": nr.id,
        "tenant_id": nr.tenant_id,
        "range_type": nr.range_type,
        "prefix": nr.prefix,
        "start_number": nr.start_number,
        "current_value": nr.current_value,
        "digit_count": nr.digit_count,
        "reserved_prefix_digits": nr.reserved_prefix_digits,
        "is_active": nr.is_active,
        "next_number": svc.peek_next(nr.range_type, tenant_id),
    }


@router.get("/")
def list_number_ranges(
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    tenant_id = get_current_tenant_id()
    svc = NumberRangeService(db)
    ranges = svc.list_ranges(tenant_id)
    return [_to_out(r, svc, tenant_id) for r in ranges]


@router.post("/", status_code=201)
def configure_number_range(
    body: NumberRangeConfigRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    tenant_id = get_current_tenant_id()
    svc = NumberRangeService(db)
    try:
        nr = svc.configure(
            tenant_id=tenant_id,
            range_type=body.range_type,
            prefix=body.prefix,
            start_number=body.start_number,
            digit_count=body.digit_count,
            reserved_prefix_digits=body.reserved_prefix_digits,
        )
        db.commit()
        db.refresh(nr)
        return _to_out(nr, svc, tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{range_type}/peek")
def peek_next_number(
    range_type: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    tenant_id = get_current_tenant_id()
    svc = NumberRangeService(db)
    next_nr = svc.peek_next(range_type, tenant_id)
    if next_nr is None:
        raise HTTPException(status_code=404, detail=f"Kein Nummernkreis fuer '{range_type}' konfiguriert")
    return {"range_type": range_type, "next_number": next_nr}
