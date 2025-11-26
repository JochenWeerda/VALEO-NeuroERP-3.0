"""
CRM Lead endpoints proxied through crm-core.
"""

from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ....core.config import settings
from ....integrations import crm_core_client
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Lead, LeadCreate, LeadUpdate

router = APIRouter()


def _adapt_lead(core_lead: crm_core_client.CRMCoreLead) -> dict:
    tenant_uuid = UUID(settings.DEFAULT_TENANT_ID)
    return {
        "id": core_lead.id,
        "tenant_id": tenant_uuid,
        "source": core_lead.source or "unknown",
        "status": core_lead.status,
        "priority": core_lead.priority,
        "estimated_value": core_lead.estimated_value,
        "company_name": core_lead.company_name,
        "contact_person": core_lead.contact_person,
        "email": core_lead.email,
        "phone": core_lead.phone,
        "assigned_to": core_lead.assigned_to,
        "created_at": core_lead.created_at,
        "updated_at": core_lead.updated_at,
        "converted_at": None,
        "converted_to_customer_id": None,
        "is_active": True,
        "deleted_at": None,
    }


def _map_create_payload(payload: LeadCreate) -> dict:
    body = payload.model_dump()
    return {
        "company_name": body["company_name"],
        "contact_person": body["contact_person"],
        "email": body["email"],
        "phone": body.get("phone"),
        "status": body["status"],
        "priority": body["priority"],
        "source": body["source"],
        "estimated_value": float(body["estimated_value"]) if body.get("estimated_value") is not None else None,
        "assigned_to": body.get("assigned_to"),
        "notes": None,
    }


def _map_update_payload(payload: LeadUpdate) -> dict:
    body = payload.model_dump(exclude_unset=True)
    if "estimated_value" in body and body["estimated_value"] is not None:
        body["estimated_value"] = float(body["estimated_value"])
    return body


@router.get("/", response_model=PaginatedResponse[Lead])
async def list_leads(
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None, description="Search in company/contact"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        leads, total = await crm_core_client.list_leads(status=status_filter, search=search, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list leads: {exc}") from exc
    items = [_adapt_lead(lead) for lead in leads]
    pages = (total + limit - 1) // limit if limit else 0
    return PaginatedResponse[Lead](
        items=[Lead.model_validate(item) for item in items],
        total=total,
        page=(skip // limit) + 1 if limit else 1,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    try:
        lead = await crm_core_client.get_lead(lead_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Lead not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve lead: {exc}") from exc
    return Lead.model_validate(_adapt_lead(lead))


@router.post("/", response_model=Lead, status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadCreate):
    try:
        created = await crm_core_client.create_lead(_map_create_payload(payload))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {exc}") from exc
    return Lead.model_validate(_adapt_lead(created))


@router.put("/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, payload: LeadUpdate):
    try:
        updated = await crm_core_client.update_lead(lead_id, _map_update_payload(payload))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Lead not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update lead: {exc}") from exc
    return Lead.model_validate(_adapt_lead(updated))


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: str):
    try:
        await crm_core_client.delete_lead(lead_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Lead not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete lead: {exc}") from exc
