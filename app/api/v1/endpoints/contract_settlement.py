"""Kontrakt-Settlement-Übergabe & Storno (DOM-CON-004.4)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.contract_settlement_service import ContractSettlementService, SettlementError

router = APIRouter(prefix="/contracts", tags=["contracts", "kontrakte", "agrar"])


@router.get("/settlement/status", summary="Settlement-Status je Kontrakt (Bewegungen + Fixierungen)")
def settlement_status(
    kontrakt: str = Query(..., description="Kontraktnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ContractSettlementService(db, tenant_id).settlement_status(kontrakt)


class HandoverIn(BaseModel):
    kontrakt: str
    movementId: Optional[str] = None        # einzelne Bewegung; sonst alle offenen
    invoiceNo: Optional[str] = None
    bediener: Optional[str] = None


@router.post("/settlement", summary="Bewegung(en) an die Abrechnung übergeben")
def handover(
    body: HandoverIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return ContractSettlementService(db, tenant_id).handover(
            contract_ref=body.kontrakt, movement_id=body.movementId,
            invoice_no=body.invoiceNo, bediener=body.bediener or "KIM",
        )
    except SettlementError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


class StornoIn(BaseModel):
    grund: str
    bediener: Optional[str] = None


@router.post("/movements/{movement_id}/storno", summary="Abruf-Bewegung stornieren (frei werdender Abruf)")
def storno_movement(
    movement_id: str,
    body: StornoIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return ContractSettlementService(db, tenant_id).storno_movement(movement_id, body.grund, body.bediener or "KIM")
    except SettlementError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/fixings/{fixing_id}/storno", summary="Fixierung stornieren (frei werdende Fixiermenge)")
def storno_fixing(
    fixing_id: str,
    body: StornoIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return ContractSettlementService(db, tenant_id).storno_fixing(fixing_id, body.grund, body.bediener or "KIM")
    except SettlementError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
