"""Persistent admin mutation state for Superglue tenant control-center flows."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _state_path() -> Path:
    return Path(settings.SUPERGLUE_ADMIN_STATE_PATH)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_state() -> dict[str, Any]:
    path = _state_path()
    if not path.exists():
        return {"schema_version": 1, "updated_at": None, "tenants": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": 1, "updated_at": None, "tenants": {}}
    if not isinstance(payload, dict):
        return {"schema_version": 1, "updated_at": None, "tenants": {}}
    payload.setdefault("schema_version", 1)
    payload.setdefault("updated_at", None)
    payload.setdefault("tenants", {})
    return payload


def _write_state(payload: dict[str, Any]) -> None:
    path = _state_path()
    _ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _tenant_state(payload: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    return payload.setdefault("tenants", {}).setdefault(
        tenant_id,
        {
            "connector_overrides": {},
            "policy_overrides": {},
            "wizard": {
                "current_step": "credentials",
                "completed_steps": [],
                "last_updated_at": None,
            },
        },
    )


def get_superglue_admin_state(tenant_id: str) -> dict[str, Any]:
    payload = _read_state()
    state = _tenant_state(payload, tenant_id)
    return {
        "tenant_id": tenant_id,
        "storage_path": str(_state_path()),
        "connector_overrides": state.get("connector_overrides", {}),
        "policy_overrides": state.get("policy_overrides", {}),
        "wizard": state.get("wizard", {}),
        "schema_version": 1,
    }


def get_superglue_connector_override(tenant_id: str, connector_key: str) -> dict[str, Any]:
    state = get_superglue_admin_state(tenant_id)
    override = state["connector_overrides"].get(connector_key, {})
    return override if isinstance(override, dict) else {}


def get_superglue_policy_override(tenant_id: str) -> dict[str, Any]:
    state = get_superglue_admin_state(tenant_id)
    override = state.get("policy_overrides", {})
    return override if isinstance(override, dict) else {}


def update_superglue_connector_override(
    tenant_id: str,
    connector_key: str,
    *,
    system_url: str | None = None,
    system_name: str | None = None,
    system_instructions: str | None = None,
) -> dict[str, Any]:
    payload = _read_state()
    state = _tenant_state(payload, tenant_id)
    overrides = state.setdefault("connector_overrides", {}).setdefault(connector_key, {})
    if system_url is not None:
        overrides["system_url"] = system_url
    if system_name is not None:
        overrides["system_name"] = system_name
    if system_instructions is not None:
        overrides["system_instructions"] = system_instructions
    payload["updated_at"] = _utcnow()
    state["wizard"]["last_updated_at"] = payload["updated_at"]
    _write_state(payload)
    return {
        "tenant_id": tenant_id,
        "connector_key": connector_key,
        "override": overrides,
        "updated_at": payload["updated_at"],
        "schema_version": 1,
    }


def update_superglue_policy_override(
    tenant_id: str,
    *,
    require_tenant_secrets: bool | None = None,
    execution_enabled: bool | None = None,
    alert_error_rate_pct: float | None = None,
    alert_open_quarantine_count: int | None = None,
    run_retention_days: int | None = None,
    artifact_retention_days: int | None = None,
) -> dict[str, Any]:
    payload = _read_state()
    state = _tenant_state(payload, tenant_id)
    overrides = state.setdefault("policy_overrides", {})
    if require_tenant_secrets is not None:
        overrides["require_tenant_secrets"] = require_tenant_secrets
    if execution_enabled is not None:
        overrides["execution_enabled"] = execution_enabled
    if alert_error_rate_pct is not None:
        overrides["alert_error_rate_pct"] = alert_error_rate_pct
    if alert_open_quarantine_count is not None:
        overrides["alert_open_quarantine_count"] = alert_open_quarantine_count
    if run_retention_days is not None:
        overrides["run_retention_days"] = run_retention_days
    if artifact_retention_days is not None:
        overrides["artifact_retention_days"] = artifact_retention_days
    payload["updated_at"] = _utcnow()
    state["wizard"]["last_updated_at"] = payload["updated_at"]
    _write_state(payload)
    return {
        "tenant_id": tenant_id,
        "policy_overrides": overrides,
        "updated_at": payload["updated_at"],
        "schema_version": 1,
    }


def update_superglue_wizard_state(
    tenant_id: str,
    *,
    current_step: str | None = None,
    completed_step: str | None = None,
) -> dict[str, Any]:
    payload = _read_state()
    state = _tenant_state(payload, tenant_id)
    wizard = state.setdefault("wizard", {"current_step": "credentials", "completed_steps": []})
    if current_step is not None:
        wizard["current_step"] = current_step
    if completed_step is not None and completed_step not in wizard.setdefault("completed_steps", []):
        wizard["completed_steps"].append(completed_step)
    wizard["last_updated_at"] = _utcnow()
    payload["updated_at"] = wizard["last_updated_at"]
    _write_state(payload)
    return {
        "tenant_id": tenant_id,
        "wizard": wizard,
        "schema_version": 1,
    }
