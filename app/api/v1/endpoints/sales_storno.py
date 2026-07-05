"""Lieferungs-Storno & Gutschrift-Übersicht (DOM-SALES-004.4)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.sales_storno_service import SalesStornoService, StornoError

router = APIRouter(prefix="/sales", tags=["sales", "o2c", "storno"])


@router.get("/storno/status", response_model=dict, summary="Storno-/Gutschrift-Status je Auftrag")
def storno_status(
    auftrag: str = Query(..., description="Auftragsnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return SalesStornoService(db, tenant_id).order_storno_status(auftrag)


class StornoIn(BaseModel):
    grund: str
    bediener: Optional[str] = None


@router.post("/deliveries/{delivery_no}/storno", response_model=dict, summary="Lieferschein stornieren (durchgängig in den Match)")
def storno_delivery(
    delivery_no: str,
    body: StornoIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return SalesStornoService(db, tenant_id).storno_delivery(delivery_no, body.grund, body.bediener or "KIM")
    except StornoError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
