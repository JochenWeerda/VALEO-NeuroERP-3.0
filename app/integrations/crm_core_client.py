"""Async HTTP client helpers for talking to the crm-core service."""

from __future__ import annotations

from typing import Any, Tuple

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings


class CRMCoreCustomer(BaseModel):
    """Shape of a customer returned by crm-core."""

    id: str
    display_name: str
    type: str
    status: str
    email: str | None = None
    phone: str | None = None
    industry: str | None = None
    region: str | None = None
    lead_score: float | None = Field(default=None, ge=0, le=1)
    churn_score: float | None = Field(default=None, ge=0, le=1)
    notes: str | None = None
    tenant_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CRMCoreListResponse(BaseModel):
    items: list[CRMCoreCustomer]
    total: int


class CRMCoreContact(BaseModel):
    id: str
    customer_id: str
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    job_title: str | None = None
    department: str | None = None
    customer_name: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CRMCoreContactListResponse(BaseModel):
    items: list[CRMCoreContact]
    total: int


class CRMCoreLead(BaseModel):
    id: str
    tenant_id: str
    company_name: str
    contact_person: str
    email: str | None = None
    phone: str | None = None
    status: str
    priority: str
    source: str | None = None
    estimated_value: float | None = None
    assigned_to: str | None = None
    notes: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CRMCoreLeadListResponse(BaseModel):
    items: list[CRMCoreLead]
    total: int


class CRMCoreActivity(BaseModel):
    id: str
    tenant_id: str
    type: str
    title: str
    status: str
    assigned_to: str | None = None
    scheduled_at: str | None = None
    description: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    contact_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CRMCoreActivityListResponse(BaseModel):
    items: list[CRMCoreActivity]
    total: int


class CRMCoreFarmProfile(BaseModel):
    id: str
    tenant_id: str
    farm_name: str
    owner: str
    total_area: float
    crops: list[dict] | None = None
    livestock: list[dict] | None = None
    location: dict | None = None
    certifications: list[str] | None = None
    notes: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CRMCoreFarmProfileListResponse(BaseModel):
    items: list[CRMCoreFarmProfile]
    total: int


async def list_customers(
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
) -> Tuple[list[CRMCoreCustomer], int]:
    params: dict[str, Any] = {"skip": skip, "limit": limit}
    if search:
        params["search"] = search
    payload = await _request("GET", "/api/v1/customers", params=params)
    response = CRMCoreListResponse.model_validate(payload)
    return response.items, response.total


async def get_customer(customer_id: str) -> CRMCoreCustomer:
    payload = await _request("GET", f"/api/v1/customers/{customer_id}")
    return CRMCoreCustomer.model_validate(payload)


async def create_customer(body: dict[str, Any]) -> CRMCoreCustomer:
    payload = await _request("POST", "/api/v1/customers", json=body)
    return CRMCoreCustomer.model_validate(payload)


async def update_customer(customer_id: str, body: dict[str, Any]) -> CRMCoreCustomer:
    payload = await _request("PATCH", f"/api/v1/customers/{customer_id}", json=body)
    return CRMCoreCustomer.model_validate(payload)


async def delete_customer(customer_id: str) -> None:
    await _request("DELETE", f"/api/v1/customers/{customer_id}")


async def list_contacts(
    customer_id: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[CRMCoreContact], int]:
    params: dict[str, Any] = {"skip": skip, "limit": limit}
    if customer_id:
        params["customer_id"] = customer_id
    if search:
        params["search"] = search
    payload = await _request("GET", "/api/v1/contacts", params=params)
    response = CRMCoreContactListResponse.model_validate(payload)
    return response.items, response.total


async def get_contact(contact_id: str) -> CRMCoreContact:
    payload = await _request("GET", f"/api/v1/contacts/{contact_id}")
    return CRMCoreContact.model_validate(payload)


async def create_contact(body: dict[str, Any]) -> CRMCoreContact:
    payload = await _request("POST", "/api/v1/contacts", json=body)
    return CRMCoreContact.model_validate(payload)


async def update_contact(contact_id: str, body: dict[str, Any]) -> CRMCoreContact:
    payload = await _request("PATCH", f"/api/v1/contacts/{contact_id}", json=body)
    return CRMCoreContact.model_validate(payload)


async def delete_contact(contact_id: str) -> None:
    await _request("DELETE", f"/api/v1/contacts/{contact_id}")


async def list_leads(
    status: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[CRMCoreLead], int]:
    params: dict[str, Any] = {"skip": skip, "limit": limit}
    if status:
        params["status"] = status
    if search:
        params["search"] = search
    payload = await _request("GET", "/api/v1/leads", params=params)
    response = CRMCoreLeadListResponse.model_validate(payload)
    return response.items, response.total


async def get_lead(lead_id: str) -> CRMCoreLead:
    payload = await _request("GET", f"/api/v1/leads/{lead_id}")
    return CRMCoreLead.model_validate(payload)


async def create_lead(body: dict[str, Any]) -> CRMCoreLead:
    payload = await _request("POST", "/api/v1/leads", json=body)
    return CRMCoreLead.model_validate(payload)


async def update_lead(lead_id: str, body: dict[str, Any]) -> CRMCoreLead:
    payload = await _request("PATCH", f"/api/v1/leads/{lead_id}", json=body)
    return CRMCoreLead.model_validate(payload)


async def delete_lead(lead_id: str) -> None:
    await _request("DELETE", f"/api/v1/leads/{lead_id}")


async def list_activities(
    activity_type: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[CRMCoreActivity], int]:
    params: dict[str, Any] = {"skip": skip, "limit": limit}
    if activity_type:
        params["type"] = activity_type
    if status:
        params["status"] = status
    payload = await _request("GET", "/api/v1/activities", params=params)
    response = CRMCoreActivityListResponse.model_validate(payload)
    return response.items, response.total


async def get_activity(activity_id: str) -> CRMCoreActivity:
    payload = await _request("GET", f"/api/v1/activities/{activity_id}")
    return CRMCoreActivity.model_validate(payload)


async def create_activity(body: dict[str, Any]) -> CRMCoreActivity:
    payload = await _request("POST", "/api/v1/activities", json=body)
    return CRMCoreActivity.model_validate(payload)


async def update_activity(activity_id: str, body: dict[str, Any]) -> CRMCoreActivity:
    payload = await _request("PATCH", f"/api/v1/activities/{activity_id}", json=body)
    return CRMCoreActivity.model_validate(payload)


async def delete_activity(activity_id: str) -> None:
    await _request("DELETE", f"/api/v1/activities/{activity_id}")


async def list_farm_profiles(
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[CRMCoreFarmProfile], int]:
    params: dict[str, Any] = {"skip": skip, "limit": limit}
    if search:
        params["search"] = search
    payload = await _request("GET", "/api/v1/farm-profiles", params=params)
    response = CRMCoreFarmProfileListResponse.model_validate(payload)
    return response.items, response.total


async def get_farm_profile(profile_id: str) -> CRMCoreFarmProfile:
    payload = await _request("GET", f"/api/v1/farm-profiles/{profile_id}")
    return CRMCoreFarmProfile.model_validate(payload)


async def create_farm_profile(body: dict[str, Any]) -> CRMCoreFarmProfile:
    payload = await _request("POST", "/api/v1/farm-profiles", json=body)
    return CRMCoreFarmProfile.model_validate(payload)


async def update_farm_profile(profile_id: str, body: dict[str, Any]) -> CRMCoreFarmProfile:
    payload = await _request("PATCH", f"/api/v1/farm-profiles/{profile_id}", json=body)
    return CRMCoreFarmProfile.model_validate(payload)


async def delete_farm_profile(profile_id: str) -> None:
    await _request("DELETE", f"/api/v1/farm-profiles/{profile_id}")


# CRM Sales client functions
async def list_opportunities(
    tenant_id: str | None = None,
    status: str | None = None,
    assigned_to: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[dict], int]:
    """List opportunities from crm-sales service."""
    params: dict[str, Any] = {"skip": skip, "limit": limit}
    if tenant_id:
        params["tenant_id"] = tenant_id
    if status:
        params["status"] = status
    if assigned_to:
        params["assigned_to"] = assigned_to
    payload = await _request_crm_sales("GET", "/api/v1/opportunities", params=params)
    return payload.get("items", []), payload.get("total", 0)


async def get_opportunity(opportunity_id: str) -> dict:
    """Get opportunity by ID from crm-sales service."""
    return await _request_crm_sales("GET", f"/api/v1/opportunities/{opportunity_id}")


async def create_opportunity(data: dict[str, Any]) -> dict:
    """Create opportunity via crm-sales service."""
    return await _request_crm_sales("POST", "/api/v1/opportunities", json=data)


async def update_opportunity(opportunity_id: str, data: dict[str, Any]) -> dict:
    """Update opportunity via crm-sales service."""
    return await _request_crm_sales("PUT", f"/api/v1/opportunities/{opportunity_id}", json=data)


async def delete_opportunity(opportunity_id: str) -> None:
    """Delete opportunity via crm-sales service."""
    await _request_crm_sales("DELETE", f"/api/v1/opportunities/{opportunity_id}")


# CRM Service client functions
async def list_cases(
    tenant_id: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: str | None = None,
    customer_id: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[dict], int]:
    """List cases from crm-service."""
    params: dict[str, Any] = {"skip": skip, "limit": limit}
    if tenant_id:
        params["tenant_id"] = tenant_id
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if assigned_to:
        params["assigned_to"] = assigned_to
    if customer_id:
        params["customer_id"] = customer_id
    payload = await _request_crm_service("GET", "/api/v1/cases", params=params)
    return payload.get("items", []), payload.get("total", 0)


async def get_case(case_id: str) -> dict:
    """Get case by ID from crm-service."""
    return await _request_crm_service("GET", f"/api/v1/cases/{case_id}")


async def create_case(data: dict[str, Any]) -> dict:
    """Create case via crm-service."""
    return await _request_crm_service("POST", "/api/v1/cases", json=data)


async def update_case(case_id: str, data: dict[str, Any]) -> dict:
    """Update case via crm-service."""
    return await _request_crm_service("PUT", f"/api/v1/cases/{case_id}", json=data)


async def delete_case(case_id: str) -> None:
    """Delete case via crm-service."""
    await _request_crm_service("DELETE", f"/api/v1/cases/{case_id}")


async def escalate_case(case_id: str, reason: str, escalated_by: str) -> dict:
    """Escalate case via crm-service."""
    params = {"reason": reason, "escalated_by": escalated_by}
    return await _request_crm_service("POST", f"/api/v1/cases/{case_id}/escalate", params=params)


async def _request_crm_sales(method: str, path: str, **kwargs: Any) -> Any:
    """Make request to crm-sales service."""
    timeout = getattr(settings, 'CRM_SALES_HTTP_TIMEOUT_SECONDS', 5)
    base_url = getattr(settings, 'CRM_SALES_BASE_URL', 'http://localhost:5700')
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None


async def _request_crm_service(method: str, path: str, **kwargs: Any) -> Any:
    """Make request to crm-service."""
    timeout = getattr(settings, 'CRM_SERVICE_HTTP_TIMEOUT_SECONDS', 5)
    base_url = getattr(settings, 'CRM_SERVICE_BASE_URL', 'http://localhost:5800')
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None


async def _request(method: str, path: str, **kwargs: Any) -> Any:
    timeout = settings.CRM_CORE_HTTP_TIMEOUT_SECONDS
    async with httpx.AsyncClient(
        base_url=settings.CRM_CORE_BASE_URL,
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None
