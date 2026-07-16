"""Performance analytics API: ration version impact (FEED-PERF-033)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.rations_controlling_service import RationsControllingService

router = APIRouter(prefix="/feeding", tags=["feeding-performance"])


class VersionImpactOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ration_version_id: str
    activated_at: str
    window_days: int
    before: dict[str, Any]
    after: dict[str, Any]
    confidence: str


@router.get("/performance/version-impact", response_model=list[VersionImpactOut],
            summary="Vorher/Nachher-Auswertung je aktivierter Rationsversion (ehrliche Unsicherheit)")
async def version_impact(group_id: str, window_days: int = Query(default=14, ge=3, le=90),
                         db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id),
                         user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Leistungsauswertung.")
    service = RationsControllingService(db, tenant_id, str(user.get("sub") or "unknown"))
    return service.version_impact(group_id=group_id, window_days=window_days)
