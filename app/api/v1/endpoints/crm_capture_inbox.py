"""KIM Klärfall-Inbox — nicht zuordenbare Auto-Captures sichten und zuordnen.

Auto-erfasste Kommunikation ohne erkennbaren Kunden landet in der Inbox
(siehe CrmAutoCaptureService). Hier wird sie gelistet, einem Kunden zugeordnet
(legt den Kontakt in kunden_kontakte an) oder verworfen.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_capture_inbox_service import CrmCaptureInboxService

router = APIRouter(prefix="/crm/kim", tags=["crm", "kim", "360"])


class AssignIn(BaseModel):
    kundenNr: str
    resolvedBy: Optional[str] = None


class DismissIn(BaseModel):
    resolvedBy: Optional[str] = None


@router.get("/capture-inbox", response_model=dict[str, Any], summary="Klärfälle (nicht zugeordnete Auto-Captures) listen")
def list_inbox(
    status: str = Query("offen", description="offen | zugeordnet | verworfen | alle"),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = CrmCaptureInboxService(db, tenant_id)
    return {"items": svc.list(status=status, limit=limit), "open": svc.count_open()}


@router.post("/capture-inbox/{inbox_id}/assign", response_model=dict[str, Any], summary="Klärfall einem Kunden zuordnen")
def assign_inbox(
    inbox_id: str,
    body: AssignIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmCaptureInboxService(db, tenant_id).assign(
        inbox_id, body.kundenNr, resolved_by=body.resolvedBy
    )


@router.post("/capture-inbox/{inbox_id}/dismiss", response_model=dict[str, Any], summary="Klärfall verwerfen")
def dismiss_inbox(
    inbox_id: str,
    body: DismissIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmCaptureInboxService(db, tenant_id).dismiss(inbox_id, resolved_by=body.resolvedBy)
