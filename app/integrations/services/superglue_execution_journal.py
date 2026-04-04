"""Append-only execution journal for Superglue operations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings


def _storage_path() -> Path:
    return Path(settings.SUPERGLUE_EXECUTION_JOURNAL_PATH)


def append_execution_journal_entry(
    *,
    tenant_id: str,
    correlation_id: str,
    tool_id: str,
    execution_mode: str,
    target_kind: str,
    result_status: str,
    started_at: datetime,
    finished_at: datetime,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": tenant_id,
        "correlation_id": correlation_id,
        "tool_id": tool_id,
        "execution_mode": execution_mode,
        "target_kind": target_kind,
        "result_status": result_status,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "detail": detail or {},
    }
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True, sort_keys=True))
        handle.write("\n")
    return entry


def list_execution_journal_entries(limit: int = 50) -> list[dict[str, Any]]:
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
                data = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                entries.append(data)
    return entries[-limit:]


def build_execution_journal_summary(limit: int = 20) -> dict[str, Any]:
    entries = list_execution_journal_entries(limit=500)
    success_entries = [entry for entry in entries if entry.get("result_status") == "success"]
    error_entries = [entry for entry in entries if entry.get("result_status") != "success"]
    return {
        "entry_count": len(entries),
        "success_count": len(success_entries),
        "error_count": len(error_entries),
        "latest": entries[-1] if entries else None,
        "entries": entries[-limit:],
        "storage_path": str(_storage_path()),
        "schema_version": 1,
    }
