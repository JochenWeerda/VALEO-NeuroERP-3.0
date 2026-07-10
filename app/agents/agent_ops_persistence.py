"""Persistent snapshot storage for Agent Ops read models."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _state_path() -> Path:
    return _resolve_runtime_path(settings.AGENT_OPS_STATE_PATH)


def _history_path() -> Path:
    return _resolve_runtime_path(settings.AGENT_OPS_HISTORY_PATH)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _resolve_runtime_path(configured_path: str) -> Path:
    path = Path(configured_path).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if path != cwd and cwd not in path.parents:
        raise ValueError(f"Runtime path must stay inside the working directory: {configured_path}")
    return path


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


def load_agent_ops_tenant_snapshot(tenant_id: str) -> dict[str, Any] | None:
    payload = _read_state()
    tenant_snapshot = payload.get("tenants", {}).get(tenant_id)
    return tenant_snapshot if isinstance(tenant_snapshot, dict) else None


def save_agent_ops_tenant_snapshot(tenant_id: str, snapshot: dict[str, Any], *, reason: str) -> dict[str, Any]:
    payload = _read_state()
    updated_at = _utcnow()
    payload["updated_at"] = updated_at
    payload.setdefault("tenants", {})[tenant_id] = {
        **snapshot,
        "tenant_id": tenant_id,
        "persisted_at": updated_at,
    }
    path = _state_path()
    _ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    append_agent_ops_history_entry(
        tenant_id,
        {
            "event_type": "snapshot_saved",
            "reason": reason,
            "persisted_at": updated_at,
            "budget_count": len(snapshot.get("budgets", [])),
            "ticket_count": len(snapshot.get("tickets", [])),
            "revision_count": len(snapshot.get("config_revisions", [])),
        },
    )
    return payload["tenants"][tenant_id]


def append_agent_ops_history_entry(tenant_id: str, entry: dict[str, Any]) -> None:
    path = _history_path()
    _ensure_parent(path)
    history_entry = {
        "tenant_id": tenant_id,
        "timestamp": _utcnow(),
        **entry,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(history_entry, ensure_ascii=True) + "\n")


def list_agent_ops_history(tenant_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
    path = _history_path()
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(parsed.get("tenant_id")) == tenant_id:
            entries.append(parsed)
    return sorted(entries, key=lambda item: str(item.get("timestamp") or ""), reverse=True)[:limit]


def build_agent_ops_persistence_status(tenant_id: str) -> dict[str, Any]:
    tenant_snapshot = load_agent_ops_tenant_snapshot(tenant_id) or {}
    history = list_agent_ops_history(tenant_id, limit=10)
    return {
        "tenant_id": tenant_id,
        "state_path": str(_state_path()),
        "history_path": str(_history_path()),
        "persisted": bool(tenant_snapshot),
        "persisted_at": tenant_snapshot.get("persisted_at"),
        "history_count": len(history),
        "recent_events": history[:5],
        "snapshot_counts": {
            "budget_count": len(tenant_snapshot.get("budgets", [])),
            "ticket_count": len(tenant_snapshot.get("tickets", [])),
            "revision_count": len(tenant_snapshot.get("config_revisions", [])),
            "intervention_count": len(tenant_snapshot.get("interventions", [])),
        },
        "schema_version": 1,
    }
