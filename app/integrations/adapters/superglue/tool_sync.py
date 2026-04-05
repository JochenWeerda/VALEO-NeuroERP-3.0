"""Superglue catalog mapping into VALEO's provider and manifest surface."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.contracts import SuperglueToolRecord


class SuperglueSyncStatus(BaseModel):
    provider_key: str = "superglue"
    enabled: bool = False
    sync_enabled: bool = False
    execution_enabled: bool = False
    tool_count: int = 0
    healthy: bool = False
    dashboard_url: str | None = None
    graphql_url: str | None = None
    rest_url: str | None = None
    auth_mode: str = "tenant-scoped secret + bearer header"
    last_synced_at: str | None = None
    last_error: str | None = None
    schema_version: int = 1


class SuperglueHealthStatus(BaseModel):
    provider_key: str = "superglue"
    healthy: bool = False
    checked_at: str
    detail: str | None = None
    dashboard_url: str | None = None
    schema_version: int = 1


_DEFAULT_SUPERGLUE_TOOLS: list[SuperglueToolRecord] = [
    SuperglueToolRecord(
        external_tool_id="sg.document.search",
        external_tool_version="2026.04",
        valeo_contract_id="superglue.document.search",
        display_name="Superglue Document Search",
        execution_modes=["read", "suggest"],
        target_kind="document",
        auth_model="superglue_token",
        tags=["pilot", "document", "search"],
        metadata={"source_system": "superglue"},
    ),
    SuperglueToolRecord(
        external_tool_id="sg.document.metadata",
        external_tool_version="2026.04",
        valeo_contract_id="superglue.document.metadata",
        display_name="Superglue Document Metadata",
        execution_modes=["read"],
        target_kind="document",
        auth_model="superglue_token",
        tags=["pilot", "document", "metadata"],
        metadata={"source_system": "superglue"},
    ),
    SuperglueToolRecord(
        external_tool_id="sg.partner.adapter.preview",
        external_tool_version="2026.04",
        valeo_contract_id="superglue.partner.adapter.preview",
        display_name="Superglue Partner Adapter Preview",
        execution_modes=["simulate", "suggest"],
        target_kind="partner_adapter",
        auth_model="superglue_token",
        tags=["partner", "preview"],
        metadata={"source_system": "superglue"},
    ),
    SuperglueToolRecord(
        external_tool_id="sg.customer.profile.preview",
        external_tool_version="2026.04",
        valeo_contract_id="superglue.customer.profile.preview",
        display_name="Superglue Customer Profile Preview",
        execution_modes=["read", "suggest"],
        target_kind="customer_profile",
        auth_model="superglue_token",
        tags=["crm", "preview"],
        metadata={"source_system": "superglue"},
    ),
]

_PILOT_TOOL_DEFAULTS: dict[str, dict[str, Any]] = {
    item.external_tool_id: {
        "display_name": item.display_name,
        "execution_modes": list(item.execution_modes),
        "target_kind": item.target_kind,
        "tags": list(item.tags),
    }
    for item in _DEFAULT_SUPERGLUE_TOOLS
}


def list_superglue_tool_records(client: SuperglueClient | None = None) -> list[SuperglueToolRecord]:
    if not settings.SUPERGLUE_ENABLED or not settings.SUPERGLUE_SYNC_ENABLED:
        return _load_snapshot_records() or list(_DEFAULT_SUPERGLUE_TOOLS)

    sync_client = client or SuperglueClient()
    try:
        payload = sync_client.request("GET", "/v1/tools", mode="rest", params={"page": 1, "limit": 100})
        tools = payload.get("data", [])
        mapped: list[SuperglueToolRecord] = []
        for item in tools:
            tool_id = str(item.get("id") or item.get("toolId") or "").strip()
            if not tool_id:
                continue
            mapped.append(
                SuperglueToolRecord(
                    external_tool_id=tool_id,
                    external_tool_version=str(item.get("version", item.get("updatedAt", "1"))),
                    valeo_contract_id=f"superglue.{tool_id}",
                    display_name=str(
                        item.get("title")
                        or item.get("name")
                        or _pilot_tool_defaults(tool_id).get("display_name")
                        or tool_id
                    ),
                    execution_modes=_normalize_execution_modes(item),
                    target_kind=str(item.get("targetKind") or _pilot_tool_defaults(tool_id).get("target_kind") or "external_api"),
                    auth_model="superglue_token",
                    tags=_normalize_tags(tool_id),
                    metadata={
                        "source_system": "superglue",
                        "folder_path": item.get("folderPath"),
                        "request_source": "rest_v1",
                    },
                )
            )
        if mapped:
            _persist_snapshot(mapped)
            return mapped
        return _load_snapshot_records() or list(_DEFAULT_SUPERGLUE_TOOLS)
    except Exception:
        return _load_snapshot_records() or list(_DEFAULT_SUPERGLUE_TOOLS)


def refresh_superglue_sync_snapshot(client: SuperglueClient | None = None) -> dict[str, Any]:
    records = list_superglue_tool_records(client)
    _persist_snapshot(records)
    payload = {
        "provider_key": "superglue",
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "tool_count": len(records),
        "storage_path": str(_snapshot_path()),
        "schema_version": 1,
    }
    _append_sync_history(payload)
    return payload


def build_superglue_sync_status(client: SuperglueClient | None = None) -> SuperglueSyncStatus:
    records = list_superglue_tool_records(client)
    snapshot = _load_snapshot_payload()
    return SuperglueSyncStatus(
        enabled=settings.SUPERGLUE_ENABLED,
        sync_enabled=settings.SUPERGLUE_SYNC_ENABLED,
        execution_enabled=settings.SUPERGLUE_EXECUTION_ENABLED,
        tool_count=len(records),
        healthy=settings.SUPERGLUE_ENABLED and bool(
            settings.SUPERGLUE_BASE_URL or settings.SUPERGLUE_GRAPHQL_URL or settings.SUPERGLUE_REST_URL
        ),
        dashboard_url=settings.SUPERGLUE_DASHBOARD_URL,
        graphql_url=settings.SUPERGLUE_GRAPHQL_URL,
        rest_url=settings.SUPERGLUE_REST_URL or settings.SUPERGLUE_BASE_URL,
        last_synced_at=snapshot.get("refreshed_at") if snapshot else datetime.now(timezone.utc).isoformat(),
    )


def build_superglue_health_status(client: SuperglueClient | None = None) -> SuperglueHealthStatus:
    checked_at = datetime.now(timezone.utc).isoformat()
    if not settings.SUPERGLUE_ENABLED:
        return SuperglueHealthStatus(
            healthy=False,
            checked_at=checked_at,
            detail="SUPERGLUE_ENABLED=false",
            dashboard_url=settings.SUPERGLUE_DASHBOARD_URL,
        )
    if not (settings.SUPERGLUE_BASE_URL or settings.SUPERGLUE_GRAPHQL_URL or settings.SUPERGLUE_REST_URL):
        return SuperglueHealthStatus(
            healthy=False,
            checked_at=checked_at,
            detail="Keine Superglue URL konfiguriert",
            dashboard_url=settings.SUPERGLUE_DASHBOARD_URL,
        )
    sync_client = client or SuperglueClient()
    try:
        sync_client.request("GET", "/v1/health", mode="rest")
        return SuperglueHealthStatus(
            healthy=True,
            checked_at=checked_at,
            detail="HTTP /v1/health erfolgreich",
            dashboard_url=settings.SUPERGLUE_DASHBOARD_URL,
        )
    except Exception as exc:
        return SuperglueHealthStatus(
            healthy=False,
            checked_at=checked_at,
            detail=str(exc),
            dashboard_url=settings.SUPERGLUE_DASHBOARD_URL,
        )


def build_superglue_tool_summary() -> dict[str, Any]:
    records = list_superglue_tool_records()
    return {
        "provider_key": "superglue",
        "tool_count": len(records),
        "tools": [item.model_dump() for item in records],
        "schema_version": 1,
    }


def build_superglue_config_summary() -> dict[str, Any]:
    return {
        "provider_key": "superglue",
        "enabled": settings.SUPERGLUE_ENABLED,
        "sync_enabled": settings.SUPERGLUE_SYNC_ENABLED,
        "execution_enabled": settings.SUPERGLUE_EXECUTION_ENABLED,
        "require_tenant_secrets": settings.SUPERGLUE_REQUIRE_TENANT_SECRETS,
        "base_url_configured": bool(settings.SUPERGLUE_BASE_URL),
        "graphql_url_configured": bool(settings.SUPERGLUE_GRAPHQL_URL),
        "rest_url_configured": bool(settings.SUPERGLUE_REST_URL),
        "dashboard_url": settings.SUPERGLUE_DASHBOARD_URL,
        "auth_token_configured": bool(settings.SUPERGLUE_AUTH_TOKEN),
        "sync_state_path": settings.SUPERGLUE_SYNC_STATE_PATH,
        "sync_history_path": settings.SUPERGLUE_SYNC_HISTORY_PATH,
        "quarantine_log_path": settings.SUPERGLUE_QUARANTINE_LOG_PATH,
        "execution_journal_path": settings.SUPERGLUE_EXECUTION_JOURNAL_PATH,
        "allowed_hosts": list(settings.SUPERGLUE_ALLOWED_HOSTS),
        "allowed_domains": list(settings.SUPERGLUE_ALLOWED_DOMAINS),
        "allow_loopback_dev_egress": settings.SUPERGLUE_ALLOW_LOOPBACK_DEV_EGRESS,
        "schema_version": 1,
    }


def build_superglue_sync_history(limit: int = 20) -> dict[str, Any]:
    entries = _load_sync_history_entries(limit=limit)
    return {
        "provider_key": "superglue",
        "entry_count": len(entries),
        "latest": entries[-1] if entries else None,
        "entries": entries,
        "storage_path": str(_sync_history_path()),
        "schema_version": 1,
    }


def get_superglue_tool_record(tool_id: str) -> SuperglueToolRecord | None:
    normalized = str(tool_id or "").strip()
    if not normalized:
        return None
    for record in list_superglue_tool_records():
        if normalized in {record.external_tool_id, record.valeo_contract_id}:
            return record
    return None


def validate_superglue_execution_request(
    *,
    tool_id: str,
    execution_mode: str,
    target_kind: str,
) -> SuperglueToolRecord:
    record = get_superglue_tool_record(tool_id)
    if record is None:
        raise ValueError(f"Unbekanntes Superglue-Tool: {tool_id}")
    if execution_mode not in record.execution_modes:
        raise ValueError(
            f"Execution-Mode {execution_mode!r} ist fuer Tool {record.external_tool_id!r} nicht erlaubt"
        )
    if target_kind and target_kind != record.target_kind:
        raise ValueError(
            f"Target-Kind {target_kind!r} passt nicht zu Tool {record.external_tool_id!r} ({record.target_kind!r})"
        )
    return record


def _snapshot_path() -> Path:
    return Path(settings.SUPERGLUE_SYNC_STATE_PATH)


def _sync_history_path() -> Path:
    return Path(settings.SUPERGLUE_SYNC_HISTORY_PATH)


def _persist_snapshot(records: list[SuperglueToolRecord]) -> None:
    path = _snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "provider_key": "superglue",
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "tools": [item.model_dump() for item in records],
        "schema_version": 1,
    }
    path.write_text(json.dumps(payload, ensure_ascii=True, sort_keys=True), encoding="utf-8")


def _append_sync_history(entry: dict[str, Any]) -> None:
    path = _sync_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True, sort_keys=True))
        handle.write("\n")


def _load_snapshot_payload() -> dict[str, Any] | None:
    path = _snapshot_path()
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _load_snapshot_records() -> list[SuperglueToolRecord]:
    payload = _load_snapshot_payload()
    if not payload:
        return []
    tools = payload.get("tools", [])
    records: list[SuperglueToolRecord] = []
    for item in tools:
        try:
            records.append(SuperglueToolRecord.model_validate(item))
        except Exception:
            continue
    return records


def _load_sync_history_entries(limit: int = 20) -> list[dict[str, Any]]:
    path = _sync_history_path()
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                entries.append(data)
    return entries[-limit:]


def _normalize_execution_modes(item: dict[str, Any]) -> list[str]:
    tool_id = str(item.get("id") or item.get("toolId") or "").strip()
    raw_modes = item.get("executionModes")
    if isinstance(raw_modes, list) and raw_modes:
        return [str(mode) for mode in raw_modes]
    known_modes = _pilot_tool_defaults(tool_id).get("execution_modes")
    if isinstance(known_modes, list) and known_modes:
        return [str(mode) for mode in known_modes]
    return ["read", "suggest", "simulate", "execute"]


def _pilot_tool_defaults(tool_id: str) -> dict[str, Any]:
    return _PILOT_TOOL_DEFAULTS.get(str(tool_id).strip(), {})


def _normalize_tags(tool_id: str) -> list[str]:
    known_tags = _pilot_tool_defaults(tool_id).get("tags")
    if isinstance(known_tags, list) and known_tags:
        return ["synced", *[str(tag) for tag in known_tags]]
    return ["synced"]
