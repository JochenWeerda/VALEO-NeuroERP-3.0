"""Mahnlauf & Mahnstufen-Eskalation (DOM-FIN-004.2)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.finance_dunning_service import FinanceDunningService

router = APIRouter(prefix="/finance", tags=["finance", "fibu", "mahnwesen"])


@router.get("/mahnlauf/candidates", response_model=dict, summary="Mahnkandidaten (überfällige Debitoren-OP + nächste Stufe)")
def candidates(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": FinanceDunningService(db, tenant_id).candidates()}


@router.get("/mahnlauf/notices", response_model=dict, summary="Erzeugte Mahnungen")
def notices(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": FinanceDunningService(db, tenant_id).list_notices(limit=limit)}


class DunningRunIn(BaseModel):
    rechnungsnr: Optional[str] = None      # einzelne OP; sonst alle überfälligen
    bediener: Optional[str] = None


@router.post("/mahnlauf/run", response_model=dict, summary="Mahnlauf ausführen (Mahnungen erzeugen + Stufe eskalieren)")
def run(
    body: DunningRunIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return FinanceDunningService(db, tenant_id).run_dunning(rechnungsnr=body.rechnungsnr, bediener=body.bediener or "KIM")
