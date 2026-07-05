"""Kreditlimit-Prüfung & Billing-Status im O2C-Kontext (DOM-SALES-004.3) — read-only."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.sales_credit_service import SalesCreditService

router = APIRouter(prefix="/sales", tags=["sales", "o2c", "credit"])


@router.get("/credit-check/customers", response_model=dict, summary="Kunden mit Kreditlimit-Ampel (offene Exposure)")
def list_customers(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": SalesCreditService(db, tenant_id).list_customers(limit=limit)}


@router.get("/credit-check", response_model=dict, summary="Kreditlimit-Prüfung + Billing-Status je Auftrag")
def credit_check(
    auftrag: str = Query(..., description="Auftragsnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return SalesCreditService(db, tenant_id).order_credit(auftrag)
