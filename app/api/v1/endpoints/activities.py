"""
CRM activity endpoints proxied via crm-core.
"""

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from ....core.config import settings
from ....integrations import crm_core_client
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Activity, ActivityCreate, ActivityUpdate

router = APIRouter()


class _StringListItem(BaseModel):
    value: str = Field(..., min_length=1, max_length=200)


class _FollowUpActionItem(BaseModel):
    value: dict[str, Any] | str


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
        "main_topics": core_activity.main_topics or [],
        "orders_placed": core_activity.orders_placed or [],
        "follow_up_actions": core_activity.follow_up_actions or [],
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


def _raise_core_error(exc: Exception, not_found_detail: str, default_detail: str) -> None:
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail=not_found_detail) from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    raise HTTPException(status_code=500, detail=default_detail) from exc


async def _get_activity_or_404(activity_id: str) -> crm_core_client.CRMCoreActivity:
    try:
        return await crm_core_client.get_activity(activity_id)
    except Exception as exc:
        _raise_core_error(exc, "Activity not found", f"Failed to retrieve activity: {exc}")
    raise HTTPException(status_code=500, detail="Failed to retrieve activity")


def _validate_item_index(items: list[Any], item_index: int, field_label: str) -> None:
    if item_index < 0 or item_index >= len(items):
        raise HTTPException(status_code=404, detail=f"{field_label} item not found")


async def _load_list_field(activity_id: str, field_name: str) -> list[Any]:
    activity = await _get_activity_or_404(activity_id)
    value = getattr(activity, field_name, None)
    return list(value or [])


async def _replace_list_field(activity_id: str, field_name: str, items: list[Any]) -> list[Any]:
    try:
        updated = await crm_core_client.update_activity(activity_id, {field_name: items})
    except Exception as exc:
        _raise_core_error(exc, "Activity not found", f"Failed to update {field_name}: {exc}")
    value = getattr(updated, field_name, None)
    return list(value or [])


@router.get("/", response_model=PaginatedResponse[Activity], summary="Activities auflisten")
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


@router.get("/{activity_id}", response_model=Activity, summary="Activity abrufen")
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


@router.post("/", response_model=Activity, status_code=status.HTTP_201_CREATED, summary="Activity anlegen")
async def create_activity(payload: ActivityCreate):
    try:
        body = _map_activity_payload(payload)
        created = await crm_core_client.create_activity(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {exc}") from exc
    return Activity.model_validate(_adapt_activity(created))


@router.put("/{activity_id}", response_model=Activity, summary="Activity aktualisieren")
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


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Activity löschen",
    response_model=None
)
async def delete_activity(activity_id: str):
    try:
        await crm_core_client.delete_activity(activity_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Activity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete activity: {exc}") from exc


@router.get("/{activity_id}/main-topics", response_model=list[str], summary="Activity main topics auflisten")
async def list_activity_main_topics(activity_id: str):
    items = await _load_list_field(activity_id, "main_topics")
    return [str(item) for item in items]


@router.post(
    "/{activity_id}/main-topics",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Activity main topic anlegen",
)
async def create_activity_main_topic(activity_id: str, payload: _StringListItem):
    items = [str(item) for item in await _load_list_field(activity_id, "main_topics")]
    items.append(payload.value)
    updated = await _replace_list_field(activity_id, "main_topics", items)
    return str(updated[-1])


@router.put("/{activity_id}/main-topics/{item_index}", response_model=str, summary="Activity main topic replace")
async def replace_activity_main_topic(
    activity_id: str,
    payload: _StringListItem,
    item_index: int = Path(..., ge=0),
):
    items = [str(item) for item in await _load_list_field(activity_id, "main_topics")]
    _validate_item_index(items, item_index, "Main topic")
    items[item_index] = payload.value
    updated = await _replace_list_field(activity_id, "main_topics", items)
    return str(updated[item_index])


@router.delete("/{activity_id}/main-topics/{item_index}", status_code=status.HTTP_204_NO_CONTENT, summary="Activity main topic löschen",
    response_model=None
)
async def delete_activity_main_topic(activity_id: str, item_index: int = Path(..., ge=0)):
    items = [str(item) for item in await _load_list_field(activity_id, "main_topics")]
    _validate_item_index(items, item_index, "Main topic")
    del items[item_index]
    await _replace_list_field(activity_id, "main_topics", items)


@router.get("/{activity_id}/orders-placed", response_model=list[str], summary="Activity orders placed auflisten")
async def list_activity_orders_placed(activity_id: str):
    items = await _load_list_field(activity_id, "orders_placed")
    return [str(item) for item in items]


@router.post(
    "/{activity_id}/orders-placed",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Activity order placed anlegen",
)
async def create_activity_order_placed(activity_id: str, payload: _StringListItem):
    items = [str(item) for item in await _load_list_field(activity_id, "orders_placed")]
    items.append(payload.value)
    updated = await _replace_list_field(activity_id, "orders_placed", items)
    return str(updated[-1])


@router.put("/{activity_id}/orders-placed/{item_index}", response_model=str, summary="Activity order placed replace")
async def replace_activity_order_placed(
    activity_id: str,
    payload: _StringListItem,
    item_index: int = Path(..., ge=0),
):
    items = [str(item) for item in await _load_list_field(activity_id, "orders_placed")]
    _validate_item_index(items, item_index, "Order")
    items[item_index] = payload.value
    updated = await _replace_list_field(activity_id, "orders_placed", items)
    return str(updated[item_index])


@router.delete("/{activity_id}/orders-placed/{item_index}", status_code=status.HTTP_204_NO_CONTENT, summary="Activity order placed löschen",
    response_model=None
)
async def delete_activity_order_placed(activity_id: str, item_index: int = Path(..., ge=0)):
    items = [str(item) for item in await _load_list_field(activity_id, "orders_placed")]
    _validate_item_index(items, item_index, "Order")
    del items[item_index]
    await _replace_list_field(activity_id, "orders_placed", items)


@router.get("/{activity_id}/follow-up-actions", response_model=list[dict[str, Any] | str], summary="Activity follow up actions auflisten")
async def list_activity_follow_up_actions(activity_id: str):
    return await _load_list_field(activity_id, "follow_up_actions")


@router.post(
    "/{activity_id}/follow-up-actions",
    response_model=dict[str, Any] | str,
    status_code=status.HTTP_201_CREATED,
    summary="Activity follow up action anlegen",
)
async def create_activity_follow_up_action(activity_id: str, payload: _FollowUpActionItem):
    items = await _load_list_field(activity_id, "follow_up_actions")
    items.append(payload.value)
    updated = await _replace_list_field(activity_id, "follow_up_actions", items)
    return updated[-1]


@router.put("/{activity_id}/follow-up-actions/{item_index}", response_model=dict[str, Any] | str, summary="Activity follow up action replace")
async def replace_activity_follow_up_action(
    activity_id: str,
    payload: _FollowUpActionItem,
    item_index: int = Path(..., ge=0),
):
    items = await _load_list_field(activity_id, "follow_up_actions")
    _validate_item_index(items, item_index, "Follow-up action")
    items[item_index] = payload.value
    updated = await _replace_list_field(activity_id, "follow_up_actions", items)
    return updated[item_index]


@router.delete("/{activity_id}/follow-up-actions/{item_index}", status_code=status.HTTP_204_NO_CONTENT, summary="Activity follow up action löschen",
    response_model=None
)
async def delete_activity_follow_up_action(activity_id: str, item_index: int = Path(..., ge=0)):
    items = await _load_list_field(activity_id, "follow_up_actions")
    _validate_item_index(items, item_index, "Follow-up action")
    del items[item_index]
    await _replace_list_field(activity_id, "follow_up_actions", items)
