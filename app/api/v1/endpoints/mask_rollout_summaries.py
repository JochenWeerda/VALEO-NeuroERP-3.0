"""Central screen-summary routes for batch mask rollouts (Waves 42–51)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.mask_rollout_catalog import get_rollout_spec
from app.core.tenant import get_tenant_id
from app.services.mask_rollout_summary_service import MaskRolloutSummaryService

router = APIRouter(prefix="/mask-rollouts", tags=["ui", "mask-rollout", "screen-summary"])


def _normalize_screen_id(screen_id: str) -> str:
    return screen_id.strip("/")


@router.get(
    "/{screen_id:path}/{entity_id}/screen-summary",
    response_model=dict[str, Any],
    summary="Rollout screen summary abrufen",
)
async def get_mask_rollout_screen_summary(
    screen_id: str,
    entity_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    normalized = _normalize_screen_id(screen_id)
    if get_rollout_spec(normalized) is None:
        raise HTTPException(status_code=404, detail=f"Unknown rollout screen {screen_id}")
    return MaskRolloutSummaryService(db, tenant_id).build_summary(normalized, entity_id)


@router.get(
    "/{screen_id:path}/{entity_id}/tabs/{tab_key}",
    response_model=dict[str, Any],
    summary="Rollout tab data abrufen",
)
async def get_mask_rollout_tab_data(
    screen_id: str,
    entity_id: str,
    tab_key: str,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: str | None = Query(None),
    sort: str | None = Query(None, description="Sortierfeld (Spalten-Key)"),
    sort_dir: str | None = Query(None, pattern="^(asc|desc)$", description="Sortierrichtung"),
    filter_plan: str | None = Query(None, description="JSON FilterPlan (machine-readable column filters)"),
    filter_plan_legacy: str | None = Query(
        None,
        alias="filterPlan",
        include_in_schema=False,
        description="Deprecated camelCase alias for filter_plan.",
    ),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    import json

    normalized = _normalize_screen_id(screen_id)
    if get_rollout_spec(normalized) is None:
        raise HTTPException(status_code=404, detail=f"Unknown rollout screen {screen_id}")
    parsed_filter_plan: dict | None = None
    raw_filter_plan = filter_plan or filter_plan_legacy
    if raw_filter_plan:
        try:
            parsed_filter_plan = json.loads(raw_filter_plan)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="filter_plan must be valid JSON")
    return MaskRolloutSummaryService(db, tenant_id).build_tab_data(
        normalized,
        entity_id,
        tab_key,
        page=page,
        limit=limit,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
        filter_plan=parsed_filter_plan,
    )
