"""Tenant-aware live-readiness summary for Superglue rollouts."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.services.superglue_admin_state import get_superglue_policy_override
from app.integrations.services.superglue_connector_registry import list_superglue_connector_bindings
from app.integrations.services.superglue_monitoring import build_superglue_monitoring_summary


def build_superglue_live_readiness(tenant_id: str) -> dict[str, Any]:
    bindings = list_superglue_connector_bindings(tenant_id)
    monitoring = build_superglue_monitoring_summary(tenant_id)
    policy_override = get_superglue_policy_override(tenant_id)
    connectors: list[dict[str, Any]] = []
    ready_count = 0
    blocked_count = 0
    execute_ready_count = 0

    for binding in bindings:
        required_credential_fields = [str(field) for field in binding.metadata.get("credential_fields", [])]
        configured_credentials = binding.system.credentials
        missing_credentials = [field for field in required_credential_fields if not configured_credentials.get(field)]
        uses_placeholder_url = _is_placeholder_url(binding.system.url)
        execute_capable = "execute" in binding.execution_modes
        blockers: list[str] = []
        if missing_credentials:
            blockers.append("missing_credentials")
        if uses_placeholder_url:
            blockers.append("placeholder_system_url")
        execution_enabled = bool(policy_override.get("execution_enabled", settings.SUPERGLUE_EXECUTION_ENABLED))
        if execute_capable and not execution_enabled:
            blockers.append("execute_mode_disabled")

        is_ready = not blockers
        if is_ready:
            ready_count += 1
            if execute_capable:
                execute_ready_count += 1
        else:
            blocked_count += 1

        connectors.append(
            {
                "connector_key": binding.connector_key,
                "display_name": binding.display_name,
                "tool_id": binding.tool_id,
                "system_id": binding.system.system_id,
                "system_url": binding.system.url,
                "execution_modes": list(binding.execution_modes),
                "required_credential_fields": required_credential_fields,
                "configured_credential_fields": sorted(configured_credentials.keys()),
                "missing_credential_fields": missing_credentials,
                "uses_placeholder_url": uses_placeholder_url,
                "ready": is_ready,
                "blockers": blockers,
            }
        )

    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "environment": settings.APP_ENV,
        "connector_count": len(connectors),
        "ready_connector_count": ready_count,
        "blocked_connector_count": blocked_count,
        "execute_ready_count": execute_ready_count,
        "policy": {
            "require_tenant_secrets": bool(policy_override.get("require_tenant_secrets", settings.SUPERGLUE_REQUIRE_TENANT_SECRETS)),
            "execution_enabled": bool(policy_override.get("execution_enabled", settings.SUPERGLUE_EXECUTION_ENABLED)),
            "alert_error_rate_pct": float(policy_override.get("alert_error_rate_pct", settings.SUPERGLUE_ALERT_ERROR_RATE_PCT)),
            "alert_open_quarantine_count": int(policy_override.get("alert_open_quarantine_count", settings.SUPERGLUE_ALERT_OPEN_QUARANTINE_COUNT)),
            "run_retention_days": int(policy_override.get("run_retention_days", settings.SUPERGLUE_RUN_RETENTION_DAYS)),
            "artifact_retention_days": int(policy_override.get("artifact_retention_days", settings.SUPERGLUE_ARTIFACT_RETENTION_DAYS)),
        },
        "monitoring": {
            "run_count": monitoring["run_count"],
            "average_latency_ms": monitoring["average_latency_ms"],
            "total_cost_cents": monitoring["total_cost_cents"],
            "quarantine_open_count": monitoring["quarantine"]["open_count"],
        },
        "connectors": connectors,
        "recommended_actions": _build_recommended_actions(connectors),
        "schema_version": 1,
    }


def _build_recommended_actions(connectors: list[dict[str, Any]]) -> list[str]:
    if not connectors:
        return ["Keine Superglue-Connectoren fuer diesen Tenant registriert."]

    actions: list[str] = []
    missing_credentials = sum(1 for connector in connectors if "missing_credentials" in connector["blockers"])
    placeholder_urls = sum(1 for connector in connectors if "placeholder_system_url" in connector["blockers"])
    execute_disabled = sum(1 for connector in connectors if "execute_mode_disabled" in connector["blockers"])

    if missing_credentials:
        actions.append(f"{missing_credentials} Connector(en) brauchen tenant-spezifische Live-Credentials.")
    if placeholder_urls:
        actions.append(f"{placeholder_urls} Connector(en) zeigen noch auf Platzhalter-URLs statt echte Zielsysteme.")
    if execute_disabled:
        actions.append(f"{execute_disabled} Execute-Connector(en) bleiben blockiert, solange SUPERGLUE_EXECUTION_ENABLED=false ist.")
    if not actions:
        actions.append("Alle Connectoren wirken fuer den aktuellen Tenant betriebsbereit.")
    return actions


def _is_placeholder_url(url: str) -> bool:
    normalized = str(url or "").strip().lower()
    return ".example.invalid" in normalized or ".example.test" in normalized or normalized.endswith(".invalid/api")
