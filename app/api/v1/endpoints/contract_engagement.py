"""Kontrakt-Engagement & Kontraktmahnung (DOM-CON-004.3).

Engagement-Sicht (offene Menge je Artikel/Partei, Netto-Position) read-only +
Kontraktmahnung (überfällig-untererfüllte Kontrakte; Mahnung erfassen, append-only).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.contract_engagement_service import ContractEngagementService, ReminderError

router = APIRouter(prefix="/contracts", tags=["contracts", "kontrakte", "agrar"])


@router.get("/engagement", summary="Engagement: offene Menge je Artikel (Netto) und je Partei")
def engagement(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ContractEngagementService(db, tenant_id).engagement()


@router.get("/dunning/candidates", summary="Mahnkandidaten: überfällige, untererfüllte Kontrakte")
def dunning_candidates(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ContractEngagementService(db, tenant_id).dunning_candidates()}


@router.get("/dunning/list", summary="Mahnungen eines Kontrakts")
def list_reminders(
    kontrakt: str = Query(..., description="Kontraktnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ContractEngagementService(db, tenant_id).list_reminders(kontrakt)}


class ReminderIn(BaseModel):
    kontrakt: str
    text: Optional[str] = None
    mahnstufe: Optional[int] = None
    bediener: Optional[str] = None


@router.post("/dunning", summary="Kontraktmahnung erfassen (append-only)")
def create_reminder(
    body: ReminderIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return ContractEngagementService(db, tenant_id).create_reminder(
            contract_ref=body.kontrakt, text_body=body.text,
            mahnstufe=body.mahnstufe, bediener=body.bediener or "KIM",
        )
    except ReminderError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
