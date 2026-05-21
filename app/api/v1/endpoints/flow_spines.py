from __future__ import annotations

import hashlib
import json as _json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant_context import get_current_tenant_id
from app.core.flow_spine_registry import (
    get_flow_spine_catalog,
    get_flow_spine_workspace,
    merge_instance_statuses,
)
from sqlalchemy import or_
from app.domains.operations.models import FlowSpineInstance, FlowSpineInstanceEvent
from app.infrastructure.models import BusinessPartner, Customer
from app.domains.shared.events import get_event_publisher
from app.domains.shared.process_events import (
    FlowSpineInstanceCreated,
    FlowSpineTransitionOccurred,
)
from app.infrastructure.eventbus.outbox import OutboxPublisher
from app.services.numbering_service import get_numbering

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/process/flow-spines", tags=["process", "flow-spines"])
LIFECYCLE_STATUSES = {"draft", "in_progress", "on_hold", "completed", "cancelled", "failed"}
REASON_CATEGORIES = {
    "customer",
    "supplier",
    "logistics",
    "quality",
    "finance",
    "compliance",
    "technical",
    "internal",
}


def _utcnow() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _flow_spine_etag(payload: dict[str, Any]) -> str:
    """
    ETag fuer JSON-Responses. SHA-256 statt MD5 — MD5 ist auf manchen Hosts (FIPS/OpenSSL)
    blockiert und konnte bisher einen 500er beim Generieren der ETag-Header ausloesen.
    """
    body = _json.dumps(payload, ensure_ascii=False)
    return f'"{hashlib.sha256(body.encode("utf-8")).hexdigest()}"'


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
        "lifecycle_status": inst.lifecycle_status,
        "business_status": inst.business_status,
        "node_statuses": inst.node_statuses or {},
        "active_node_id": inst.active_node_id,
        "resume_node_id": inst.resume_node_id,
        "resume_route": inst.resume_route,
        "resume_payload": inst.resume_payload or {},
        "assigned_owner": inst.assigned_owner,
        "last_actor": inst.last_actor,
        "last_action_label": inst.last_action_label,
        "last_activity_at": inst.last_activity_at.isoformat() if inst.last_activity_at else None,
        "blocked_until": inst.blocked_until.isoformat() if inst.blocked_until else None,
        "completion_reason_code": inst.completion_reason_code,
        "cancellation_reason_category": inst.cancellation_reason_category,
        "cancellation_reason_code": inst.cancellation_reason_code,
        "failure_reason_category": inst.failure_reason_category,
        "failure_reason_code": inst.failure_reason_code,
        "reason_note": inst.reason_note,
        "closed_at": inst.closed_at.isoformat() if inst.closed_at else None,
        "closed_by": inst.closed_by,
        "cancelled_at": inst.cancelled_at.isoformat() if inst.cancelled_at else None,
        "cancelled_by": inst.cancelled_by,
        "failed_at": inst.failed_at.isoformat() if inst.failed_at else None,
        "failed_by": inst.failed_by,
        "version_no": inst.version_no,
        "tenant_id": inst.tenant_id,
        "created_at": inst.created_at.isoformat() if inst.created_at else None,
        "updated_at": inst.updated_at.isoformat() if inst.updated_at else None,
    }


def _event_to_dict(event: FlowSpineInstanceEvent) -> dict[str, Any]:
    return {
        "event_id": event.id,
        "instance_id": event.instance_id,
        "process_key": event.process_key,
        "tenant_id": event.tenant_id,
        "event_type": event.event_type,
        "from_lifecycle_status": event.from_lifecycle_status,
        "to_lifecycle_status": event.to_lifecycle_status,
        "from_business_status": event.from_business_status,
        "to_business_status": event.to_business_status,
        "node_id": event.node_id,
        "actor_id": event.actor_id,
        "reason_category": event.reason_category,
        "reason_code": event.reason_code,
        "reason_note": event.reason_note,
        "payload": event.payload or {},
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def _get_instance_or_404(db: Session, process_key: str, instance_id: str) -> FlowSpineInstance:
    tenant_id = get_current_tenant_id()
    inst = db.get(FlowSpineInstance, instance_id)
    if not inst or inst.process_key != process_key or inst.tenant_id != tenant_id:
        raise HTTPException(
            status_code=404,
            detail=f"Instance '{instance_id}' not found for process '{process_key}'",
        )
    return inst


def _parse_datetime(value: str | None, field_name: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid datetime for '{field_name}'.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _record_instance_event(
    db: Session,
    inst: FlowSpineInstance,
    *,
    event_type: str,
    actor_id: str | None = None,
    node_id: str | None = None,
    reason_category: str | None = None,
    reason_code: str | None = None,
    reason_note: str | None = None,
    payload: dict[str, Any] | None = None,
    from_lifecycle_status: str | None = None,
    to_lifecycle_status: str | None = None,
    from_business_status: str | None = None,
    to_business_status: str | None = None,
) -> None:
    db.add(
        FlowSpineInstanceEvent(
            instance_id=inst.id,
            process_key=inst.process_key,
            tenant_id=inst.tenant_id,
            event_type=event_type,
            from_lifecycle_status=from_lifecycle_status,
            to_lifecycle_status=to_lifecycle_status,
            from_business_status=from_business_status,
            to_business_status=to_business_status,
            node_id=node_id,
            actor_id=actor_id,
            reason_category=reason_category,
            reason_code=reason_code,
            reason_note=reason_note,
            payload=payload or {},
        )
    )


def _touch_instance(inst: FlowSpineInstance, *, actor_id: str | None = None, action_label: str | None = None) -> None:
    inst.last_activity_at = datetime.now(UTC)
    inst.version_no = (inst.version_no or 0) + 1
    if actor_id:
        inst.last_actor = actor_id
    if action_label:
        inst.last_action_label = action_label


def _resolve_customer_data(db: Session, tenant_id: str, customer_id: str) -> dict[str, Any] | None:
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.tenant_id == tenant_id,
        )
        .first()
    )
    partner_id = customer.business_partner_id if customer and customer.business_partner_id else customer_id
    bp = (
        db.query(BusinessPartner)
        .filter(
            BusinessPartner.partner_id == partner_id,
            BusinessPartner.tenant_id == tenant_id,
        )
        .first()
    )
    if not bp:
        return None
    return {
        "partner_id": bp.partner_id,
        "partner_number": bp.partner_number,
        "name_1": bp.name_1,
        "name_2": bp.name_2,
        "street": bp.street,
        "house_number": bp.house_number,
        "postal_code": bp.postal_code,
        "city": bp.city,
        "country": bp.country,
        "phone": bp.phone,
        "email": bp.email,
        "debtor_account": bp.debtor_account,
        "creditor_account": bp.creditor_account,
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


class AgentActionRequest(BaseModel):
    action: str
    node_id: Optional[str] = None
    instance_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class InstanceUpdateRequest(BaseModel):
    label: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    partner_name: Optional[str] = None
    subject: Optional[str] = None
    entry_mode: Optional[str] = None
    linked_document_id: Optional[str] = None
    linked_document_type: Optional[str] = None
    business_status: Optional[str] = None
    assigned_owner: Optional[str] = None
    resume_node_id: Optional[str] = None
    resume_route: Optional[str] = None
    resume_payload: Optional[dict[str, Any]] = None
    user_id: Optional[str] = None


class InstanceSaveRequest(BaseModel):
    resume_node_id: Optional[str] = None
    resume_route: Optional[str] = None
    resume_payload: dict[str, Any] = Field(default_factory=dict)
    business_status: Optional[str] = None
    assigned_owner: Optional[str] = None
    action_label: Optional[str] = None
    note: Optional[str] = None
    user_id: Optional[str] = None


class LifecycleActionRequest(BaseModel):
    business_status: Optional[str] = None
    node_id: Optional[str] = None
    assigned_owner: Optional[str] = None
    action_label: Optional[str] = None
    reason_category: Optional[str] = None
    reason_code: Optional[str] = None
    reason_note: Optional[str] = None
    blocked_until: Optional[str] = None
    user_id: Optional[str] = None


class ResumeRequest(BaseModel):
    user_id: Optional[str] = None
    action_label: Optional[str] = None


# ── Catalog ──────────────────────────────────────────────────────────────────

@router.get("/catalog")
def get_catalog(lang: Optional[str] = Query(None)) -> JSONResponse:
    catalog = get_flow_spine_catalog(lang)
    etag = _flow_spine_etag(catalog)
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
    tenant_id = get_current_tenant_id()
    try:
        workspace = get_flow_spine_workspace(process_key, lang)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown flow spine process '{process_key}'") from exc

    if instance_id:
        inst = db.get(FlowSpineInstance, instance_id)
        if inst and inst.process_key == process_key and inst.tenant_id == tenant_id:
            workspace = merge_instance_statuses(workspace, _instance_to_dict(inst))
            if inst.customer_id:
                customer_data = _resolve_customer_data(db, inst.tenant_id, inst.customer_id)
                if customer_data:
                    workspace["customer_data"] = customer_data
        return JSONResponse(content=workspace)

    etag = _flow_spine_etag(workspace)
    return JSONResponse(
        content=workspace,
        headers={
            "Cache-Control": "public, max-age=60, stale-while-revalidate=120",
            "ETag": etag,
        },
    )


# ── Instance CRUD ─────────────────────────────────────────────────────────────

@router.post("/{process_key}/instances", status_code=201, response_model=dict)
async def create_instance(
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

    tenant_id = get_current_tenant_id()
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
        lifecycle_status="draft",
        node_statuses={},
        resume_payload={},
        version_no=1,
        tenant_id=tenant_id,
    )
    db.add(inst)
    _record_instance_event(
        db,
        inst,
        event_type="created",
        to_lifecycle_status=inst.lifecycle_status,
        payload={
            "case_number": case_number,
            "entry_mode": body.entry_mode,
            "linked_document_type": body.linked_document_type,
        },
    )

    try:
        event = FlowSpineInstanceCreated(
            aggregate_id=instance_id,
            tenant_id=tenant_id,
            instance_id=instance_id,
            process_key=process_key,
            case_number=case_number,
            label=label,
            entry_mode=body.entry_mode,
            linked_document_type=body.linked_document_type,
        )
        await OutboxPublisher(db, get_event_publisher()).store_event(event, tenant_id)
    except Exception:
        logger.warning("Outbox unavailable — FlowSpineInstanceCreated not stored", exc_info=True)

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.get("/{process_key}/instances", response_model=dict)
def list_instances(
    process_key: str,
    skip: int = Query(default=0, ge=0, description="Anzahl übersprungener Einträge"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximale Anzahl Einträge"),
    search: Optional[str] = Query(None, description="Suche in Vorgangsnummer, Kundenname, Bezeichnung"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List instances for a given process_key, tenant-isolated, with pagination and search."""
    tenant_id = get_current_tenant_id()
    base_q = (
        db.query(FlowSpineInstance)
        .filter(
            FlowSpineInstance.process_key == process_key,
            FlowSpineInstance.tenant_id == tenant_id,
        )
        .order_by(FlowSpineInstance.created_at.desc())
    )
    if search:
        s = f"%{search}%"
        base_q = base_q.filter(
            or_(
                FlowSpineInstance.case_number.ilike(s),
                FlowSpineInstance.customer_name.ilike(s),
                FlowSpineInstance.label.ilike(s),
                FlowSpineInstance.subject.ilike(s),
            )
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
    inst = _get_instance_or_404(db, process_key, instance_id)
    return _instance_to_dict(inst)


@router.patch("/{process_key}/instances/{instance_id}", response_model=dict)
def update_instance(
    process_key: str,
    instance_id: str,
    body: InstanceUpdateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    inst = _get_instance_or_404(db, process_key, instance_id)
    previous_business_status = inst.business_status
    previous_owner = inst.assigned_owner
    persisted_partner_name = body.partner_name or body.customer_name

    if body.label is not None:
        inst.label = body.label.strip() or inst.label
    if body.customer_id is not None:
        inst.customer_id = body.customer_id
    if persisted_partner_name is not None:
        inst.customer_name = persisted_partner_name
    if body.subject is not None:
        inst.subject = body.subject
    if body.entry_mode is not None:
        inst.entry_mode = body.entry_mode
    if body.linked_document_id is not None:
        inst.linked_document_id = body.linked_document_id
    if body.linked_document_type is not None:
        inst.linked_document_type = body.linked_document_type
    if body.business_status is not None:
        inst.business_status = body.business_status
    if body.assigned_owner is not None:
        inst.assigned_owner = body.assigned_owner
    if body.resume_node_id is not None:
        inst.resume_node_id = body.resume_node_id
    if body.resume_route is not None:
        inst.resume_route = body.resume_route
    if body.resume_payload is not None:
        inst.resume_payload = body.resume_payload

    _touch_instance(inst, actor_id=body.user_id, action_label="Instanz aktualisiert")
    _record_instance_event(
        db,
        inst,
        event_type="metadata_updated",
        actor_id=body.user_id,
        from_business_status=previous_business_status,
        to_business_status=inst.business_status,
        payload={
            "assigned_owner_before": previous_owner,
            "assigned_owner_after": inst.assigned_owner,
            "resume_node_id": inst.resume_node_id,
            "resume_route": inst.resume_route,
        },
    )

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.post("/{process_key}/instances/{instance_id}/save", response_model=dict)
def save_instance(
    process_key: str,
    instance_id: str,
    body: InstanceSaveRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    inst = _get_instance_or_404(db, process_key, instance_id)
    from_lifecycle_status = inst.lifecycle_status
    from_business_status = inst.business_status

    if body.resume_node_id is not None:
        inst.resume_node_id = body.resume_node_id
        inst.active_node_id = body.resume_node_id
    if body.resume_route is not None:
        inst.resume_route = body.resume_route
    if body.resume_payload:
        inst.resume_payload = body.resume_payload
    if body.business_status is not None:
        inst.business_status = body.business_status
    if body.assigned_owner is not None:
        inst.assigned_owner = body.assigned_owner
    if inst.lifecycle_status == "draft":
        inst.lifecycle_status = "in_progress"

    _touch_instance(inst, actor_id=body.user_id, action_label=body.action_label or "Zwischengespeichert")
    _record_instance_event(
        db,
        inst,
        event_type="saved",
        actor_id=body.user_id,
        node_id=inst.resume_node_id,
        reason_note=body.note,
        from_lifecycle_status=from_lifecycle_status,
        to_lifecycle_status=inst.lifecycle_status,
        from_business_status=from_business_status,
        to_business_status=inst.business_status,
        payload={
            "resume_route": inst.resume_route,
            "resume_payload": inst.resume_payload or {},
        },
    )

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.post("/{process_key}/instances/{instance_id}/resume", response_model=dict)
def resume_instance(
    process_key: str,
    instance_id: str,
    body: ResumeRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    inst = _get_instance_or_404(db, process_key, instance_id)
    if inst.lifecycle_status in {"completed", "cancelled", "failed"}:
        raise HTTPException(
            status_code=409,
            detail=f"Instance '{instance_id}' cannot be resumed from lifecycle_status '{inst.lifecycle_status}'",
        )

    from_lifecycle_status = inst.lifecycle_status
    if inst.lifecycle_status in {"draft", "on_hold"}:
        inst.lifecycle_status = "in_progress"

    _touch_instance(inst, actor_id=body.user_id, action_label=body.action_label or "Vorgang wieder aufgenommen")
    _record_instance_event(
        db,
        inst,
        event_type="resumed",
        actor_id=body.user_id,
        node_id=inst.resume_node_id or inst.active_node_id,
        from_lifecycle_status=from_lifecycle_status,
        to_lifecycle_status=inst.lifecycle_status,
        from_business_status=inst.business_status,
        to_business_status=inst.business_status,
        payload={
            "resume_route": inst.resume_route,
            "resume_payload": inst.resume_payload or {},
        },
    )

    db.commit()
    db.refresh(inst)
    return {
        **_instance_to_dict(inst),
        "resume_target": {
            "node_id": inst.resume_node_id or inst.active_node_id,
            "route": inst.resume_route,
            "payload": inst.resume_payload or {},
        },
    }


@router.post("/{process_key}/instances/{instance_id}/hold", response_model=dict)
def hold_instance(
    process_key: str,
    instance_id: str,
    body: LifecycleActionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    inst = _get_instance_or_404(db, process_key, instance_id)
    from_lifecycle_status = inst.lifecycle_status
    from_business_status = inst.business_status
    inst.lifecycle_status = "on_hold"
    if body.business_status is not None:
        inst.business_status = body.business_status
    if body.assigned_owner is not None:
        inst.assigned_owner = body.assigned_owner
    inst.blocked_until = _parse_datetime(body.blocked_until, "blocked_until")

    _touch_instance(inst, actor_id=body.user_id, action_label=body.action_label or "Vorgang pausiert")
    _record_instance_event(
        db,
        inst,
        event_type="hold_set",
        actor_id=body.user_id,
        node_id=body.node_id or inst.active_node_id,
        reason_category=body.reason_category,
        reason_code=body.reason_code,
        reason_note=body.reason_note,
        from_lifecycle_status=from_lifecycle_status,
        to_lifecycle_status=inst.lifecycle_status,
        from_business_status=from_business_status,
        to_business_status=inst.business_status,
        payload={"blocked_until": inst.blocked_until.isoformat() if inst.blocked_until else None},
    )

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.post("/{process_key}/instances/{instance_id}/complete", response_model=dict)
def complete_instance(
    process_key: str,
    instance_id: str,
    body: LifecycleActionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    inst = _get_instance_or_404(db, process_key, instance_id)
    from_lifecycle_status = inst.lifecycle_status
    from_business_status = inst.business_status
    inst.lifecycle_status = "completed"
    if body.business_status is not None:
        inst.business_status = body.business_status
    inst.completion_reason_code = body.reason_code
    inst.reason_note = body.reason_note
    inst.closed_at = datetime.now(UTC)
    inst.closed_by = body.user_id
    inst.blocked_until = None

    _touch_instance(inst, actor_id=body.user_id, action_label=body.action_label or "Vorgang abgeschlossen")
    _record_instance_event(
        db,
        inst,
        event_type="completed",
        actor_id=body.user_id,
        node_id=body.node_id or inst.active_node_id,
        reason_code=body.reason_code,
        reason_note=body.reason_note,
        from_lifecycle_status=from_lifecycle_status,
        to_lifecycle_status=inst.lifecycle_status,
        from_business_status=from_business_status,
        to_business_status=inst.business_status,
    )

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


def _validate_required_reason(body: LifecycleActionRequest) -> None:
    if not body.reason_category or not body.reason_code:
        raise HTTPException(
            status_code=422,
            detail="reason_category and reason_code are required for this lifecycle action.",
        )
    if body.reason_category not in REASON_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid reason_category '{body.reason_category}'. Must be one of {sorted(REASON_CATEGORIES)}.",
        )


@router.post("/{process_key}/instances/{instance_id}/cancel", response_model=dict)
def cancel_instance(
    process_key: str,
    instance_id: str,
    body: LifecycleActionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _validate_required_reason(body)
    inst = _get_instance_or_404(db, process_key, instance_id)
    from_lifecycle_status = inst.lifecycle_status
    from_business_status = inst.business_status
    inst.lifecycle_status = "cancelled"
    if body.business_status is not None:
        inst.business_status = body.business_status
    inst.cancellation_reason_category = body.reason_category
    inst.cancellation_reason_code = body.reason_code
    inst.reason_note = body.reason_note
    inst.cancelled_at = datetime.now(UTC)
    inst.cancelled_by = body.user_id
    inst.blocked_until = None

    _touch_instance(inst, actor_id=body.user_id, action_label=body.action_label or "Vorgang abgebrochen")
    _record_instance_event(
        db,
        inst,
        event_type="cancelled",
        actor_id=body.user_id,
        node_id=body.node_id or inst.active_node_id,
        reason_category=body.reason_category,
        reason_code=body.reason_code,
        reason_note=body.reason_note,
        from_lifecycle_status=from_lifecycle_status,
        to_lifecycle_status=inst.lifecycle_status,
        from_business_status=from_business_status,
        to_business_status=inst.business_status,
    )

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.post("/{process_key}/instances/{instance_id}/fail", response_model=dict)
def fail_instance(
    process_key: str,
    instance_id: str,
    body: LifecycleActionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _validate_required_reason(body)
    inst = _get_instance_or_404(db, process_key, instance_id)
    from_lifecycle_status = inst.lifecycle_status
    from_business_status = inst.business_status
    inst.lifecycle_status = "failed"
    if body.business_status is not None:
        inst.business_status = body.business_status
    inst.failure_reason_category = body.reason_category
    inst.failure_reason_code = body.reason_code
    inst.reason_note = body.reason_note
    inst.failed_at = datetime.now(UTC)
    inst.failed_by = body.user_id
    inst.blocked_until = None

    _touch_instance(inst, actor_id=body.user_id, action_label=body.action_label or "Vorgang gescheitert")
    _record_instance_event(
        db,
        inst,
        event_type="failed",
        actor_id=body.user_id,
        node_id=body.node_id or inst.active_node_id,
        reason_category=body.reason_category,
        reason_code=body.reason_code,
        reason_note=body.reason_note,
        from_lifecycle_status=from_lifecycle_status,
        to_lifecycle_status=inst.lifecycle_status,
        from_business_status=from_business_status,
        to_business_status=inst.business_status,
    )

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.get("/{process_key}/instances/{instance_id}/timeline", response_model=dict)
def get_instance_timeline(
    process_key: str,
    instance_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    inst = _get_instance_or_404(db, process_key, instance_id)
    events = (
        db.query(FlowSpineInstanceEvent)
        .filter(
            FlowSpineInstanceEvent.instance_id == instance_id,
            FlowSpineInstanceEvent.process_key == process_key,
            FlowSpineInstanceEvent.tenant_id == inst.tenant_id,
        )
        .order_by(FlowSpineInstanceEvent.created_at.asc(), FlowSpineInstanceEvent.id.asc())
        .all()
    )
    return {
        "instance_id": instance_id,
        "process_key": process_key,
        "tenant_id": inst.tenant_id,
        "events": [_event_to_dict(event) for event in events],
    }


@router.post("/{process_key}/instances/{instance_id}/transitions", response_model=dict)
async def transition_instance(
    process_key: str,
    instance_id: str,
    body: TransitionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Update a node's status in the instance, recording the transition."""
    inst = _get_instance_or_404(db, process_key, instance_id)

    valid_statuses = {"ok", "active", "pending", "warning", "error"}
    if body.new_status not in valid_statuses:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid new_status '{body.new_status}'. Must be one of {sorted(valid_statuses)}.",
        )

    statuses = dict(inst.node_statuses or {})
    previous_lifecycle_status = inst.lifecycle_status
    previous_business_status = inst.business_status
    statuses[body.node_id] = body.new_status
    inst.node_statuses = statuses
    inst.active_node_id = body.node_id
    inst.resume_node_id = body.node_id
    if inst.lifecycle_status == "draft":
        inst.lifecycle_status = "in_progress"
    if body.user_id:
        inst.last_actor = body.user_id
    inst.last_action_label = body.action_label
    _touch_instance(inst, actor_id=body.user_id, action_label=body.action_label)
    _record_instance_event(
        db,
        inst,
        event_type="node_transition",
        actor_id=body.user_id,
        node_id=body.node_id,
        payload={"new_status": body.new_status, "action_label": body.action_label},
        from_lifecycle_status=previous_lifecycle_status,
        to_lifecycle_status=inst.lifecycle_status,
        from_business_status=previous_business_status,
        to_business_status=inst.business_status,
    )

    try:
        event = FlowSpineTransitionOccurred(
            aggregate_id=instance_id,
            tenant_id=inst.tenant_id,
            instance_id=instance_id,
            process_key=process_key,
            node_id=body.node_id,
            new_status=body.new_status,
            action_label=body.action_label,
            actor_id=body.user_id,
        )
        await OutboxPublisher(db, get_event_publisher()).store_event(event, inst.tenant_id)
    except Exception:
        logger.warning("Outbox unavailable — FlowSpineTransitionOccurred not stored", exc_info=True)

    db.commit()
    db.refresh(inst)
    return _instance_to_dict(inst)


@router.delete("/{process_key}/instances/{instance_id}", status_code=204, response_class=Response)
def delete_instance(
    process_key: str,
    instance_id: str,
    db: Session = Depends(get_db),
) -> Response:
    """Remove an instance from the store."""
    inst = _get_instance_or_404(db, process_key, instance_id)
    db.delete(inst)
    db.commit()
    return Response(status_code=204)


# ── Agent Action (GAP-104-H) ──────────────────────────────────────────────────

@router.post("/{process_key}/agent-action", response_model=dict)
async def execute_agent_action(
    process_key: str,
    body: AgentActionRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Execute an agent action for a flow spine process, optionally enriched with RAG context.

    Falls back gracefully if the vector store (ChromaDB) is not available.
    """
    try:
        workspace = get_flow_spine_workspace(process_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown flow spine process '{process_key}'") from exc

    # Optional instance context
    instance_data: dict[str, Any] | None = None
    if body.instance_id:
        inst = db.get(FlowSpineInstance, body.instance_id)
        if inst and inst.process_key == process_key:
            instance_data = _instance_to_dict(inst)

    # RAG enrichment — graceful degradation if ChromaDB is unavailable
    rag_hits: list[dict[str, Any]] = []
    try:
        import chromadb  # type: ignore  # noqa: F401
        from app.infrastructure.rag.client import get_rag_collection

        collection = get_rag_collection()
        results = collection.query(
            query_texts=[body.action],
            n_results=3,
            where={"process_key": process_key} if collection.count() > 0 else None,
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        rag_hits = [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(docs, metas)
            if doc
        ]
    except Exception:
        logger.debug("RAG not available — agent action proceeds without knowledge enrichment")

    # Build response payload
    response: dict[str, Any] = {
        "process_key": process_key,
        "action": body.action,
        "node_id": body.node_id,
        "instance_id": body.instance_id,
        "executed_at": _utcnow(),
        "status": "accepted",
        "rag_hits": rag_hits,
        "workspace_title": workspace.get("title", process_key),
    }
    if instance_data:
        response["instance"] = {
            "case_number": instance_data["case_number"],
            "label": instance_data["label"],
            "active_node_id": instance_data["active_node_id"],
            "node_statuses": instance_data["node_statuses"],
        }

    logger.info(
        "Agent action '%s' accepted for process '%s' (instance=%s, rag_hits=%d)",
        body.action,
        process_key,
        body.instance_id,
        len(rag_hits),
    )
    return response
