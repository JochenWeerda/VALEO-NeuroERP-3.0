"""CRM Farm Profile endpoints proxied through crm-core."""

from typing import Any
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from ....core.config import settings
from ....integrations import crm_core_client
from ..schemas.base import PaginatedResponse
from ..schemas.crm import FarmProfile, FarmProfileCreate, FarmProfileUpdate

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter()


class _CertificationItem(BaseModel):
    value: str = Field(..., min_length=1, max_length=200)


def _adapt_farm_profile(core_profile: crm_core_client.CRMCoreFarmProfile) -> dict:
    tenant_uuid = UUID(settings.DEFAULT_TENANT_ID)
    return {
        "id": core_profile.id,
        "tenant_id": tenant_uuid,
        "farm_name": core_profile.farm_name,
        "owner": core_profile.owner,
        "total_area": core_profile.total_area,
        "crops": core_profile.crops,
        "livestock": core_profile.livestock,
        "location": core_profile.location,
        "certifications": core_profile.certifications,
        "notes": core_profile.notes,
        "customer_id": core_profile.customer_id,
        "customer_name": core_profile.customer_name,
        "created_at": core_profile.created_at,
        "updated_at": core_profile.updated_at,
        "is_active": True,
        "deleted_at": None,
    }


def _map_create_payload(payload: FarmProfileCreate) -> dict:
    body = payload.model_dump()
    return {
        "farm_name": body["farm_name"],
        "owner": body["owner"],
        "total_area": body["total_area"],
        "crops": body.get("crops"),
        "livestock": body.get("livestock"),
        "location": body.get("location"),
        "certifications": body.get("certifications"),
        "notes": body.get("notes"),
        "customer_id": body.get("customer_id"),
    }


def _map_update_payload(payload: FarmProfileUpdate) -> dict:
    return payload.model_dump(exclude_unset=True)


def _raise_core_error(exc: Exception, not_found_detail: str, default_detail: str) -> None:
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail=not_found_detail) from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    raise HTTPException(status_code=500, detail=default_detail) from exc


async def _get_profile_or_404(profile_id: str) -> crm_core_client.CRMCoreFarmProfile:
    try:
        return await crm_core_client.get_farm_profile(profile_id)
    except Exception as exc:
        _raise_core_error(exc, "Farm profile not found", f"Failed to retrieve farm profile: {exc}")
    raise HTTPException(status_code=500, detail="Failed to retrieve farm profile")


async def _replace_list_field(profile_id: str, field_name: str, items: list[Any]) -> list[Any]:
    try:
        updated = await crm_core_client.update_farm_profile(profile_id, {field_name: items})
    except Exception as exc:
        _raise_core_error(exc, "Farm profile not found", f"Failed to update {field_name}: {exc}")
    value = getattr(updated, field_name, None)
    return list(value or [])


async def _load_list_field(profile_id: str, field_name: str) -> list[Any]:
    profile = await _get_profile_or_404(profile_id)
    value = getattr(profile, field_name, None)
    return list(value or [])


def _validate_item_index(items: list[Any], item_index: int, field_label: str) -> None:
    if item_index < 0 or item_index >= len(items):
        raise HTTPException(status_code=404, detail=f"{field_label} item not found")


@router.get("/", response_model=PaginatedResponse[FarmProfile], summary="Farm profiles auflisten")
async def list_farm_profiles(
    search: str | None = Query(None, description="Search in farm name or owner"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        profiles, total = await crm_core_client.list_farm_profiles(
            search=search, skip=skip, limit=limit
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list farm profiles: {exc}") from exc
    items = [_adapt_farm_profile(profile) for profile in profiles]
    pages = (total + limit - 1) // limit if limit else 0
    return PaginatedResponse[FarmProfile](
        items=[FarmProfile.model_validate(item) for item in items],
        total=total,
        page=(skip // limit) + 1 if limit else 1,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{profile_id}", response_model=FarmProfile, summary="Farm profile abrufen")
async def get_farm_profile(profile_id: str):
    try:
        profile = await crm_core_client.get_farm_profile(profile_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Farm profile not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve farm profile: {exc}") from exc
    return FarmProfile.model_validate(_adapt_farm_profile(profile))


@router.post("/", response_model=FarmProfile, status_code=status.HTTP_201_CREATED, summary="Farm profile anlegen")
async def create_farm_profile(payload: FarmProfileCreate):
    try:
        body = _map_create_payload(payload)
        created = await crm_core_client.create_farm_profile(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create farm profile: {exc}") from exc
    return FarmProfile.model_validate(_adapt_farm_profile(created))


@router.put("/{profile_id}", response_model=FarmProfile, summary="Farm profile aktualisieren")
async def update_farm_profile(profile_id: str, payload: FarmProfileUpdate):
    try:
        body = _map_update_payload(payload)
        updated = await crm_core_client.update_farm_profile(profile_id, body)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Farm profile not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update farm profile: {exc}") from exc
    return FarmProfile.model_validate(_adapt_farm_profile(updated))


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Farm profile löschen",
    response_model=None
)
async def delete_farm_profile(profile_id: str):
    try:
        await crm_core_client.delete_farm_profile(profile_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Farm profile not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete farm profile: {exc}") from exc


@router.get("/{profile_id}/crops", response_model=list[CompatFlexOut], summary="Farm profile crops auflisten")
async def list_farm_profile_crops(profile_id: str):
    return await _load_list_field(profile_id, "crops")


@router.post("/{profile_id}/crops", response_model=CompatFlexOut, status_code=status.HTTP_201_CREATED, summary="Farm profile crop anlegen")
async def create_farm_profile_crop(profile_id: str, payload: dict[str, Any]):
    items = await _load_list_field(profile_id, "crops")
    items.append(payload)
    updated = await _replace_list_field(profile_id, "crops", items)
    return dict(updated[-1])


@router.put("/{profile_id}/crops/{item_index}", response_model=CompatFlexOut, summary="Farm profile crop replace")
async def replace_farm_profile_crop(
    profile_id: str,
    item_index: int = Path(..., ge=0),
    payload: dict[str, Any] = ...,
):
    items = await _load_list_field(profile_id, "crops")
    _validate_item_index(items, item_index, "Crop")
    items[item_index] = payload
    updated = await _replace_list_field(profile_id, "crops", items)
    return dict(updated[item_index])


@router.delete("/{profile_id}/crops/{item_index}", status_code=status.HTTP_204_NO_CONTENT, summary="Farm profile crop löschen",
    response_model=None
)
async def delete_farm_profile_crop(profile_id: str, item_index: int = Path(..., ge=0)):
    items = await _load_list_field(profile_id, "crops")
    _validate_item_index(items, item_index, "Crop")
    del items[item_index]
    await _replace_list_field(profile_id, "crops", items)


@router.get("/{profile_id}/livestock", response_model=list[CompatFlexOut], summary="Farm profile livestock auflisten")
async def list_farm_profile_livestock(profile_id: str):
    return await _load_list_field(profile_id, "livestock")


@router.post("/{profile_id}/livestock", response_model=CompatFlexOut, status_code=status.HTTP_201_CREATED, summary="Farm profile livestock anlegen")
async def create_farm_profile_livestock(profile_id: str, payload: dict[str, Any]):
    items = await _load_list_field(profile_id, "livestock")
    items.append(payload)
    updated = await _replace_list_field(profile_id, "livestock", items)
    return dict(updated[-1])


@router.put("/{profile_id}/livestock/{item_index}", response_model=CompatFlexOut, summary="Farm profile livestock replace")
async def replace_farm_profile_livestock(
    profile_id: str,
    item_index: int = Path(..., ge=0),
    payload: dict[str, Any] = ...,
):
    items = await _load_list_field(profile_id, "livestock")
    _validate_item_index(items, item_index, "Livestock")
    items[item_index] = payload
    updated = await _replace_list_field(profile_id, "livestock", items)
    return dict(updated[item_index])


@router.delete("/{profile_id}/livestock/{item_index}", status_code=status.HTTP_204_NO_CONTENT, summary="Farm profile livestock löschen",
    response_model=None
)
async def delete_farm_profile_livestock(profile_id: str, item_index: int = Path(..., ge=0)):
    items = await _load_list_field(profile_id, "livestock")
    _validate_item_index(items, item_index, "Livestock")
    del items[item_index]
    await _replace_list_field(profile_id, "livestock", items)


@router.get("/{profile_id}/certifications", response_model=list[str], summary="Farm profile certifications auflisten")
async def list_farm_profile_certifications(profile_id: str):
    raw_items = await _load_list_field(profile_id, "certifications")
    return [str(item) for item in raw_items]


@router.post(
    "/{profile_id}/certifications",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Farm profile certification anlegen",
)
async def create_farm_profile_certification(profile_id: str, payload: _CertificationItem):
    items = [str(item) for item in await _load_list_field(profile_id, "certifications")]
    items.append(payload.value)
    updated = await _replace_list_field(profile_id, "certifications", items)
    return str(updated[-1])


@router.put("/{profile_id}/certifications/{item_index}", response_model=str, summary="Farm profile certification replace")
async def replace_farm_profile_certification(
    profile_id: str,
    payload: _CertificationItem,
    item_index: int = Path(..., ge=0),
):
    items = [str(item) for item in await _load_list_field(profile_id, "certifications")]
    _validate_item_index(items, item_index, "Certification")
    items[item_index] = payload.value
    updated = await _replace_list_field(profile_id, "certifications", items)
    return str(updated[item_index])


@router.delete("/{profile_id}/certifications/{item_index}", status_code=status.HTTP_204_NO_CONTENT, summary="Farm profile certification löschen",
    response_model=None
)
async def delete_farm_profile_certification(profile_id: str, item_index: int = Path(..., ge=0)):
    items = [str(item) for item in await _load_list_field(profile_id, "certifications")]
    _validate_item_index(items, item_index, "Certification")
    del items[item_index]
    await _replace_list_field(profile_id, "certifications", items)
