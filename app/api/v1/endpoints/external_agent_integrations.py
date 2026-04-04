from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.external_agent_catalog import (
    build_external_agent_install_pack,
    build_external_agent_integration_catalog,
)
from app.integrations.adapters.superglue.tool_sync import (
    build_superglue_config_summary,
    build_superglue_health_status,
    build_superglue_sync_status,
    build_superglue_tool_summary,
    refresh_superglue_sync_snapshot,
)
from app.integrations.services.superglue_quarantine import build_quarantine_summary

router = APIRouter(prefix="/agent/integrations", tags=["agents", "integrations", "openapi", "mcp"])


@router.get("", summary="External Agent Integration Catalog")
def get_external_agent_integration_catalog(
    domain: str | None = Query(default=None, description="Optional domain filter"),
    provider_key: str | None = Query(default=None, description="Optional provider filter"),
) -> dict:
    manifest = build_external_agent_integration_catalog(domain=domain, provider_key=provider_key)
    return manifest.model_dump()


@router.get("/providers", summary="External Agent Provider Catalog")
def get_external_agent_provider_catalog(
    provider_key: str | None = Query(default=None, description="Optional provider filter"),
) -> dict:
    manifest = build_external_agent_integration_catalog(provider_key=provider_key)
    return {
        "schema_version": manifest.schema_version,
        "generated_at": manifest.generated_at,
        "provider_count": manifest.provider_count,
        "providers": [provider.model_dump() for provider in manifest.providers],
    }


@router.get("/providers/{provider_key}", summary="Single External Agent Provider")
def get_external_agent_provider(provider_key: str) -> dict:
    manifest = build_external_agent_integration_catalog(provider_key=provider_key)
    if not manifest.providers:
        raise HTTPException(status_code=404, detail=f"Provider {provider_key!r} not found")
    return manifest.providers[0].model_dump()


@router.get("/providers/superglue/tools", summary="Mapped Superglue Tool Catalog")
def get_superglue_tool_catalog() -> dict:
    return build_superglue_tool_summary()


@router.get("/providers/superglue/sync-status", summary="Superglue Sync Status")
def get_superglue_sync_status() -> dict:
    return build_superglue_sync_status().model_dump()


@router.get("/providers/superglue/health", summary="Superglue Health")
def get_superglue_health() -> dict:
    return build_superglue_health_status().model_dump()


@router.get("/providers/superglue/config-summary", summary="Superglue Config Summary")
def get_superglue_config_summary() -> dict:
    return build_superglue_config_summary()


@router.post("/providers/superglue/sync-status/refresh", summary="Refresh Superglue Sync Snapshot")
def refresh_superglue_sync() -> dict:
    return refresh_superglue_sync_snapshot()


@router.get("/providers/superglue/quarantine", summary="Superglue Quarantine")
def get_superglue_quarantine() -> dict:
    return build_quarantine_summary()


@router.get("/use-cases", summary="External Agent Use Cases")
def get_external_agent_use_cases(
    domain: str | None = Query(default=None, description="Optional domain filter"),
    provider_key: str | None = Query(default=None, description="Optional provider filter"),
) -> dict:
    manifest = build_external_agent_integration_catalog(domain=domain, provider_key=provider_key)
    return {
        "schema_version": manifest.schema_version,
        "generated_at": manifest.generated_at,
        "use_case_count": manifest.use_case_count,
        "domain_count": manifest.domain_count,
        "domains": sorted({item.domain for item in manifest.use_cases}),
        "use_cases": [use_case.model_dump() for use_case in manifest.use_cases],
    }


@router.get("/use-cases/{use_case_id}", summary="Single External Agent Use Case")
def get_external_agent_use_case(use_case_id: str) -> dict:
    manifest = build_external_agent_integration_catalog(use_case_id=use_case_id)
    if not manifest.use_cases:
        raise HTTPException(status_code=404, detail=f"Use case {use_case_id!r} not found")
    return manifest.use_cases[0].model_dump()


@router.get("/use-cases/{use_case_id}/install-pack", summary="Install Pack for External Agent Use Case")
def get_external_agent_install_pack(use_case_id: str) -> dict:
    try:
        pack = build_external_agent_install_pack(use_case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Use case {use_case_id!r} not found")
    return pack.model_dump()
