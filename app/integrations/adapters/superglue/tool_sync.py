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
]


def list_superglue_tool_records(client: SuperglueClient | None = None) -> list[SuperglueToolRecord]:
    if not settings.SUPERGLUE_ENABLED or not settings.SUPERGLUE_SYNC_ENABLED:
        return _load_snapshot_records() or list(_DEFAULT_SUPERGLUE_TOOLS)

    sync_client = client or SuperglueClient()
    try:
        payload = sync_client.execute_graphql(
            """
            query ValeoSuperglueCatalog {
              tools {
                id
                version
                title
                targetKind
                executionModes
              }
            }
            """,
        )
        tools = payload.get("data", {}).get("tools", [])
        mapped: list[SuperglueToolRecord] = []
        for item in tools:
            mapped.append(
                SuperglueToolRecord(
                    external_tool_id=str(item["id"]),
                    external_tool_version=str(item.get("version", "1")),
                    valeo_contract_id=f"superglue.{item['id']}",
                    display_name=str(item.get("title", item["id"])),
                    execution_modes=list(item.get("executionModes", ["read"])),
                    target_kind=str(item.get("targetKind", "external_api")),
                    auth_model="superglue_token",
                    tags=["synced"],
                    metadata={"source_system": "superglue"},
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
    return {
        "provider_key": "superglue",
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "tool_count": len(records),
        "storage_path": str(_snapshot_path()),
        "schema_version": 1,
    }


def build_superglue_sync_status(client: SuperglueClient | None = None) -> SuperglueSyncStatus:
    records = list_superglue_tool_records(client)
    snapshot = _load_snapshot_payload()
    return SuperglueSyncStatus(
        enabled=settings.SUPERGLUE_ENABLED,
        sync_enabled=settings.SUPERGLUE_SYNC_ENABLED,
        execution_enabled=settings.SUPERGLUE_EXECUTION_ENABLED,
        tool_count=len(records),
        healthy=settings.SUPERGLUE_ENABLED and bool(settings.SUPERGLUE_BASE_URL or settings.SUPERGLUE_GRAPHQL_URL),
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
        sync_client.request("GET", "/health", mode="rest")
        return SuperglueHealthStatus(
            healthy=True,
            checked_at=checked_at,
            detail="HTTP health check erfolgreich",
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
        "quarantine_log_path": settings.SUPERGLUE_QUARANTINE_LOG_PATH,
        "allowed_hosts": list(settings.SUPERGLUE_ALLOWED_HOSTS),
        "allowed_domains": list(settings.SUPERGLUE_ALLOWED_DOMAINS),
        "schema_version": 1,
    }


def _snapshot_path() -> Path:
    return Path(settings.SUPERGLUE_SYNC_STATE_PATH)


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
