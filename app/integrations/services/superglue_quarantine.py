"""Append-only quarantine log for degraded or failed Superglue executions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import settings


class SuperglueQuarantineEntry(BaseModel):
    timestamp: str
    tenant_id: str
    tool_id: str
    execution_mode: str
    outcome: str
    reason: str
    correlation_id: str | None = None
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
        timestamp=datetime.now(timezone.utc).isoformat(),
        tenant_id=tenant_id,
        tool_id=tool_id,
        execution_mode=execution_mode,
        outcome=outcome,
        reason=reason,
        correlation_id=correlation_id,
        detail=detail or {},
    )
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry.model_dump_json())
        handle.write("\n")
    return entry


def list_quarantine_entries(limit: int = 50) -> list[dict[str, Any]]:
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
    return entries[-limit:]


def build_quarantine_summary() -> dict[str, Any]:
    entries = list_quarantine_entries(limit=500)
    return {
        "entry_count": len(entries),
        "latest": entries[-1] if entries else None,
        "entries": entries[-20:],
        "storage_path": str(_storage_path()),
        "schema_version": 1,
    }
