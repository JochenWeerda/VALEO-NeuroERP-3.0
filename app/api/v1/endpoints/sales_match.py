"""Auftrag-↔-Lieferschein-Positions-Match (DOM-SALES-004.2) — read-only."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.sales_match_service import SalesMatchService

router = APIRouter(prefix="/sales", tags=["sales", "o2c"])


@router.get("/match/orders", summary="Aufträge mit Positions-Match-Übersicht (Picker)")
def list_orders(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": SalesMatchService(db, tenant_id).list_orders(limit=limit)}


@router.get("/match", summary="Positions-Match Auftrag ↔ Lieferschein (Teil-/Überlieferung)")
def match(
    auftrag: str = Query(..., description="Auftragsnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return SalesMatchService(db, tenant_id).match(auftrag)
