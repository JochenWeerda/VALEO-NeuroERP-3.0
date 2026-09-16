"""Process-local studio drafts with tenant isolation and four-eyes publish."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

_DRAFTS: dict[str, dict[str, Any]] = {}


def reset_studio_drafts() -> None:
    _DRAFTS.clear()


def list_drafts(tenant_id: str) -> list[dict[str, Any]]:
    return [deepcopy(item) for item in _DRAFTS.values() if item["tenant_id"] == tenant_id]


def get_draft(tenant_id: str, draft_id: str) -> dict[str, Any] | None:
    item = _DRAFTS.get(draft_id)
    if item is None or item["tenant_id"] != tenant_id:
        return None
    return deepcopy(item)


def save_draft(
    tenant_id: str,
    actor: str,
    definition: dict[str, Any],
    *,
    draft_id: str | None = None,
    readiness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    existing = _DRAFTS.get(draft_id) if draft_id else None
    if existing is not None and existing["tenant_id"] != tenant_id:
        raise KeyError(draft_id)
    if existing is not None and existing["status"] not in {"draft", "review"}:
        raise ValueError(f"status_{existing['status']}_nicht_editierbar")
    now = datetime.now(UTC).isoformat()
    record = {
        "id": existing["id"] if existing else str(uuid4()),
        "tenant_id": tenant_id,
        "screen_id": definition.get("id"),
        "definition": deepcopy(definition),
        "status": existing["status"] if existing else "draft",
        "readiness": deepcopy(readiness) if readiness is not None else (existing or {}).get("readiness"),
        "created_by": existing["created_by"] if existing else actor,
        "updated_by": actor,
        "updated_at": now,
    }
    _DRAFTS[record["id"]] = record
    return deepcopy(record)


def set_status(tenant_id: str, draft_id: str, actor: str, status: str) -> dict[str, Any]:
    item = _DRAFTS.get(draft_id)
    if item is None or item["tenant_id"] != tenant_id:
        raise KeyError(draft_id)
    if status == "published_temp" and item["updated_by"] == actor:
        raise PermissionError("vier_augen:publisher_gleich_letzter_editor")
    item = deepcopy(item)
    item["status"] = status
    item["updated_by"] = actor
    item["updated_at"] = datetime.now(UTC).isoformat()
    _DRAFTS[draft_id] = item
    return deepcopy(item)
