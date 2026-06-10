"""Kontrakt-Erfüllungsstand (DOM-CON-004) — read-only."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.contract_fulfillment_service import ContractFulfillmentService

router = APIRouter(prefix="/contracts", tags=["contracts", "kontrakte", "agrar"])


@router.get("/fulfillment/list", summary="Kontrakte mit Erfüllungsgrad (Picker)")
def list_contracts(
    typ: str = Query("alle", description="EINKAUF | VERKAUF | alle"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ContractFulfillmentService(db, tenant_id).list_contracts(typ=typ, limit=limit)}


@router.get("/fulfillment", summary="Erfüllungsstand je Kontrakt (Kontrahiert vs. abgerufen)")
def fulfillment(
    kontrakt: str = Query(..., description="Kontraktnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ContractFulfillmentService(db, tenant_id).detail(kontrakt)
