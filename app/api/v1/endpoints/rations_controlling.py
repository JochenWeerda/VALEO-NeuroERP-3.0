"""Daily feeding controlling API."""

from datetime import date
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.rations_controlling_service import RationsControllingService

router = APIRouter(prefix="/controlling", tags=["rations-controlling"])


class DailyObservationIn(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    observation_date: date
    source: Literal["manual", "mixing_wagon", "herd_data", "import"] = "manual"
    source_ref: str = Field(min_length=1, max_length=200)
    cow_count: int | None = Field(default=None, ge=0)
    actual_dmi_kg_cow: float | None = Field(default=None, ge=0)
    actual_cost_eur_cow: float | None = Field(default=None, ge=0)
    milk_price_eur_kg: float | None = Field(default=None, ge=0)
    actual_milk_kg_cow: float | None = Field(default=None, ge=0)
    actual_fat_pct: float | None = Field(default=None, ge=0, le=20)
    actual_protein_pct: float | None = Field(default=None, ge=0, le=20)
    feed_n_kg_cow: float | None = Field(default=None, ge=0)
    actual_methane_kg_cow: float | None = Field(default=None, ge=0)
    methane_estimated: bool = False
    # MLP-/Milchguete-Kennzahlen (FEED-PERF-033); Provenienz via source-Feld.
    milk_urea_mg_dl: float | None = Field(default=None, ge=0, le=100)
    somatic_cell_count_k: float | None = Field(default=None, ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)


@router.post(
    "/observations",
    response_model=dict,
    status_code=201,
    summary="Taegliche Soll-Ist-Beobachtung erfassen",
)
async def record_observation(
    body: DailyObservationIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(
        user,
        WRITE_ROLES,
        detail="Keine Berechtigung zum Erfassen von Fuetterungs-Tageswerten.",
    )
    try:
        return RationsControllingService(
            db,
            tenant_id,
            str(user.get("sub") or "unknown"),
        ).record(body.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/series", response_model=list[dict], summary="Soll-Ist-Zeitreihe lesen")
async def get_series(
    group_id: str | None = None,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(
        user, READ_ROLES, detail="Keine Berechtigung zum Lesen der Soll-Ist-Zeitreihe."
    )
    return RationsControllingService(
        db, tenant_id, str(user.get("sub") or "unknown")
    ).series(group_id=group_id, date_from=date_from, date_to=date_to)
