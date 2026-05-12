"""Tenant-isolated cache and rate-limit API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.tenant_rate_limits import (
    RateLimitRequest,
    get_tenant_isolation_registry,
)

router = APIRouter(prefix="/process/tenant-limits", tags=["process-kernel", "limits"])


class TenantRateLimitCheckIn(BaseModel):
    tenant_id: str = Field(min_length=1)
    user_id: str = Field(default="")
    endpoint: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    aktuelle_zaehlung: int = Field(default=0, ge=0)
    zeitfenster_sekunden: int = Field(default=60, ge=1)


@router.get("/overview", response_model=dict)
def get_tenant_limit_overview(
    tenant_id: str = Query(min_length=1),
    domain: str = "",
) -> dict[str, Any]:
    registry = get_tenant_isolation_registry()
    overview = registry.build_overview(tenant_id=tenant_id, domain=domain)
    return {
        "schema_version": 1,
        "overview": overview.as_dict(),
        "rate_limits": [policy.as_dict() for policy in registry.get_policies(domain)],
    }


@router.get("/cache-configs/{tenant_id}", response_model=dict)
def get_tenant_cache_config(tenant_id: str) -> dict[str, Any]:
    registry = get_tenant_isolation_registry()
    cache_config = registry.get_cache_config(tenant_id)
    return {
        "schema_version": 1,
        "cache_config": cache_config.as_dict(),
        "cache_namespace": f"tenant:{tenant_id}",
    }


@router.get("/rate-limits", response_model=dict)
def list_rate_limits(domain: str = "") -> dict[str, Any]:
    registry = get_tenant_isolation_registry()
    policies = registry.get_policies(domain)
    if domain and not policies:
        raise HTTPException(status_code=404, detail=f"No rate-limit policies found for domain {domain!r}")
    return {
        "schema_version": 1,
        "policy_count": len(policies),
        "domains": sorted({policy.domain for policy in policies}),
        "policies": [policy.as_dict() for policy in policies],
    }


@router.post("/rate-limits/check", response_model=dict)
def check_rate_limit(body: TenantRateLimitCheckIn) -> dict[str, Any]:
    registry = get_tenant_isolation_registry()
    request = RateLimitRequest(
        tenant_id=body.tenant_id,
        user_id=body.user_id,
        endpoint=body.endpoint,
        domain=body.domain,
        aktuelle_zaehlung=body.aktuelle_zaehlung,
        zeitfenster_sekunden=body.zeitfenster_sekunden,
    )
    result = registry.evaluate(request)
    return {
        "schema_version": 1,
        "result": result.as_dict(),
    }
