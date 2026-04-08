"""Wizard-oriented control-center helpers for Superglue tenant onboarding."""

from __future__ import annotations

from typing import Any

from app.integrations.services.superglue_admin_state import (
    get_superglue_admin_state,
    update_superglue_connector_override,
    update_superglue_policy_override,
    update_superglue_wizard_state,
)
from app.integrations.services.superglue_live_readiness import build_superglue_live_readiness
from app.integrations.services.superglue_onboarding_pack import build_superglue_onboarding_pack


def build_superglue_onboarding_wizard(tenant_id: str) -> dict[str, Any]:
    readiness = build_superglue_live_readiness(tenant_id)
    onboarding_pack = build_superglue_onboarding_pack(tenant_id)
    admin_state = get_superglue_admin_state(tenant_id)
    wizard_state = admin_state["wizard"]
    completed_steps = set(wizard_state.get("completed_steps") or [])

    connectors_with_missing_credentials = [
        connector["connector_key"]
        for connector in readiness["connectors"]
        if connector.get("missing_credential_fields")
    ]
    connectors_with_placeholder_urls = [
        connector["connector_key"]
        for connector in readiness["connectors"]
        if connector.get("uses_placeholder_url")
    ]

    steps = [
        {
            "step_key": "credentials",
            "title": "Live-Credentials vorbereiten",
            "status": "complete" if not connectors_with_missing_credentials else ("done" if "credentials" in completed_steps else "pending"),
            "details": connectors_with_missing_credentials,
        },
        {
            "step_key": "systems",
            "title": "Zielsystem-URLs einrichten",
            "status": "complete" if not connectors_with_placeholder_urls else ("done" if "systems" in completed_steps else "pending"),
            "details": connectors_with_placeholder_urls,
        },
        {
            "step_key": "policy",
            "title": "Ops-Policy und Retention setzen",
            "status": "done" if "policy" in completed_steps else "pending",
            "details": onboarding_pack["policy_keys"],
        },
        {
            "step_key": "bootstrap",
            "title": "Tenant-Bootstrap und Rollout",
            "status": "done" if "bootstrap" in completed_steps else "pending",
            "details": {
                "connector_count": readiness["connector_count"],
                "ready_connector_count": readiness["ready_connector_count"],
                "blocked_connector_count": readiness["blocked_connector_count"],
            },
        },
    ]

    return {
        "tenant_id": tenant_id,
        "current_step": wizard_state.get("current_step", "credentials"),
        "completed_steps": list(wizard_state.get("completed_steps") or []),
        "recommended_actions": readiness["recommended_actions"],
        "steps": steps,
        "schema_version": 1,
    }


def apply_superglue_onboarding_wizard(
    tenant_id: str,
    *,
    connector_key: str | None = None,
    system_url: str | None = None,
    execution_enabled: bool | None = None,
    require_tenant_secrets: bool | None = None,
    alert_error_rate_pct: float | None = None,
    alert_open_quarantine_count: int | None = None,
    run_retention_days: int | None = None,
    artifact_retention_days: int | None = None,
    completed_step: str | None = None,
    next_step: str | None = None,
) -> dict[str, Any]:
    mutation_results: dict[str, Any] = {}
    if connector_key and system_url:
        mutation_results["connector"] = update_superglue_connector_override(
            tenant_id,
            connector_key,
            system_url=system_url,
        )
    if any(
        value is not None
        for value in [
            execution_enabled,
            require_tenant_secrets,
            alert_error_rate_pct,
            alert_open_quarantine_count,
            run_retention_days,
            artifact_retention_days,
        ]
    ):
        mutation_results["policy"] = update_superglue_policy_override(
            tenant_id,
            execution_enabled=execution_enabled,
            require_tenant_secrets=require_tenant_secrets,
            alert_error_rate_pct=alert_error_rate_pct,
            alert_open_quarantine_count=alert_open_quarantine_count,
            run_retention_days=run_retention_days,
            artifact_retention_days=artifact_retention_days,
        )
    mutation_results["wizard"] = update_superglue_wizard_state(
        tenant_id,
        current_step=next_step,
        completed_step=completed_step,
    )
    mutation_results["wizard_summary"] = build_superglue_onboarding_wizard(tenant_id)
    mutation_results["schema_version"] = 1
    return mutation_results
