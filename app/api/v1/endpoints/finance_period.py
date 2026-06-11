"""Periodenabschluss & Storno-Konsistenz (DOM-FIN-004.4)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.finance_period_service import FinancePeriodService, PeriodError

router = APIRouter(prefix="/finance", tags=["finance", "fibu", "abschluss"])


@router.get("/perioden", summary="Buchungsperioden mit Abschlussreife")
def list_periods(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": FinancePeriodService(db, tenant_id).list_periods()}


@router.get("/perioden/{period}/readiness", summary="Abschlussreife einer Periode")
def readiness(
    period: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return FinancePeriodService(db, tenant_id).readiness(period)


class CloseIn(BaseModel):
    force: bool = False
    bediener: Optional[str] = None


@router.post("/perioden/{period}/close", summary="Periode abschließen (sperren)")
def close_period(
    period: str,
    body: CloseIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return FinancePeriodService(db, tenant_id).close_period(period, bediener=body.bediener or "KIM", force=body.force)
    except PeriodError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


class ReopenIn(BaseModel):
    grund: str
    bediener: Optional[str] = None


@router.post("/perioden/{period}/reopen", summary="Periode wieder öffnen")
def reopen_period(
    period: str,
    body: ReopenIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return FinancePeriodService(db, tenant_id).reopen_period(period, body.grund, bediener=body.bediener or "KIM")
    except PeriodError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
