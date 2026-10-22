"""Kunden-Ownership (DOM-CRM-004.3) — Zuordnung/Übergabe Außendienst/Innendienst."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.crm_bundle_schemas import (
    ByOwnerOut,
    OwnershipHistoryOut,
    OwnershipOut,
    UnassignedOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_ownership_service import CrmOwnershipService

router = APIRouter(prefix="/crm", tags=["crm", "ownership"])


class OwnershipIn(BaseModel):
    salesRep: Optional[str] = None
    dispatcher: Optional[str] = None
    grund: Optional[str] = None
    bediener: Optional[str] = None


@router.get("/ownership/unassigned", response_model=UnassignedOut, summary="Kunden ohne Außendienst-Zuordnung (Worklist)")
def unassigned(
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmOwnershipService(db, tenant_id).unassigned(limit=limit)


@router.get("/ownership/by-owner", response_model=ByOwnerOut, summary="Kunden eines Außendienst-Owners (Workload)")
def by_owner(
    salesRep: str = Query(..., description="Außendienst-Kürzel"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmOwnershipService(db, tenant_id).by_owner(salesRep)


@router.get("/{kunden_nr}/ownership", response_model=OwnershipOut, summary="Ownership eines Kunden abrufen")
def get_ownership(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmOwnershipService(db, tenant_id).get(kunden_nr)


@router.put("/{kunden_nr}/ownership", response_model=OwnershipOut, summary="Ownership setzen/übergeben")
def set_ownership(
    kunden_nr: str,
    body: OwnershipIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmOwnershipService(db, tenant_id).set(
        kunden_nr, sales_rep=body.salesRep, dispatcher=body.dispatcher,
        grund=body.grund, bediener=body.bediener or "KIM",
    )


@router.get("/{kunden_nr}/ownership/history", response_model=OwnershipHistoryOut, summary="Übergabe-Historie eines Kunden")
def ownership_history(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": CrmOwnershipService(db, tenant_id).history(kunden_nr)}
