"""
CRM Contact management endpoints proxied via crm-core
"""

from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ....integrations import crm_core_client
from ..schemas.crm import ContactCreate, ContactUpdate

router = APIRouter()


def _adapt_contact(core_contact: crm_core_client.CRMCoreContact) -> Dict[str, Any]:
    full_name = " ".join(filter(None, [core_contact.first_name, core_contact.last_name])).strip()
    if not full_name:
        full_name = core_contact.email or "Kontakt"
    created_at = core_contact.created_at or datetime.utcnow().isoformat()
    updated_at = core_contact.updated_at or created_at
    notes_parts = [value for value in [core_contact.job_title, core_contact.department] if value]
    notes = " - ".join(notes_parts) if notes_parts else None
    return {
        "id": core_contact.id,
        "name": full_name,
        "company": core_contact.customer_name or "",
        "email": core_contact.email or "",
        "phone": core_contact.phone or "",
        "type": "customer",
        "address": None,
        "notes": notes,
        "createdAt": created_at,
        "updatedAt": updated_at,
    }


def _map_create_payload(payload: ContactCreate) -> Dict[str, Any]:
    body = payload.model_dump()
    return {
        "customer_id": str(body["customer_id"]),
        "first_name": body["first_name"],
        "last_name": body["last_name"],
        "email": body.get("email"),
        "phone": body.get("phone"),
        "job_title": body.get("position"),
        "department": body.get("department"),
    }


def _map_update_payload(payload: ContactUpdate) -> Dict[str, Any]:
    body = payload.model_dump(exclude_unset=True)
    mapped: Dict[str, Any] = {}
    if "first_name" in body:
        mapped["first_name"] = body["first_name"]
    if "last_name" in body:
        mapped["last_name"] = body["last_name"]
    if "email" in body:
        mapped["email"] = body["email"]
    if "phone" in body:
        mapped["phone"] = body["phone"]
    if "position" in body:
        mapped["job_title"] = body["position"]
    if "department" in body:
        mapped["department"] = body["department"]
    return mapped


@router.get("/")
async def list_contacts(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    search: Optional[str] = Query(None, description="Client-side search term"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
):
    try:
        core_contacts, total = await crm_core_client.list_contacts(
            customer_id=customer_id,
            search=search,
            skip=skip,
            limit=limit,
        )
        data = [_adapt_contact(contact) for contact in core_contacts]
        if search:
            needle = search.lower()
            data = [
                contact
                for contact in data
                if needle in contact["name"].lower()
                or needle in contact["company"].lower()
                or needle in contact["email"].lower()
            ]
            total = len(data)
        return {"data": data, "total": total}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list contacts: {exc}") from exc


@router.get("/{contact_id}")
async def get_contact(contact_id: str):
    try:
        contact = await crm_core_client.get_contact(contact_id)
    except httpx.HTTPStatusError as exc:  # type: ignore[name-defined]
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Contact not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve contact: {exc}") from exc
    return {"data": _adapt_contact(contact)}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_contact(contact_data: ContactCreate):
    try:
        payload = _map_create_payload(contact_data)
        created = await crm_core_client.create_contact(payload)
        return {"data": _adapt_contact(created)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create contact: {exc}") from exc


@router.put("/{contact_id}")
async def update_contact(contact_id: str, contact_data: ContactUpdate):
    try:
        payload = _map_update_payload(contact_data)
        updated = await crm_core_client.update_contact(contact_id, payload)
        return {"data": _adapt_contact(updated)}
    except httpx.HTTPStatusError as exc:  # type: ignore[name-defined]
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Contact not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update contact: {exc}") from exc


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: str):
    try:
        await crm_core_client.delete_contact(contact_id)
    except httpx.HTTPStatusError as exc:  # type: ignore[name-defined]
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Contact not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete contact: {exc}") from exc
