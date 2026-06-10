"""Offene-Posten-Cockpit / OP-Aging (DOM-FIN-004) — read-only."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.finance_op_service import FinanceOpService

router = APIRouter(prefix="/finance", tags=["finance", "fibu", "op"])


@router.get("/offene-posten", summary="Offene Posten mit Aging/Mahnstufe/Skonto")
def offene_posten(
    typ: str = Query("alle", description="debitor | kreditor | alle"),
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return FinanceOpService(db, tenant_id).list_open_items(typ=typ, limit=limit)
