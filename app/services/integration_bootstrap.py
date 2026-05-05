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


@dataclass(frozen=True)
class IntegrationProbe:
    integration_key: str
    status: str
    probe_kind: str
    target: str | None
    command_hint: str | None
    blocked_by: list[str]
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


def _probe_status(check: IntegrationCheck) -> str:
    if check.status == "disabled":
        return "disabled"
    if check.missing:
        return "blocked"
    if check.status == "ready":
        return "ready"
    return "manual"


def _oidc_probe(check: IntegrationCheck) -> IntegrationProbe:
    issuer = settings.OIDC_ISSUER_URL or settings.KEYCLOAK_URL
    target = f"{str(issuer).rstrip('/')}/.well-known/openid-configuration" if issuer else None
    return IntegrationProbe(
        integration_key=check.integration_key,
        status=_probe_status(check),
        probe_kind="http_get",
        target=target,
        command_hint=f"curl -fsS {target}" if target else None,
        blocked_by=list(check.missing),
        notes=["Validates issuer reachability and OIDC discovery metadata."],
    )


def _event_bus_probe(check: IntegrationCheck) -> IntegrationProbe:
    target = settings.EVENT_BUS_NATS_URL if _has_value(settings.EVENT_BUS_NATS_URL) else None
    return IntegrationProbe(
        integration_key=check.integration_key,
        status=_probe_status(check),
        probe_kind="nats_connect",
        target=target,
        command_hint=f"nats server check --server {target}" if target else None,
        blocked_by=list(check.missing),
        notes=["Requires NATS CLI or equivalent JetStream client in the target environment."],
    )


def _superglue_probe(check: IntegrationCheck) -> IntegrationProbe:
    base_url = settings.SUPERGLUE_BASE_URL or settings.SUPERGLUE_REST_URL
    target = f"{str(base_url).rstrip('/')}/health" if base_url else None
    return IntegrationProbe(
        integration_key=check.integration_key,
        status=_probe_status(check),
        probe_kind="http_get_authenticated",
        target=target,
        command_hint=f"curl -fsS -H \"Authorization: Bearer $SUPERGLUE_AUTH_TOKEN\" {target}" if target else None,
        blocked_by=list(check.missing),
        notes=["Tenant-scoped token should come from the configured secret provider."],
    )


def _voice_probe(check: IntegrationCheck) -> IntegrationProbe:
    return IntegrationProbe(
        integration_key=check.integration_key,
        status=_probe_status(check),
        probe_kind="provider_smoke",
        target="configured STT/TTS provider" if check.status != "disabled" else None,
        command_hint="POST /api/v1/neuro/voice/transcribe with a short sample audio file",
        blocked_by=list(check.missing),
        notes=["Browser fallback is not a substitute for server-side provider validation."],
    )


def _crm_downstream_probe(check: IntegrationCheck) -> IntegrationProbe:
    targets = [
        value
        for value in (
            settings.CRM_CORE_BASE_URL,
            settings.CRM_SALES_BASE_URL,
            settings.CRM_SERVICE_BASE_URL,
        )
        if _has_value(value)
    ]
    target = ", ".join(str(value).rstrip("/") for value in targets) if targets else None
    command_hint = (
        " && ".join(f"curl -fsS {str(value).rstrip('/')}/health" for value in targets)
        if targets
        else None
    )
    return IntegrationProbe(
        integration_key=check.integration_key,
        status=_probe_status(check),
        probe_kind="http_get",
        target=target,
        command_hint=command_hint,
        blocked_by=list(check.missing),
        notes=["All CRM downstream services should be checked in the same tenant/network context."],
    )


def build_integration_probe_plan(
    checks: list[IntegrationCheck] | None = None,
) -> list[IntegrationProbe]:
    checks_by_key = {
        check.integration_key: check
        for check in (
            checks
            if checks is not None
            else [
                _oidc_check(),
                _event_bus_check(),
                _superglue_check(),
                _voice_check(),
                _crm_downstream_check(),
            ]
        )
    }
    return [
        _oidc_probe(checks_by_key["oidc"]),
        _event_bus_probe(checks_by_key["event_bus_nats"]),
        _superglue_probe(checks_by_key["superglue"]),
        _voice_probe(checks_by_key["voice"]),
        _crm_downstream_probe(checks_by_key["crm_downstream"]),
    ]


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
        "probe_plan": [asdict(probe) for probe in build_integration_probe_plan(checks)],
    }
