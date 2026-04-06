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
    idempotency_key: str | None = None,
    cost_cents: int = 0,
    artifacts: list[dict[str, Any]] | None = None,
    replayed_from_correlation_id: str | None = None,
) -> dict[str, Any]:
    latency_ms = max(0, int((finished_at - started_at).total_seconds() * 1000))
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": tenant_id,
        "correlation_id": correlation_id,
        "idempotency_key": idempotency_key,
        "replayed_from_correlation_id": replayed_from_correlation_id,
        "tool_id": tool_id,
        "execution_mode": execution_mode,
        "target_kind": target_kind,
        "result_status": result_status,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "latency_ms": latency_ms,
        "cost_cents": max(0, int(cost_cents or 0)),
        "artifacts": artifacts or [],
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
    replay_entries = [entry for entry in entries if entry.get("replayed_from_correlation_id")]
    avg_latency_ms = int(sum(int(entry.get("latency_ms") or 0) for entry in entries) / len(entries)) if entries else 0
    total_cost_cents = sum(int(entry.get("cost_cents") or 0) for entry in entries)
    artifact_count = sum(len(entry.get("artifacts") or []) for entry in entries)
    by_tool: dict[str, int] = {}
    by_tenant: dict[str, int] = {}
    for entry in entries:
        by_tool[str(entry.get("tool_id") or "unknown")] = by_tool.get(str(entry.get("tool_id") or "unknown"), 0) + 1
        by_tenant[str(entry.get("tenant_id") or "unknown")] = by_tenant.get(str(entry.get("tenant_id") or "unknown"), 0) + 1
    return {
        "entry_count": len(entries),
        "success_count": len(success_entries),
        "error_count": len(error_entries),
        "replay_count": len(replay_entries),
        "average_latency_ms": avg_latency_ms,
        "total_cost_cents": total_cost_cents,
        "artifact_count": artifact_count,
        "by_tool": by_tool,
        "by_tenant": by_tenant,
        "latest": entries[-1] if entries else None,
        "entries": entries[-limit:],
        "storage_path": str(_storage_path()),
        "schema_version": 1,
    }


def find_latest_execution_by_idempotency_key(*, tenant_id: str, tool_id: str, idempotency_key: str) -> dict[str, Any] | None:
    normalized_key = str(idempotency_key or "").strip()
    if not normalized_key:
        return None
    for entry in reversed(list_execution_journal_entries(limit=2000)):
        if (
            str(entry.get("tenant_id")) == tenant_id
            and str(entry.get("tool_id")) == tool_id
            and str(entry.get("idempotency_key") or "") == normalized_key
        ):
            return entry
    return None
