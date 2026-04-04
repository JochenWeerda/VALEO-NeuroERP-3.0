"""Append-only quarantine log for degraded or failed Superglue executions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.core.config import settings


class SuperglueQuarantineEntry(BaseModel):
    entry_id: str
    event_type: str = "incident"
    timestamp: str
    status: str = "open"
    tenant_id: str
    tool_id: str
    execution_mode: str
    outcome: str
    reason: str
    correlation_id: str | None = None
    resolved_at: str | None = None
    resolved_by: str | None = None
    detail: dict[str, Any] = Field(default_factory=dict)


def _storage_path() -> Path:
    return Path(settings.SUPERGLUE_QUARANTINE_LOG_PATH)


def append_quarantine_entry(
    *,
    tenant_id: str,
    tool_id: str,
    execution_mode: str,
    outcome: str,
    reason: str,
    correlation_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> SuperglueQuarantineEntry:
    entry = SuperglueQuarantineEntry(
        entry_id=f"sgq-{uuid4()}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        tenant_id=tenant_id,
        tool_id=tool_id,
        execution_mode=execution_mode,
        outcome=outcome,
        reason=reason,
        correlation_id=correlation_id,
        detail=detail or {},
    )
    _append_event(entry.model_dump())
    return entry


def resolve_quarantine_entry(
    *,
    entry_id: str,
    resolved_by: str,
    note: str | None = None,
) -> dict[str, Any]:
    entries = _fold_events()
    if entry_id not in entries:
        raise KeyError(entry_id)
    current = entries[entry_id]
    event = SuperglueQuarantineEntry(
        entry_id=entry_id,
        event_type="resolve",
        timestamp=datetime.now(timezone.utc).isoformat(),
        status="resolved",
        tenant_id=str(current.get("tenant_id", "unknown")),
        tool_id=str(current.get("tool_id", "unknown")),
        execution_mode=str(current.get("execution_mode", "unknown")),
        outcome="resolved",
        reason=note or "reviewed",
        correlation_id=current.get("correlation_id"),
        resolved_at=datetime.now(timezone.utc).isoformat(),
        resolved_by=resolved_by,
        detail={"note": note or "", "previous_outcome": current.get("outcome")},
    )
    _append_event(event.model_dump())
    updated = _fold_events().get(entry_id, current)
    return updated


def list_quarantine_entries(*, limit: int = 50, status: str = "all") -> list[dict[str, Any]]:
    entries = list(_fold_events().values())
    if status != "all":
        entries = [entry for entry in entries if entry.get("status") == status]
    entries.sort(key=lambda item: str(item.get("timestamp", "")))
    return entries[-limit:]


def _load_raw_events(limit: int | None = None) -> list[dict[str, Any]]:
    path = _storage_path()
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            try:
                entries.append(json.loads(payload))
            except json.JSONDecodeError:
                continue
    return entries[-limit:] if limit else entries


def _fold_events() -> dict[str, dict[str, Any]]:
    folded: dict[str, dict[str, Any]] = {}
    for event in _load_raw_events():
        entry_id = str(event.get("entry_id") or "")
        if not entry_id:
            continue
        existing = folded.get(entry_id)
        if event.get("event_type") == "resolve" and existing:
            existing["status"] = "resolved"
            existing["resolved_at"] = event.get("resolved_at") or event.get("timestamp")
            existing["resolved_by"] = event.get("resolved_by")
            existing["resolution_reason"] = event.get("reason")
            existing["resolution_detail"] = event.get("detail", {})
            existing["last_event_at"] = event.get("timestamp")
            continue
        normalized = dict(event)
        normalized.setdefault("status", "open")
        normalized["last_event_at"] = event.get("timestamp")
        folded[entry_id] = normalized
    return folded


def _append_event(entry: dict[str, Any]) -> None:
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True, sort_keys=True))
        handle.write("\n")


def build_quarantine_summary() -> dict[str, Any]:
    all_entries = list_quarantine_entries(limit=500, status="all")
    open_entries = [entry for entry in all_entries if entry.get("status") == "open"]
    resolved_entries = [entry for entry in all_entries if entry.get("status") == "resolved"]
    return {
        "entry_count": len(all_entries),
        "open_count": len(open_entries),
        "resolved_count": len(resolved_entries),
        "latest": all_entries[-1] if all_entries else None,
        "entries": all_entries[-20:],
        "open_entries": open_entries[-20:],
        "resolved_entries": resolved_entries[-20:],
        "storage_path": str(_storage_path()),
        "schema_version": 1,
    }
