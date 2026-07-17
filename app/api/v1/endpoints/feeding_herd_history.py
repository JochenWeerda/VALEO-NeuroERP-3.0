"""Group parameter history from herd deltas (FEED-HERD-043)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_herd_snapshot_service import FeedingHerdSnapshotService

router = APIRouter(prefix="/feeding", tags=["feeding-herd-history"])


class CondenseOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    group_id: str
    condensed_days: int
    snapshot_count: int


class SnapshotOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    group_id: str
    snapshot_date: str
    cow_count: int | None = None
    kpis: dict[str, Any]
    source: str
    condensed_at: datetime


class StalenessOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    group_id: str
    group_name: str
    last_confirmed_at: datetime
    days_since_confirmation: int
    stale: bool
    stale_after_days: int
    latest_snapshot_date: str | None = None


def _service(db: Session, tenant_id: str, user: User) -> FeedingHerdSnapshotService:
    return FeedingHerdSnapshotService(db, tenant_id, str(user.get("sub") or "unknown"))


@router.post("/groups/{group_id}/snapshots/condense", response_model=CondenseOut,
             summary="Herd-Deltas idempotent zu Tages-Snapshots der Gruppe verdichten")
async def condense_group_snapshots(group_id: str, db: Session = Depends(get_db),
                                   tenant_id: str = Depends(get_tenant_id),
                                   user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer die Snapshot-Verdichtung.")
    try:
        return _service(db, tenant_id, user).condense(group_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/groups/{group_id}/parameter-history", response_model=list[SnapshotOut],
            summary="Parameterhistorie der Gruppe (Tages-Snapshots, neueste zuerst)")
async def group_parameter_history(group_id: str, db: Session = Depends(get_db),
                                  tenant_id: str = Depends(get_tenant_id),
                                  user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Parameterhistorie.")
    try:
        return _service(db, tenant_id, user).history(group_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/groups/{group_id}/parameter-staleness", response_model=StalenessOut,
            summary="Alter der letzten Parameterbestaetigung (Veraltet-Warnung)")
async def group_parameter_staleness(group_id: str, db: Session = Depends(get_db),
                                    tenant_id: str = Depends(get_tenant_id),
                                    user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer den Parameterstatus.")
    try:
        return _service(db, tenant_id, user).staleness(group_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/groups/{group_id}/confirm-parameters", response_model=StalenessOut,
             summary="Gruppenparameter fachlich bestaetigen (setzt die Veraltet-Warnung zurueck)")
async def confirm_group_parameters(group_id: str, db: Session = Depends(get_db),
                                   tenant_id: str = Depends(get_tenant_id),
                                   user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung zum Bestaetigen der Gruppenparameter.")
    try:
        return _service(db, tenant_id, user).confirm_parameters(group_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
