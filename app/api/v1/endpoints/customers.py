"""CRM Customer endpoints backed by the crm-core service."""

from __future__ import annotations

from datetime import datetime
from math import ceil
from typing import Optional, Union
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, Response, status

from ....core.config import settings
from ....integrations.crm_core_client import (
    CRMCoreCustomer,
    create_customer as crm_create_customer,
    delete_customer as crm_delete_customer,
    get_customer as crm_get_customer,
    list_customers as crm_list_customers,
    update_customer as crm_update_customer,
)
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()


@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerCreate) -> Customer:
    """Create a new customer via crm-core."""
    payload = _map_create_payload(customer_data)
    try:
        created = await crm_create_customer(payload)
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network errors handled uniformly
        raise _to_http_exception(exc) from exc
    return _adapt_customer(created)


@router.get("/", response_model=PaginatedResponse[Customer])
async def list_customers(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search in display name"),
) -> PaginatedResponse[Customer]:
    """List customers from crm-core with pagination."""
    _ = tenant_id  # Multi-tenant routing handled in crm-core; keep parameter for compatibility.
    try:
        core_customers, total = await crm_list_customers(skip=skip, limit=limit, search=search)
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network errors handled uniformly
        raise _to_http_exception(exc) from exc

    items = [_adapt_customer(customer) for customer in core_customers]
    pages = ceil(total / limit) if total else 1
    return PaginatedResponse[Customer](
        items=items,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str) -> Customer:
    """Return a customer by ID."""
    try:
        customer = await crm_get_customer(customer_id)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return _adapt_customer(customer)


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_data: CustomerUpdate) -> Customer:
    """Update customer details by delegating to crm-core."""
    payload = _map_update_payload(customer_data)
    try:
        updated = await crm_update_customer(customer_id, payload)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return _adapt_customer(updated)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_customer(customer_id: str) -> Response:
    """Delete customer proxying the call to crm-core."""
    try:
        await crm_delete_customer(customer_id)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _adapt_customer(core_customer: CRMCoreCustomer) -> Customer:
    """Map crm-core payloads into the legacy Customer schema expected by the UI."""
    tenant_uuid = UUID(settings.DEFAULT_TENANT_ID)
    now = datetime.utcnow()
    customer_number = f"CRM-{core_customer.id[:8].upper()}"
    is_active = core_customer.status not in {"blacklisted", "former"}
    created_at = _parse_datetime(core_customer.created_at) or now
    updated_at = _parse_datetime(core_customer.updated_at) or now
    payload = {
        "id": core_customer.id,
        "tenant_id": tenant_uuid,
        "customer_number": customer_number,
        "company_name": core_customer.display_name,
        "name": core_customer.display_name,
        "contact_person": None,
        "email": core_customer.email,
        "phone": core_customer.phone,
        "address": None,
        "city": core_customer.region,
        "postal_code": None,
        "country": None,
        "industry": core_customer.industry,
        "website": None,
        "credit_limit": None,
        "payment_terms": 30,
        "tax_id": None,
        "is_active": is_active,
        "deleted_at": None,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    return Customer.model_validate(payload)


def _map_create_payload(customer_data: CustomerCreate) -> dict[str, Optional[str]]:
    """Convert monolith DTO into crm-core payload."""
    payload = {
        "display_name": customer_data.company_name,
        "email": customer_data.email,
        "phone": customer_data.phone,
        "industry": customer_data.industry,
        "region": customer_data.city or customer_data.country,
        "notes": _compose_notes(customer_data),
    }
    # Neue Sales-Felder hinzufügen (werden in domain_crm.crm_customers gespeichert)
    if hasattr(customer_data, 'price_group') and customer_data.price_group:
        payload["price_group"] = customer_data.price_group
    if hasattr(customer_data, 'tax_category') and customer_data.tax_category:
        payload["tax_category"] = customer_data.tax_category
    return payload


def _map_update_payload(customer_data: CustomerUpdate) -> dict[str, Optional[str]]:
    payload: dict[str, Optional[str]] = {}
    mapped_fields = {
        "company_name": "display_name",
        "email": "email",
        "phone": "phone",
        "industry": "industry",
        "city": "region",
        # Neue Sales-Felder (SALES-CRM-02)
        "price_group": "price_group",
        "tax_category": "tax_category",
    }
    data = customer_data.model_dump(exclude_unset=True)
    for source, target in mapped_fields.items():
        if source in data:
            payload[target] = data[source]
    if any(field in data for field in ("address", "contact_person", "website")):
        payload["notes"] = _compose_notes(customer_data)
    return payload


def _compose_notes(customer_data: Union[CustomerCreate, CustomerUpdate]) -> Optional[str]:
    """Summarise legacy-only fields into a notes blob for crm-core."""
    sections: list[str] = []
    if getattr(customer_data, "contact_person", None):
        sections.append(f"Contact: {customer_data.contact_person}")
    address_parts = [getattr(customer_data, attr, None) for attr in ("address", "city", "postal_code", "country")]
    address = ", ".join(filter(None, address_parts))
    if address:
        sections.append(f"Address: {address}")
    if getattr(customer_data, "website", None):
        sections.append(f"Website: {customer_data.website}")
    return "\n".join(sections) if sections else None


def _to_http_exception(error: httpx.HTTPStatusError) -> HTTPException:
    """Map downstream errors to FastAPI HTTPException."""
    detail = None
    try:
        payload = error.response.json()
        detail = payload.get("detail")
    except ValueError:
        detail = error.response.text or "crm-core request failed"
    return HTTPException(status_code=error.response.status_code, detail=detail or "crm-core request failed")


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
