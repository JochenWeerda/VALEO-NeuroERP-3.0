"""Tenant-aware secret resolution for Superglue credentials."""

from __future__ import annotations

from app.core.config import settings
from app.services.secrets_vault import get_first_secret


def build_superglue_secret_keys(tenant_id: str, key_name: str = "AUTH_TOKEN", connector_key: str | None = None) -> list[str]:
    tenant = tenant_id.strip()
    normalized = tenant.replace("-", "_").upper()
    key = key_name.strip().upper()
    connector = str(connector_key or "").strip()
    normalized_connector = connector.replace("-", "_").upper() if connector else ""
    scoped_keys: list[str] = []
    if connector:
        scoped_keys.extend(
            [
                f"SUPERGLUE__TENANT__{tenant}__CONNECTOR__{connector}__{key}",
                f"SUPERGLUE__TENANT__{normalized}__CONNECTOR__{normalized_connector}__{key}",
                f"SUPERGLUE_{normalized}_{normalized_connector}_{key}",
                f"SUPERGLUE__CONNECTOR__{connector}__{key}",
                f"SUPERGLUE_CONNECTOR_{normalized_connector}_{key}",
            ]
        )
    scoped_keys.extend(
        [
            f"SUPERGLUE__TENANT__{tenant}__{key}",
            f"SUPERGLUE__TENANT__{normalized}__{key}",
            f"SUPERGLUE_{normalized}_{key}",
            f"SUPERGLUE_{key}",
        ]
    )
    return scoped_keys


def resolve_superglue_auth_token(tenant_id: str, *, allow_global_fallback: bool | None = None) -> str | None:
    fallback_allowed = (
        settings.APP_ENV != "production" and not settings.SUPERGLUE_REQUIRE_TENANT_SECRETS
        if allow_global_fallback is None
        else allow_global_fallback
    )
    keys = build_superglue_secret_keys(tenant_id, "AUTH_TOKEN")
    if not fallback_allowed:
        keys = keys[:-1]
    value = get_first_secret(keys, accessor=f"superglue:{tenant_id}")
    if value:
        return value
    if fallback_allowed:
        return settings.SUPERGLUE_AUTH_TOKEN
    return None


def resolve_superglue_connector_value(
    *,
    tenant_id: str,
    connector_key: str,
    field_name: str,
    fallback: str | None = None,
    allow_global_fallback: bool = True,
) -> str | None:
    keys = build_superglue_secret_keys(tenant_id, field_name, connector_key=connector_key)
    if not allow_global_fallback:
        keys = keys[:-1]
    value = get_first_secret(keys, accessor=f"superglue:{tenant_id}:{connector_key}")
    if value:
        return value
    return fallback
