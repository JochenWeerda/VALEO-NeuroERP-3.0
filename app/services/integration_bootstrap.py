from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.core.config import settings
from app.services.secrets_vault import get_secret


@dataclass(frozen=True)
class IntegrationCheck:
    integration_key: str
    required: bool
    status: str
    configured: bool
    missing: list[str]
    notes: list[str]


def _has_secret(*keys: str) -> bool:
    for key in keys:
        if get_secret(key, accessor="integration_bootstrap"):
            return True
    return False


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _oidc_check() -> IntegrationCheck:
    missing: list[str] = []
    if not _has_value(settings.OIDC_CLIENT_ID or settings.KEYCLOAK_CLIENT_ID):
        missing.append("OIDC_CLIENT_ID or KEYCLOAK_CLIENT_ID")
    if not _has_value(settings.OIDC_ISSUER_URL or settings.KEYCLOAK_URL):
        missing.append("OIDC_ISSUER_URL or KEYCLOAK_URL")

    status = "ready" if not missing else "partial"
    return IntegrationCheck(
        integration_key="oidc",
        required=True,
        status=status,
        configured=not missing,
        missing=missing,
        notes=["Local dev may use API_DEV_TOKEN, but tenant-safe auth should use OIDC/JWKS."],
    )


def _event_bus_check() -> IntegrationCheck:
    enabled = bool(settings.EVENT_BUS_ENABLED and settings.EVENT_BUS_PROVIDER == "nats")
    missing: list[str] = []
    if enabled and not _has_value(settings.EVENT_BUS_NATS_URL):
        missing.append("EVENT_BUS_NATS_URL")

    return IntegrationCheck(
        integration_key="event_bus_nats",
        required=False,
        status="ready" if enabled and not missing else ("disabled" if not enabled else "partial"),
        configured=enabled and not missing,
        missing=missing,
        notes=["Dev Compose should provide NATS automatically when EVENT_BUS is enabled."],
    )


def _superglue_check() -> IntegrationCheck:
    if not settings.SUPERGLUE_ENABLED:
        return IntegrationCheck(
            integration_key="superglue",
            required=False,
            status="disabled",
            configured=False,
            missing=[],
            notes=["Enable only for tenants or environments that actually use Superglue."],
        )

    missing: list[str] = []
    if not _has_value(settings.SUPERGLUE_BASE_URL or settings.SUPERGLUE_REST_URL):
        missing.append("SUPERGLUE_BASE_URL or SUPERGLUE_REST_URL")
    if not (_has_value(settings.SUPERGLUE_AUTH_TOKEN) or _has_secret("SUPERGLUE_AUTH_TOKEN")):
        missing.append("SUPERGLUE_AUTH_TOKEN")

    status = "ready" if not missing else "partial"
    return IntegrationCheck(
        integration_key="superglue",
        required=False,
        status=status,
        configured=not missing,
        missing=missing,
        notes=["Prod tenants should prefer tenant-scoped secrets over shared auth tokens."],
    )


def _voice_check() -> IntegrationCheck:
    stt_provider = "whisper"
    tts_provider = "openai"
    missing: list[str] = []
    notes: list[str] = []

    if stt_provider == "whisper" and not _has_secret("OPENAI_API_KEY", "VOICE_OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY for Whisper STT")
    if tts_provider == "openai" and not _has_secret("OPENAI_API_KEY", "VOICE_OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY for OpenAI TTS")

    if missing:
        notes.append("Browser fallback exists, but server-side voice providers need credentials.")

    return IntegrationCheck(
        integration_key="voice",
        required=False,
        status="ready" if not missing else "partial",
        configured=not missing,
        missing=missing,
        notes=notes,
    )


def _crm_downstream_check() -> IntegrationCheck:
    missing: list[str] = []
    for key, value in {
        "CRM_CORE_BASE_URL": settings.CRM_CORE_BASE_URL,
        "CRM_SALES_BASE_URL": settings.CRM_SALES_BASE_URL,
        "CRM_SERVICE_BASE_URL": settings.CRM_SERVICE_BASE_URL,
    }.items():
        if not _has_value(value):
            missing.append(key)

    return IntegrationCheck(
        integration_key="crm_downstream",
        required=False,
        status="ready" if not missing else "partial",
        configured=not missing,
        missing=missing,
        notes=["These URLs are repo-side defaults; productive routing remains environment-specific."],
    )


def build_integration_bootstrap_summary() -> dict[str, Any]:
    checks = [
        _oidc_check(),
        _event_bus_check(),
        _superglue_check(),
        _voice_check(),
        _crm_downstream_check(),
    ]
    ready = sum(1 for check in checks if check.status == "ready")
    partial = sum(1 for check in checks if check.status == "partial")
    disabled = sum(1 for check in checks if check.status == "disabled")
    required_blockers = [
        check.integration_key
        for check in checks
        if check.required and check.status != "ready"
    ]
    return {
        "integration_count": len(checks),
        "ready_count": ready,
        "partial_count": partial,
        "disabled_count": disabled,
        "required_blockers": required_blockers,
        "integrations": [asdict(check) for check in checks],
    }
