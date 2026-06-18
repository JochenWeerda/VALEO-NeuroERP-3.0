"""CRM Lead-Generierung — region-universale Lead-Kandidaten (GAP/LKV).

Read-only Vorschau-Endpoint über ``CrmLeadGenService`` für die gleichnamige Maske.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import EntityNotFoundError
from app.core.tenant import get_tenant_id
from app.services.crm_lead_gen_service import CrmLeadGenService

router = APIRouter(prefix="/crm/lead-generierung", tags=["crm", "prospecting"])


class LeadKandidatIn(BaseModel):
    name: str
    plz: Optional[str] = None
    ort: Optional[str] = None
    strasse: Optional[str] = None
    score: Optional[float] = None
    quelle: Optional[str] = None
    score_label: Optional[str] = None


class UebernehmenBody(BaseModel):
    kandidaten: list[LeadKandidatIn]


@router.get("/preview", response_model=dict[str, Any], summary="Lead-Kandidaten-Vorschau (GAP/LKV, region-universal)")
def lead_preview(
    quelle: str = Query("gap", description="gap | lkv | beide"),
    plz_min: Optional[str] = Query(None, description="PLZ von (z. B. 26500)"),
    plz_max: Optional[str] = Query(None, description="PLZ bis (z. B. 26999)"),
    top_pct: float = Query(0.10, ge=0.01, le=1.0, description="Top-Anteil (0.10 = 10%)"),
    max_leads: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return CrmLeadGenService(db).preview(
        quelle=quelle, plz_min=plz_min, plz_max=plz_max, top_pct=top_pct, max_leads=max_leads
    )


@router.get("/leads", response_model=dict[str, Any], summary="Übernommene CRM-Leads auflisten")
def list_leads(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmLeadGenService(db, tenant_id).list_leads(search)


@router.get("/leads/{lead_id}", response_model=dict[str, Any], summary="Übernommenen CRM-Lead abrufen")
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    lead = CrmLeadGenService(db, tenant_id).get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    return lead


@router.get("/leads-count", response_model=dict[str, Any], summary="Anzahl übernommener CRM-Leads")
def leads_count(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return {"count": CrmLeadGenService(db, tenant_id).leads_count()}


@router.post("/uebernehmen", response_model=dict[str, Any], summary="Kandidaten als CRM-Leads übernehmen")
def uebernehmen(
    body: UebernehmenBody,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmLeadGenService(db, tenant_id).create_leads([k.model_dump() for k in body.kandidaten])


@router.post("/leads/{lead_id}/convert", response_model=dict[str, Any], summary="Lead in Kunden konvertieren")
def convert_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return CrmLeadGenService(db, tenant_id).convert_lead(lead_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
