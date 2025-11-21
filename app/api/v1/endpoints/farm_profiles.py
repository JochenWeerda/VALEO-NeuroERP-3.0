"""CRM Farm Profile endpoints proxied through crm-core."""

from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ....core.config import settings
from ....integrations import crm_core_client
from ..schemas.base import PaginatedResponse
from ..schemas.crm import FarmProfile, FarmProfileCreate, FarmProfileUpdate

router = APIRouter()


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


@router.get("/", response_model=PaginatedResponse[FarmProfile])
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


@router.get("/{profile_id}", response_model=FarmProfile)
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


@router.post("/", response_model=FarmProfile, status_code=status.HTTP_201_CREATED)
async def create_farm_profile(payload: FarmProfileCreate):
    try:
        body = _map_create_payload(payload)
        created = await crm_core_client.create_farm_profile(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create farm profile: {exc}") from exc
    return FarmProfile.model_validate(_adapt_farm_profile(created))


@router.put("/{profile_id}", response_model=FarmProfile)
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


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm_profile(profile_id: str):
    try:
        await crm_core_client.delete_farm_profile(profile_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Farm profile not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete farm profile: {exc}") from exc
