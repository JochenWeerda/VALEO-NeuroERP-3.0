"""Build exportable onboarding packs for Superglue tenant activation."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.services.superglue_live_readiness import build_superglue_live_readiness
from app.integrations.services.superglue_secret_resolver import build_superglue_secret_keys


def build_superglue_onboarding_pack(tenant_id: str) -> dict[str, Any]:
    readiness = build_superglue_live_readiness(tenant_id)
    connectors: list[dict[str, Any]] = []

    for connector in readiness["connectors"]:
        connector_key = str(connector["connector_key"])
        secret_fields = ["SYSTEM_URL", *connector.get("missing_credential_fields", [])]
        connector_secret_keys = {
            field: build_superglue_secret_keys(tenant_id, field, connector_key=connector_key)
            for field in secret_fields
        }
        connectors.append(
            {
                "connector_key": connector_key,
                "display_name": connector["display_name"],
                "tool_id": connector["tool_id"],
                "ready": connector["ready"],
                "blockers": list(connector["blockers"]),
                "secret_keys": connector_secret_keys,
            }
        )

    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "environment": readiness["environment"],
        "vault_path_prefix": settings.HASHICORP_VAULT_PATH_PREFIX,
        "platform_secret_keys": {
            "AUTH_TOKEN": build_superglue_secret_keys(tenant_id, "AUTH_TOKEN"),
        },
        "policy_keys": {
            "SUPERGLUE_ALERT_ERROR_RATE_PCT": settings.SUPERGLUE_ALERT_ERROR_RATE_PCT,
            "SUPERGLUE_ALERT_OPEN_QUARANTINE_COUNT": settings.SUPERGLUE_ALERT_OPEN_QUARANTINE_COUNT,
            "SUPERGLUE_RUN_RETENTION_DAYS": settings.SUPERGLUE_RUN_RETENTION_DAYS,
            "SUPERGLUE_ARTIFACT_RETENTION_DAYS": settings.SUPERGLUE_ARTIFACT_RETENTION_DAYS,
        },
        "connector_count": readiness["connector_count"],
        "blocked_connector_count": readiness["blocked_connector_count"],
        "connectors": connectors,
        "recommended_actions": list(readiness["recommended_actions"]),
        "schema_version": 1,
    }
