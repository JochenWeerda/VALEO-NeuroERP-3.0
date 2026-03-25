from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from app.core.flow_spine_registry import (
    get_flow_spine_catalog,
    get_flow_spine_workspace,
    merge_instance_statuses,
)


router = APIRouter(prefix="/process/flow-spines", tags=["process", "flow-spines"])

# In-memory instance store (will be replaced with Redis/DB in production)
_instances: dict[str, dict] = {}  # key: instance_id


def _utcnow() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class InstanceCreateRequest(BaseModel):
    label: str
    linked_document_id: Optional[str] = None
    linked_document_type: Optional[str] = None


class TransitionRequest(BaseModel):
    node_id: str
    new_status: str
    action_label: str
    user_id: Optional[str] = None


# ── Catalog ──────────────────────────────────────────────────────────────────

@router.get("/catalog", response_model=dict)
def get_catalog(lang: Optional[str] = Query(None, description="Optional language code for localized process labels")) -> dict[str, Any]:
    return get_flow_spine_catalog(lang)


# ── Workspace (with optional instance overlay) ───────────────────────────────

@router.get("/{process_key}", response_model=dict)
def get_workspace(
    process_key: str,
    instance_id: Optional[str] = Query(None, description="Optional instance ID to overlay node statuses"),
    lang: Optional[str] = Query(None, description="Optional language code for localized workspace labels"),
) -> dict[str, Any]:
    try:
        workspace = get_flow_spine_workspace(process_key, lang)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown flow spine process '{process_key}'") from exc

    if instance_id:
        instance = _instances.get(instance_id)
        if instance and instance.get("process_key") == process_key:
            workspace = merge_instance_statuses(workspace, instance)

    return workspace


# ── Instance CRUD ─────────────────────────────────────────────────────────────

@router.post("/{process_key}/instances", status_code=201, response_model=dict)
def create_instance(process_key: str, body: InstanceCreateRequest) -> dict[str, Any]:
    """Create a new flow spine instance for tracking a specific document/case through a process."""
    # Validate process_key exists
    try:
        get_flow_spine_workspace(process_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown flow spine process '{process_key}'") from exc

    instance_id = str(uuid.uuid4())
    instance: dict[str, Any] = {
        "instance_id": instance_id,
        "process_key": process_key,
        "label": body.label,
        "linked_document_id": body.linked_document_id,
        "linked_document_type": body.linked_document_type,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
        "node_statuses": {},
        "active_node_id": None,
    }
    _instances[instance_id] = instance
    return instance


@router.get("/{process_key}/instances", response_model=dict)
def list_instances(process_key: str) -> dict[str, Any]:
    """List all instances for a given process_key."""
    items = [
        inst for inst in _instances.values()
        if inst["process_key"] == process_key
    ]
    return {"process_key": process_key, "total": len(items), "instances": items}


@router.get("/{process_key}/instances/{instance_id}", response_model=dict)
def get_instance(process_key: str, instance_id: str) -> dict[str, Any]:
    """Return a single instance with full data."""
    instance = _instances.get(instance_id)
    if not instance or instance["process_key"] != process_key:
        raise HTTPException(
            status_code=404,
            detail=f"Instance '{instance_id}' not found for process '{process_key}'",
        )
    return instance


@router.post("/{process_key}/instances/{instance_id}/transitions", response_model=dict)
def transition_instance(
    process_key: str, instance_id: str, body: TransitionRequest
) -> dict[str, Any]:
    """Update a node's status in the instance, recording the transition."""
    instance = _instances.get(instance_id)
    if not instance or instance["process_key"] != process_key:
        raise HTTPException(
            status_code=404,
            detail=f"Instance '{instance_id}' not found for process '{process_key}'",
        )

    valid_statuses = {"ok", "active", "pending", "warning", "error"}
    if body.new_status not in valid_statuses:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid new_status '{body.new_status}'. Must be one of {sorted(valid_statuses)}.",
        )

    instance["node_statuses"][body.node_id] = body.new_status
    instance["active_node_id"] = body.node_id
    instance["updated_at"] = _utcnow()
    if body.user_id:
        instance["last_actor"] = body.user_id
    instance["last_action_label"] = body.action_label

    return instance


@router.delete("/{process_key}/instances/{instance_id}", status_code=204)
def delete_instance(process_key: str, instance_id: str) -> Response:
    """Remove an instance from the store."""
    instance = _instances.get(instance_id)
    if not instance or instance["process_key"] != process_key:
        raise HTTPException(
            status_code=404,
            detail=f"Instance '{instance_id}' not found for process '{process_key}'",
        )
    del _instances[instance_id]
    return Response(status_code=204)
