"""Workflow cockpit API.

Operational visibility for process instances, external blockers and replay
requests. The API is an auditable cockpit projection, not a workflow engine.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.tenant import get_tenant_id
from app.services.workflow_cockpit_service import (
    WorkflowCockpitBlocker,
    WorkflowCockpitEvent,
    WorkflowCockpitStatus,
    WorkflowEventKind,
    WorkflowProcessNotFoundError,
    WorkflowReplayPermissionError,
    workflow_cockpit_service,
)


router = APIRouter(prefix="/workflow/cockpit", tags=["workflow", "cockpit"])


class WorkflowCockpitEventIn(BaseModel):
    kind: WorkflowEventKind = WorkflowEventKind.DOMAIN_EVENT
    message: str
    occurred_at: datetime | None = None
    source: str = "external"
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkflowCockpitBlockerIn(BaseModel):
    blocker_type: str = "external_gate"
    message: str
    external_system: str | None = None
    retryable: bool = True
    resolved: bool = False


class WorkflowCockpitSnapshotIn(BaseModel):
    process_instance_id: str
    process_key: str
    status: WorkflowCockpitStatus
    correlation_id: str
    idempotency_key: str | None = None
    business_object_ref: str | None = None
    current_step: str | None = None
    audit_ref: str | None = None
    events: list[WorkflowCockpitEventIn] = Field(default_factory=list)
    blockers: list[WorkflowCockpitBlockerIn] = Field(default_factory=list)


class WorkflowReplayRequestIn(BaseModel):
    requested_by: str
    reason: str


class WorkflowCockpitEventOut(BaseModel):
    event_id: str
    kind: str
    message: str
    occurred_at: str
    source: str
    payload: dict[str, Any]


class WorkflowCockpitBlockerOut(BaseModel):
    blocker_id: str
    blocker_type: str
    message: str
    external_system: str | None
    since: str
    retryable: bool
    resolved: bool


class WorkflowCockpitProcessOut(BaseModel):
    process_instance_id: str
    tenant_id: str
    process_key: str
    status: str
    correlation_id: str
    idempotency_key: str | None
    business_object_ref: str | None
    current_step: str | None
    created_at: str
    updated_at: str
    audit_ref: str | None
    active_blocker_count: int
    replayable: bool
    blockers: list[WorkflowCockpitBlockerOut]
    events: list[WorkflowCockpitEventOut]


class WorkflowCockpitSummaryOut(BaseModel):
    tenant_id: str
    total_processes: int
    by_status: dict[str, int]
    blocked_external_gate: int
    replayable: int


class WorkflowStatusModelOut(BaseModel):
    statuses: list[str]
    terminal_statuses: list[str]
    replayable_statuses: list[str]
    external_blocker_status: str


def _roles_from_header(x_valeo_roles: str | None = Header(default=None, alias="X-VALEO-Roles")) -> set[str]:
    if not x_valeo_roles:
        return set()
    return {role.strip() for role in x_valeo_roles.split(",") if role.strip()}


@router.get(
    "/status-model",
    summary="Workflow-Cockpit Statusmodell abrufen",
    response_model=WorkflowStatusModelOut,
)
async def get_status_model() -> dict[str, Any]:
    return {
        "statuses": [status.value for status in WorkflowCockpitStatus],
        "terminal_statuses": ["completed", "compensated"],
        "replayable_statuses": ["blocked_external_gate", "failed"],
        "external_blocker_status": "blocked_external_gate",
    }


@router.get(
    "/summary",
    summary="Workflow-Cockpit Zusammenfassung abrufen",
    response_model=WorkflowCockpitSummaryOut,
)
async def get_summary(tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return workflow_cockpit_service.summary(tenant_id=tenant_id)


@router.get(
    "/processes",
    summary="Workflow-Prozessinstanzen fuer den Tenant listen",
    response_model=list[WorkflowCockpitProcessOut],
)
async def list_processes(
    status: WorkflowCockpitStatus | None = None,
    process_key: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return [
        process.to_dict(include_events=False)
        for process in workflow_cockpit_service.list_processes(
            tenant_id=tenant_id,
            status=status,
            process_key=process_key,
        )
    ]


@router.post(
    "/processes",
    summary="Workflow-Prozesssnapshot fuer Cockpit melden",
    response_model=WorkflowCockpitProcessOut,
)
async def upsert_process(
    request: WorkflowCockpitSnapshotIn,
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    events = [
        WorkflowCockpitEvent(
            event_id=f"evt-{idx}",
            kind=item.kind,
            message=item.message,
            occurred_at=item.occurred_at or datetime.now().astimezone(),
            source=item.source,
            payload=item.payload,
        )
        for idx, item in enumerate(request.events, start=1)
    ]
    blockers = [
        WorkflowCockpitBlocker(
            blocker_id=f"blk-{idx}",
            blocker_type=item.blocker_type,
            message=item.message,
            external_system=item.external_system,
            retryable=item.retryable,
            resolved=item.resolved,
        )
        for idx, item in enumerate(request.blockers, start=1)
    ]
    process = workflow_cockpit_service.upsert_process(
        tenant_id=tenant_id,
        process_instance_id=request.process_instance_id,
        process_key=request.process_key,
        status=request.status,
        correlation_id=request.correlation_id,
        idempotency_key=request.idempotency_key,
        business_object_ref=request.business_object_ref,
        current_step=request.current_step,
        audit_ref=request.audit_ref,
        events=events,
        blockers=blockers,
    )
    return process.to_dict()


@router.get(
    "/processes/{process_instance_id}",
    summary="Workflow-Prozessinstanz mit Event-Kette abrufen",
    response_model=WorkflowCockpitProcessOut,
)
async def get_process(
    process_instance_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return workflow_cockpit_service.get_process(
            tenant_id=tenant_id,
            process_instance_id=process_instance_id,
        ).to_dict()
    except WorkflowProcessNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Process instance not found") from exc


@router.post(
    "/processes/{process_instance_id}/replay-requests",
    summary="Replay-Anforderung fuer Workflow-Prozessinstanz auditieren",
    response_model=WorkflowCockpitEventOut,
)
async def request_replay(
    process_instance_id: str,
    request: WorkflowReplayRequestIn,
    roles: set[str] = Depends(_roles_from_header),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        event = workflow_cockpit_service.request_replay(
            tenant_id=tenant_id,
            process_instance_id=process_instance_id,
            requested_by=request.requested_by,
            roles=roles,
            reason=request.reason,
        )
    except WorkflowProcessNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Process instance not found") from exc
    except WorkflowReplayPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return event.to_dict()
