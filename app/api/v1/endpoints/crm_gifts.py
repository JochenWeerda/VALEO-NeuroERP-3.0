"""KIM-S3 — Kunden-Präsente-Endpoints (eigener Router, prefix /crm/kim).

Separat von crm_kim.py gehalten (paralleler Slice KIM-L3-S1-GAP-CLOSURE-001
besitzt crm_kim.py). Liefert kundenbezogene Präsente fürs CRM-Cockpit.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.crm_bundle_schemas import (
    GiftOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_gift_service import CrmGiftService

router = APIRouter(prefix="/crm/kim", tags=["crm", "kim", "360"])


class GiftIn(BaseModel):
    year: int
    date: Optional[str] = None
    occasion: Optional[str] = None
    contactId: Optional[str] = None
    giftName: Optional[str] = None
    quantity: Optional[float] = 1
    salesRepId: Optional[str] = None
    operatorId: Optional[str] = None
    representativeOfficerId: Optional[str] = None
    sequenceNumber: Optional[int] = None


class StatusOut(BaseModel):
    status: str = "success"


@router.get("/customers/{kunden_nr}/gifts", response_model=list[GiftOut], summary="Kunden-Präsente (Liste)")
def list_gifts(
    kunden_nr: str,
    year: Optional[int] = None,
    contactId: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return CrmGiftService(db, tenant_id).list(kunden_nr, year=year, contact_id=contactId)


@router.post("/customers/{kunden_nr}/gifts", response_model=GiftOut, summary="Präsent anlegen")
def create_gift(
    kunden_nr: str,
    body: GiftIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmGiftService(db, tenant_id).create(kunden_nr, body.model_dump())


@router.put("/gifts/{gift_id}", response_model=GiftOut, summary="Präsent bearbeiten")
def update_gift(
    gift_id: str,
    body: GiftIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmGiftService(db, tenant_id).update(gift_id, body.model_dump())


@router.delete("/gifts/{gift_id}", response_model=StatusOut, summary="Präsent löschen")
def delete_gift(
    gift_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    CrmGiftService(db, tenant_id).delete(gift_id)
    return StatusOut()
