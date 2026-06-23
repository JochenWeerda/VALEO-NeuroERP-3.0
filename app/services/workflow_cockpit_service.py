"""Workflow cockpit service for operational process visibility.

The cockpit is deliberately read-heavy. It does not replace the process
kernel, domain services or outbox/NATS. It keeps normalized process snapshots
so operators can see status, blockers, events and replay eligibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class WorkflowCockpitStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED_EXTERNAL_GATE = "blocked_external_gate"
    FAILED = "failed"
    COMPLETED = "completed"
    COMPENSATED = "compensated"


class WorkflowEventKind(str, Enum):
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    DOMAIN_EVENT = "domain_event"
    EXTERNAL_GATE = "external_gate"
    RETRY_REQUESTED = "retry_requested"
    REPLAY_REQUESTED = "replay_requested"
    AUDIT = "audit"


TERMINAL_STATUSES = {
    WorkflowCockpitStatus.COMPLETED,
    WorkflowCockpitStatus.COMPENSATED,
}

REPLAYABLE_STATUSES = {
    WorkflowCockpitStatus.BLOCKED_EXTERNAL_GATE,
    WorkflowCockpitStatus.FAILED,
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class WorkflowCockpitEvent:
    event_id: str
    kind: WorkflowEventKind
    message: str
    occurred_at: datetime = field(default_factory=_utcnow)
    source: str = "workflow-cockpit"
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "kind": self.kind.value,
            "message": self.message,
            "occurred_at": self.occurred_at.isoformat(),
            "source": self.source,
            "payload": self.payload,
        }


@dataclass(slots=True)
class WorkflowCockpitBlocker:
    blocker_id: str
    blocker_type: str
    message: str
    external_system: str | None = None
    since: datetime = field(default_factory=_utcnow)
    retryable: bool = True
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocker_id": self.blocker_id,
            "blocker_type": self.blocker_type,
            "message": self.message,
            "external_system": self.external_system,
            "since": self.since.isoformat(),
            "retryable": self.retryable,
            "resolved": self.resolved,
        }


@dataclass(slots=True)
class WorkflowCockpitProcess:
    process_instance_id: str
    tenant_id: str
    process_key: str
    status: WorkflowCockpitStatus
    correlation_id: str
    idempotency_key: str | None = None
    business_object_ref: str | None = None
    current_step: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    events: list[WorkflowCockpitEvent] = field(default_factory=list)
    blockers: list[WorkflowCockpitBlocker] = field(default_factory=list)
    audit_ref: str | None = None

    @property
    def active_blockers(self) -> list[WorkflowCockpitBlocker]:
        return [blocker for blocker in self.blockers if not blocker.resolved]

    @property
    def replayable(self) -> bool:
        if self.status not in REPLAYABLE_STATUSES:
            return False
        return any(blocker.retryable for blocker in self.active_blockers) or self.status == WorkflowCockpitStatus.FAILED

    def to_dict(self, include_events: bool = True) -> dict[str, Any]:
        events = sorted(self.events, key=lambda item: item.occurred_at)
        return {
            "process_instance_id": self.process_instance_id,
            "tenant_id": self.tenant_id,
            "process_key": self.process_key,
            "status": self.status.value,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "business_object_ref": self.business_object_ref,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "audit_ref": self.audit_ref,
            "active_blocker_count": len(self.active_blockers),
            "replayable": self.replayable,
            "blockers": [blocker.to_dict() for blocker in self.blockers],
            "events": [event.to_dict() for event in events] if include_events else [],
        }


class WorkflowReplayPermissionError(PermissionError):
    """Raised when a replay request is attempted without workflow:replay."""


class WorkflowProcessNotFoundError(LookupError):
    """Raised when a process instance is not visible for the given tenant."""


class WorkflowCockpitService:
    """In-memory cockpit projection with tenant-safe read and replay guards."""

    def __init__(self) -> None:
        self._processes: dict[tuple[str, str], WorkflowCockpitProcess] = {}

    def reset(self) -> None:
        self._processes.clear()

    def upsert_process(
        self,
        *,
        tenant_id: str,
        process_instance_id: str,
        process_key: str,
        status: WorkflowCockpitStatus | str,
        correlation_id: str,
        idempotency_key: str | None = None,
        business_object_ref: str | None = None,
        current_step: str | None = None,
        audit_ref: str | None = None,
        events: list[WorkflowCockpitEvent] | None = None,
        blockers: list[WorkflowCockpitBlocker] | None = None,
    ) -> WorkflowCockpitProcess:
        status_value = WorkflowCockpitStatus(status)
        key = (tenant_id, process_instance_id)
        existing = self._processes.get(key)
        now = _utcnow()
        if existing is None:
            existing = WorkflowCockpitProcess(
                process_instance_id=process_instance_id,
                tenant_id=tenant_id,
                process_key=process_key,
                status=status_value,
                correlation_id=correlation_id,
                idempotency_key=idempotency_key,
                business_object_ref=business_object_ref,
                current_step=current_step,
                audit_ref=audit_ref,
                events=[
                    WorkflowCockpitEvent(
                        event_id=str(uuid4()),
                        kind=WorkflowEventKind.CREATED,
                        message="Process snapshot created",
                        occurred_at=now,
                    )
                ],
            )
            self._processes[key] = existing
        else:
            if existing.status != status_value:
                existing.events.append(
                    WorkflowCockpitEvent(
                        event_id=str(uuid4()),
                        kind=WorkflowEventKind.STATUS_CHANGED,
                        message=f"Status changed from {existing.status.value} to {status_value.value}",
                        occurred_at=now,
                    )
                )
            existing.process_key = process_key
            existing.status = status_value
            existing.correlation_id = correlation_id
            existing.idempotency_key = idempotency_key
            existing.business_object_ref = business_object_ref
            existing.current_step = current_step
            existing.audit_ref = audit_ref
            existing.updated_at = now

        if events:
            existing.events.extend(events)
        if blockers:
            existing.blockers.extend(blockers)
            if status_value != WorkflowCockpitStatus.BLOCKED_EXTERNAL_GATE:
                existing.events.append(
                    WorkflowCockpitEvent(
                        event_id=str(uuid4()),
                        kind=WorkflowEventKind.EXTERNAL_GATE,
                        message="External blocker recorded without blocked status",
                    )
                )
        existing.events.sort(key=lambda item: item.occurred_at)
        return existing

    def list_processes(
        self,
        *,
        tenant_id: str,
        status: WorkflowCockpitStatus | str | None = None,
        process_key: str | None = None,
    ) -> list[WorkflowCockpitProcess]:
        status_value = WorkflowCockpitStatus(status) if status else None
        result = [
            process
            for (process_tenant, _), process in self._processes.items()
            if process_tenant == tenant_id
        ]
        if status_value is not None:
            result = [process for process in result if process.status == status_value]
        if process_key is not None:
            result = [process for process in result if process.process_key == process_key]
        return sorted(result, key=lambda item: item.updated_at, reverse=True)

    def get_process(self, *, tenant_id: str, process_instance_id: str) -> WorkflowCockpitProcess:
        process = self._processes.get((tenant_id, process_instance_id))
        if process is None:
            raise WorkflowProcessNotFoundError(process_instance_id)
        return process

    def request_replay(
        self,
        *,
        tenant_id: str,
        process_instance_id: str,
        requested_by: str,
        roles: set[str],
        reason: str,
    ) -> WorkflowCockpitEvent:
        process = self.get_process(tenant_id=tenant_id, process_instance_id=process_instance_id)
        if "workflow:replay" not in roles:
            raise WorkflowReplayPermissionError("workflow:replay role required")
        if not process.replayable:
            raise ValueError(f"Process status {process.status.value} is not replayable")
        event = WorkflowCockpitEvent(
            event_id=str(uuid4()),
            kind=WorkflowEventKind.REPLAY_REQUESTED,
            message=f"Replay requested by {requested_by}: {reason}",
            payload={"requested_by": requested_by, "reason": reason},
        )
        process.events.append(event)
        process.updated_at = event.occurred_at
        return event

    def summary(self, *, tenant_id: str) -> dict[str, Any]:
        processes = self.list_processes(tenant_id=tenant_id)
        by_status = {status.value: 0 for status in WorkflowCockpitStatus}
        blocked_external = 0
        replayable = 0
        for process in processes:
            by_status[process.status.value] += 1
            if process.status == WorkflowCockpitStatus.BLOCKED_EXTERNAL_GATE:
                blocked_external += 1
            if process.replayable:
                replayable += 1
        return {
            "tenant_id": tenant_id,
            "total_processes": len(processes),
            "by_status": by_status,
            "blocked_external_gate": blocked_external,
            "replayable": replayable,
        }


workflow_cockpit_service = WorkflowCockpitService()
