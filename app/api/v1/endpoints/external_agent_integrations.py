from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.external_agent_catalog import (
    build_external_agent_install_pack,
    build_external_agent_integration_catalog,
)
from app.integrations.adapters.superglue.tool_sync import (
    build_superglue_config_summary,
    build_superglue_health_status,
    build_superglue_sync_history,
    build_superglue_sync_status,
    build_superglue_tenant_tool_summary,
    build_superglue_tool_summary,
    refresh_superglue_sync_snapshot,
)
from app.integrations.services.superglue_execution_journal import build_execution_journal_summary
from app.integrations.services.superglue_domain_rollouts import (
    build_superglue_domain_rollout_summary,
    preview_superglue_domain_rollout,
)
from app.integrations.services.superglue_monitoring import (
    build_superglue_admin_overview,
    build_superglue_monitoring_summary,
)
from app.integrations.services.superglue_live_readiness import build_superglue_live_readiness
from app.integrations.services.superglue_onboarding_pack import build_superglue_onboarding_pack
from app.integrations.services.superglue_quarantine import build_quarantine_summary, resolve_quarantine_entry
from app.integrations.services.superglue_quarantine import retry_quarantine_entry
from app.integrations.services.superglue_tool_provisioning import (
    build_superglue_tool_lifecycle_summary,
    provision_superglue_pilot_tools,
    provision_superglue_tenant_connectors,
    run_superglue_pilot_smoke,
)

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


@router.get("/providers/superglue/tenants/{tenant_id}/tools", summary="Mapped Superglue Tool Catalog for a Tenant")
def get_superglue_tenant_tool_catalog(tenant_id: str) -> dict:
    return build_superglue_tenant_tool_summary(tenant_id)


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


@router.get("/providers/superglue/sync-history", summary="Superglue Sync History")
def get_superglue_sync_history(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    return build_superglue_sync_history(limit=limit)


@router.get("/providers/superglue/quarantine", summary="Superglue Quarantine")
def get_superglue_quarantine() -> dict:
    return build_quarantine_summary()


@router.post("/providers/superglue/quarantine/{entry_id}/resolve", summary="Resolve Superglue Quarantine Entry")
def resolve_superglue_quarantine(entry_id: str, resolved_by: str = Query(...), note: str | None = Query(default=None)) -> dict:
    try:
        return resolve_quarantine_entry(entry_id=entry_id, resolved_by=resolved_by, note=note)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Quarantine entry {entry_id!r} not found")


@router.get("/providers/superglue/execution-journal", summary="Superglue Execution Journal")
def get_superglue_execution_journal(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    return build_execution_journal_summary(limit=limit)


@router.get("/providers/superglue/admin-overview", summary="Superglue Admin Overview")
def get_superglue_admin_overview(tenant_id: str = Query(default="default")) -> dict:
    return build_superglue_admin_overview(tenant_id)


@router.get("/providers/superglue/monitoring", summary="Superglue Monitoring Summary")
def get_superglue_monitoring(tenant_id: str | None = Query(default=None)) -> dict:
    return build_superglue_monitoring_summary(tenant_id)


@router.get("/providers/superglue/live-readiness", summary="Superglue live readiness for tenant onboarding")
def get_superglue_live_readiness(tenant_id: str = Query(default="default")) -> dict:
    return build_superglue_live_readiness(tenant_id)


@router.get("/providers/superglue/onboarding-pack", summary="Superglue onboarding pack for tenant ops")
def get_superglue_onboarding_pack(tenant_id: str = Query(default="default")) -> dict:
    return build_superglue_onboarding_pack(tenant_id)


@router.post("/providers/superglue/pilot-tools/provision", summary="Provision canonical Superglue pilot tools")
def provision_superglue_pilots() -> dict:
    return provision_superglue_pilot_tools()


@router.post("/providers/superglue/pilot-tools/smoke-run", summary="Run canonical Superglue pilot smoke")
def run_superglue_pilot_tool_smoke() -> dict:
    return run_superglue_pilot_smoke()


@router.post("/providers/superglue/tenants/{tenant_id}/bootstrap", summary="Provision tenant-specific Superglue systems and tools")
def bootstrap_superglue_tenant_connectors(tenant_id: str) -> dict:
    return provision_superglue_tenant_connectors(tenant_id)


@router.get("/providers/superglue/tenants/{tenant_id}/tool-lifecycle", summary="Superglue tenant tool lifecycle summary")
def get_superglue_tenant_tool_lifecycle(tenant_id: str) -> dict:
    return build_superglue_tool_lifecycle_summary(tenant_id)


@router.post("/providers/superglue/quarantine/{entry_id}/retry", summary="Retry or dead-letter a Superglue quarantine entry")
def retry_superglue_quarantine(
    entry_id: str,
    retried_by: str = Query(...),
    note: str | None = Query(default=None),
    dead_letter: bool = Query(default=False),
) -> dict:
    try:
        return retry_quarantine_entry(entry_id=entry_id, retried_by=retried_by, note=note, dead_letter=dead_letter)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Quarantine entry {entry_id!r} not found")


@router.get("/providers/superglue/domain-rollouts", summary="Superglue domain rollout summary")
def get_superglue_domain_rollouts(tenant_id: str = Query(default="default")) -> dict:
    return build_superglue_domain_rollout_summary(tenant_id)


@router.post("/providers/superglue/domain-rollouts/{domain_key}/preview", summary="Superglue domain rollout preview")
def run_superglue_domain_rollout_preview(
    domain_key: str,
    tenant_id: str = Query(default="default"),
    body: dict | None = None,
) -> dict:
    try:
        return preview_superglue_domain_rollout(tenant_id=tenant_id, domain_key=domain_key, parameters=body or {})
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Superglue domain rollout {domain_key!r} not found")


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
