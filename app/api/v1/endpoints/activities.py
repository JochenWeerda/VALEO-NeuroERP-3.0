"""
CRM activity endpoints proxied via crm-core.
"""

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ....core.config import settings
from ....integrations import crm_core_client
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Activity, ActivityCreate, ActivityUpdate

router = APIRouter()


def _adapt_activity(core_activity: crm_core_client.CRMCoreActivity) -> dict:
    return {
        "id": core_activity.id,
        "type": core_activity.type,
        "title": core_activity.title,
        "customer": core_activity.customer_name or "",
        "contact_person": "",
        "date": core_activity.scheduled_at,
        "status": core_activity.status,
        "assigned_to": core_activity.assigned_to or "",
        "description": core_activity.description,
        "tenant_id": settings.DEFAULT_TENANT_ID,
        "created_at": core_activity.created_at,
        "updated_at": core_activity.updated_at,
    }


def _map_activity_payload(payload: ActivityCreate | ActivityUpdate) -> dict:
    body = payload.model_dump(exclude_unset=True)
    mapping = {
        "title": body.get("title"),
        "type": body.get("type"),
        "status": body.get("status"),
        "description": body.get("description"),
        "assigned_to": body.get("assigned_to"),
        "scheduled_at": body.get("date"),
    }
    return {k: v for k, v in mapping.items() if v is not None}


@router.get("/", response_model=PaginatedResponse[Activity])
async def list_activities(
    type_filter: str | None = Query(None, alias="type"),
    status_filter: str | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        activities, total = await crm_core_client.list_activities(
            activity_type=type_filter,
            status=status_filter,
            skip=skip,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list activities: {exc}") from exc

    items = [_adapt_activity(activity) for activity in activities]
    return PaginatedResponse[Activity](
        items=[Activity.model_validate(item) for item in items],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{activity_id}", response_model=Activity)
async def get_activity(activity_id: str):
    try:
        activity = await crm_core_client.get_activity(activity_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Activity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve activity: {exc}") from exc
    return Activity.model_validate(_adapt_activity(activity))


@router.post("/", response_model=Activity, status_code=status.HTTP_201_CREATED)
async def create_activity(payload: ActivityCreate):
    try:
        body = _map_activity_payload(payload)
        created = await crm_core_client.create_activity(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {exc}") from exc
    return Activity.model_validate(_adapt_activity(created))


@router.put("/{activity_id}", response_model=Activity)
async def update_activity(activity_id: str, payload: ActivityUpdate):
    try:
        body = _map_activity_payload(payload)
        updated = await crm_core_client.update_activity(activity_id, body)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Activity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update activity: {exc}") from exc
    return Activity.model_validate(_adapt_activity(updated))


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(activity_id: str):
    try:
        await crm_core_client.delete_activity(activity_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Activity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete activity: {exc}") from exc
