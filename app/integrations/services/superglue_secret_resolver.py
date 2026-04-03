"""Tenant-aware secret resolution for Superglue credentials."""

from __future__ import annotations

from app.core.config import settings
from app.services.secrets_vault import get_first_secret


def build_superglue_secret_keys(tenant_id: str, key_name: str = "AUTH_TOKEN") -> list[str]:
    tenant = tenant_id.strip()
    normalized = tenant.replace("-", "_").upper()
    key = key_name.strip().upper()
    return [
        f"SUPERGLUE__TENANT__{tenant}__{key}",
        f"SUPERGLUE__TENANT__{normalized}__{key}",
        f"SUPERGLUE_{normalized}_{key}",
        f"SUPERGLUE_{key}",
    ]


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
