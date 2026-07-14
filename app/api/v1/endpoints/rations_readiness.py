"""Feed inventory, analysis and price readiness API."""
from datetime import date
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.rations_readiness_service import RationsReadinessService

router = APIRouter(prefix="/readiness", tags=["rations-readiness"])

class ReadinessEvaluateIn(BaseModel):
    snapshot: dict[str, Any] = Field(min_length=1)
    as_of: date | None = None

@router.post("/evaluate", response_model=dict, summary="Rationsentwurf auf Bestand, Analyse und Preis pruefen")
async def evaluate_readiness(body: ReadinessEvaluateIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    return RationsReadinessService(db, tenant_id).evaluate(body.snapshot, as_of=body.as_of)

@router.get("/materials", response_model=list[dict], summary="Readiness der aktuell eingesetzten Futtermittel")
async def active_material_readiness(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    return RationsReadinessService(db, tenant_id).active_materials()
