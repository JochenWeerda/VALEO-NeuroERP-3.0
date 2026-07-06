"""Order-to-Cash-Kette (DOM-SALES-004) — Angebot→Auftrag→Lieferschein→Rechnung (read-only)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.o2c_chain_service import O2CChainService

router = APIRouter(prefix="/sales", tags=["sales", "o2c"])


@router.get("/o2c/orders", response_model=dict, summary="Aufträge mit O2C-Vollständigkeit (Picker)")
def list_orders(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": O2CChainService(db, tenant_id).list_orders(limit=limit)}


@router.get("/o2c", response_model=dict, summary="O2C-Kette je Auftrag (Angebot→Auftrag→Lieferschein→Rechnung)")
def o2c(
    auftrag: str = Query(..., description="Auftragsnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return O2CChainService(db, tenant_id).trace(auftrag)
