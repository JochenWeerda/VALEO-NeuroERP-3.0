from __future__ import annotations

import hashlib
import json as _json
import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant_context import get_current_tenant_id
from app.core.flow_spine_registry import (
    get_flow_spine_catalog,
    get_flow_spine_workspace,
    merge_instance_statuses,
)
from app.domains.operations.models import FlowSpineInstance
from app.services.numbering_service import get_numbering


router = APIRouter(prefix="/process/flow-spines", tags=["process", "flow-spines"])


def _utcnow() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _instance_to_dict(inst: FlowSpineInstance) -> dict[str, Any]:
    partner_name = inst.customer_name
    return {
        "instance_id": inst.id,
        "case_number": inst.case_number,
        "process_key": inst.process_key,
        "label": inst.label,
        "customer_id": inst.customer_id,
        "customer_name": inst.customer_name,
        "partner_name": partner_name,
        "subject": inst.subject,
        "entry_mode": inst.entry_mode,
        "linked_document_id": inst.linked_document_id,
        "linked_document_type": inst.linked_document_type,
        "node_statuses": inst.node_statuses or {},
        "active_node_id": inst.active_node_id,
        "last_actor": inst.last_actor,
        "last_action_label": inst.last_action_label,
        "tenant_id": inst.tenant_id,
        "created_at": inst.created_at.isoformat() if inst.created_at else None,
        "updated_at": inst.updated_at.isoformat() if inst.updated_at else None,
    }


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class InstanceCreateRequest(BaseModel):
    label: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    partner_name: Optional[str] = None
    subject: Optional[str] = None
    entry_mode: Optional[str] = None
    linked_document_id: Optional[str] = None
    linked_document_type: Optional[str] = None


class TransitionRequest(BaseModel):
    node_id: str
    new_status: str
    action_label: str
    user_id: Optional[str] = None


# ── Catalog ──────────────────────────────────────────────────────────────────

@router.get("/catalog")
def get_catalog(lang: Optional[str] = Query(None)) -> JSONResponse:
    catalog = get_flow_spine_catalog(lang)
    body = _json.dumps(catalog, ensure_ascii=False)
    etag = f'"{hashlib.md5(body.encode()).hexdigest()}"'
    return JSONResponse(
        content=catalog,
        headers={
            "Cache-Control": "public, max-age=300, stale-while-revalidate=600",
            "ETag": etag,
        },
    )


# ── Workspace (with optional instance overlay) ───────────────────────────────

@router.get("/{process_key}")
def get_workspace(
    process_key: str,
    instance_id: Optional[str] = Query(None),
    lang: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        workspace = get_flow_spine_workspace(process_key, lang)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown flow spine process '{process_key}'") from exc

    if instance_id:
        inst = db.get(FlowSpineInstance, instance_id)
        if inst and inst.process_key == process_key:
            workspace = merge_instance_statuses(workspace, _instance_to_dict(inst))
        return JSONResponse(content=workspace)

    body = _json.dumps(workspace, ensure_ascii=False)
    etag = f'"{hashlib.md5(body.encode()).hexdigest()}"'
    return JSONResponse(
        content=workspace,
        headers={
            "Cache-Control": "public, max-age=60, stale-while-revalidate=120",
            "ETag": etag,
        },
    )


# ── Instance CRUD ─────────────────────────────────────────────────────────────

@router.post("/{process_key}/instances", status_code=201, response_model=dict)
def create_instance(
    process_key: str,
    body: InstanceCreateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Create a new flow spine instance for tracking a specific document/case through a process."""
    try:
        get_flow_spine_workspace(process_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown flow spine process '{process_key}'") from exc

    instance_id = str(uuid.uuid4())
    case_number = get_numbering().next_number("workflow_case")
    persisted_partner_name = body.partner_name or body.customer_name
    label = body.label or " ".join(
        part for part in [persisted_partner_name, body.subject] if part
    ).strip()
    if not label:
        label = f"Vorgang {case_number}"

    inst = FlowSpineInstance(
        id=instance_id,
        case_number=case_number,
        process_key=process_key,
        label=label,
        customer_id=body.customer_id,
        customer_name=persisted_partner_name,
        subject=body.subject,
        entry_mode=body.entry_mode,
        linked_document_id=body.linked_document_id,
        linked_document_type=body.linked_document_type,
        node_statuses={},
        tenant_id=get_current_tenant_id(),
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.get("/{process_key}/instances", response_model=dict)
def list_instances(
    process_key: str,
    skip: int = Query(default=0, ge=0, description="Anzahl übersprungener Einträge"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximale Anzahl Einträge"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List instances for a given process_key, tenant-isolated, with pagination."""
    tenant_id = get_current_tenant_id()
    base_q = (
        db.query(FlowSpineInstance)
        .filter(
            FlowSpineInstance.process_key == process_key,
            FlowSpineInstance.tenant_id == tenant_id,
        )
        .order_by(FlowSpineInstance.created_at.desc())
    )
    total = base_q.count()
    items = base_q.offset(skip).limit(limit).all()
    return {
        "process_key": process_key,
        "tenant_id": tenant_id,
        "total": total,
        "skip": skip,
        "limit": limit,
        "instances": [_instance_to_dict(i) for i in items],
    }


@router.get("/{process_key}/instances/{instance_id}", response_model=dict)
def get_instance(
    process_key: str,
    instance_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return a single instance with full data."""
    inst = db.get(FlowSpineInstance, instance_id)
    if not inst or inst.process_key != process_key:
        raise HTTPException(
            status_code=404,
            detail=f"Instance '{instance_id}' not found for process '{process_key}'",
        )
    return _instance_to_dict(inst)


@router.post("/{process_key}/instances/{instance_id}/transitions", response_model=dict)
def transition_instance(
    process_key: str,
    instance_id: str,
    body: TransitionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Update a node's status in the instance, recording the transition."""
    inst = db.get(FlowSpineInstance, instance_id)
    if not inst or inst.process_key != process_key:
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

    statuses = dict(inst.node_statuses or {})
    statuses[body.node_id] = body.new_status
    inst.node_statuses = statuses
    inst.active_node_id = body.node_id
    if body.user_id:
        inst.last_actor = body.user_id
    inst.last_action_label = body.action_label
    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.delete("/{process_key}/instances/{instance_id}", status_code=204)
def delete_instance(
    process_key: str,
    instance_id: str,
    db: Session = Depends(get_db),
) -> Response:
    """Remove an instance from the store."""
    inst = db.get(FlowSpineInstance, instance_id)
    if not inst or inst.process_key != process_key:
        raise HTTPException(
            status_code=404,
            detail=f"Instance '{instance_id}' not found for process '{process_key}'",
        )
    db.delete(inst)
    db.commit()
    return Response(status_code=204)
