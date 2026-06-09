"""KIM-S4 — Ansprechpartner-Erweiterung: Werbe-Präferenzen + Pseudonymisierung.

Eigener Router (prefix /crm/kim), separat von crm_kim.py (paralleler Codex-Slice).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_contact_ext_service import CrmContactExtService

router = APIRouter(prefix="/crm/kim", tags=["crm", "kim", "360"])


class MarketingPrefIn(BaseModel):
    categoryCode: str
    preference: str = "none"  # none | company | private
    categoryLabel: Optional[str] = None
    kundenNr: Optional[str] = None


class StatusOut(BaseModel):
    status: str = "success"


@router.get("/contacts/{contact_id}/marketing-prefs", summary="Werbe-/Marketingpräferenzen")
def list_marketing(
    contact_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return CrmContactExtService(db, tenant_id).list_marketing(contact_id)


@router.put("/contacts/{contact_id}/marketing-prefs", summary="Werbepräferenz setzen")
def set_marketing(
    contact_id: str,
    body: MarketingPrefIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmContactExtService(db, tenant_id).set_marketing(
        contact_id, body.categoryCode, body.preference,
        category_label=body.categoryLabel, kunden_nr=body.kundenNr,
    )


@router.post("/contacts/{contact_id}/pseudonymize", summary="Ansprechpartner DSGVO-pseudonymisieren")
def pseudonymize(
    contact_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmContactExtService(db, tenant_id).pseudonymize(contact_id)
