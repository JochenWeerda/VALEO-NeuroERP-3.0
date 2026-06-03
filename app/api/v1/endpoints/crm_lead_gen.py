"""CRM Lead-Generierung — region-universale Lead-Kandidaten (GAP/LKV).

Read-only Vorschau-Endpoint über ``CrmLeadGenService`` für die gleichnamige Maske.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.crm_lead_gen_service import CrmLeadGenService

router = APIRouter(prefix="/crm/lead-generierung", tags=["crm", "prospecting"])


@router.get("/preview", summary="Lead-Kandidaten-Vorschau (GAP/LKV, region-universal)")
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
