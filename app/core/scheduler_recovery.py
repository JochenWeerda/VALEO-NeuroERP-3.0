"""
scheduler_recovery.py — Recovery- und Eskalations-Contracts fuer Scheduler-Heartbeats

Setzt auf scheduler_heartbeat.py auf und definiert standardisierte
Recovery-/Eskalationsaktionen fuer ACTIVE / DEGRADED / STALE Scheduler-Zustaende.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .process_notification_contracts import (
    NotifikationsAusloeser,
    NotifikationsNachricht,
    erstelle_benachrichtigung,
    route_benachrichtigung,
)
from .runtime_operations import ComponentHealth, RuntimeComponent
from .scheduler_heartbeat import HeartbeatHealthResult, SchedulerNodeStatus


class SchedulerRecoveryAction(str, Enum):
    NONE = "NONE"
    NOTIFY_OPERATIONS = "NOTIFY_OPERATIONS"
    RESTART_WORKER = "RESTART_WORKER"
    REQUEUE_STALE_JOBS = "REQUEUE_STALE_JOBS"
    FAILOVER_SCHEDULER = "FAILOVER_SCHEDULER"


@dataclass(frozen=True)
class SchedulerRecoveryPlan:
    scheduler_id: str
    status: SchedulerNodeStatus
    escalation_level: str
    actions: tuple[SchedulerRecoveryAction, ...]
    stale_worker_ids: tuple[str, ...] = ()
    degraded_worker_ids: tuple[str, ...] = ()
    running_job_ids: tuple[str, ...] = ()
    rationale: list[str] = field(default_factory=list)
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "scheduler_id": self.scheduler_id,
            "status": self.status.value,
            "escalation_level": self.escalation_level,
            "actions": [action.value for action in self.actions],
            "stale_worker_ids": list(self.stale_worker_ids),
            "degraded_worker_ids": list(self.degraded_worker_ids),
            "running_job_ids": list(self.running_job_ids),
            "rationale": list(self.rationale),
            "schema_version": self.schema_version,
        }


def resolve_scheduler_health_from_status(
    scheduler_status: dict[str, Any],
) -> tuple[HeartbeatHealthResult | None, datetime | None]:
    """Rekonstruiert den Heartbeat-Health-Contract aus dem Scheduler-Status-Payload."""
    heartbeat = scheduler_status.get("heartbeat") or {}
    if not heartbeat:
        return None, None

    last_heartbeat = heartbeat.get("last_heartbeat") or {}
    last_heartbeat_at = (
        datetime.fromisoformat(last_heartbeat["heartbeat_at"])
        if last_heartbeat.get("heartbeat_at")
        else None
    )
    return (
        HeartbeatHealthResult(
            scheduler_id=str(heartbeat["scheduler_id"]),
            status=SchedulerNodeStatus(str(heartbeat["status"])),
            active_worker_ids=tuple(heartbeat.get("active_worker_ids", [])),
            degraded_worker_ids=tuple(heartbeat.get("degraded_worker_ids", [])),
            stale_worker_ids=tuple(heartbeat.get("stale_worker_ids", [])),
            running_job_ids=tuple(heartbeat.get("running_job_ids", [])),
            evaluated_at=datetime.fromisoformat(str(heartbeat["evaluated_at"])),
            stale_after_seconds=int(heartbeat["stale_after_seconds"]),
            degrade_after_seconds=int(heartbeat["degrade_after_seconds"]),
        ),
        last_heartbeat_at,
    )


def build_scheduler_recovery_plan(health: HeartbeatHealthResult) -> SchedulerRecoveryPlan:
    if health.status == SchedulerNodeStatus.ACTIVE:
        return SchedulerRecoveryPlan(
            scheduler_id=health.scheduler_id,
            status=health.status,
            escalation_level="OK",
            actions=(SchedulerRecoveryAction.NONE,),
            running_job_ids=health.running_job_ids,
            rationale=["Scheduler heartbeat is healthy; no recovery action required."],
        )

    if health.status == SchedulerNodeStatus.DEGRADED:
        return SchedulerRecoveryPlan(
            scheduler_id=health.scheduler_id,
            status=health.status,
            escalation_level="WARNUNG",
            actions=(SchedulerRecoveryAction.NOTIFY_OPERATIONS,),
            degraded_worker_ids=health.degraded_worker_ids,
            running_job_ids=health.running_job_ids,
            rationale=[
                "Heartbeat exceeded degrade threshold but lease is still valid.",
                "Operations should inspect scheduler latency before jobs become stale.",
            ],
        )

    actions: list[SchedulerRecoveryAction] = [
        SchedulerRecoveryAction.NOTIFY_OPERATIONS,
        SchedulerRecoveryAction.RESTART_WORKER,
    ]
    rationale = [
        "Heartbeat is stale or lease expired.",
        "Scheduler/worker restart is required before queued or running jobs can be trusted again.",
    ]
    if health.running_job_ids:
        actions.append(SchedulerRecoveryAction.REQUEUE_STALE_JOBS)
        rationale.append("Running jobs are attached to a stale worker and require deterministic reassignment.")
    actions.append(SchedulerRecoveryAction.FAILOVER_SCHEDULER)
    rationale.append("Failover should be prepared if the primary scheduler does not recover immediately.")
    return SchedulerRecoveryPlan(
        scheduler_id=health.scheduler_id,
        status=health.status,
        escalation_level="KRITISCH",
        actions=tuple(actions),
        stale_worker_ids=health.stale_worker_ids,
        degraded_worker_ids=health.degraded_worker_ids,
        running_job_ids=health.running_job_ids,
        rationale=rationale,
    )


def build_scheduler_runtime_component(
    health: HeartbeatHealthResult,
    *,
    worker_id: str,
    last_heartbeat_at: datetime | None = None,
    recovery_plan: SchedulerRecoveryPlan | None = None,
    notification_preview: NotifikationsNachricht | None = None,
) -> RuntimeComponent:
    if health.status == SchedulerNodeStatus.ACTIVE:
        component_health = ComponentHealth.HEALTHY
    elif health.status == SchedulerNodeStatus.DEGRADED:
        component_health = ComponentHealth.DEGRADED
    else:
        component_health = ComponentHealth.UNHEALTHY

    metrics = {
        "scheduler_status": health.status.value,
        "active_worker_ids": list(health.active_worker_ids),
        "degraded_worker_ids": list(health.degraded_worker_ids),
        "stale_worker_ids": list(health.stale_worker_ids),
        "running_job_ids": list(health.running_job_ids),
    }
    if recovery_plan is not None:
        metrics["recovery_plan"] = recovery_plan.as_dict()
    if notification_preview is not None:
        metrics["notification_preview"] = notification_preview.as_dict()

    return RuntimeComponent(
        component_id=f"{health.scheduler_id}:{worker_id}",
        component_type="scheduler_worker",
        health=component_health,
        last_heartbeat=last_heartbeat_at,
        metrics=metrics,
    )


def build_scheduler_recovery_notification(
    plan: SchedulerRecoveryPlan,
    *,
    worker_id: str,
    generated_at: datetime | None = None,
) -> NotifikationsNachricht:
    if plan.status == SchedulerNodeStatus.ACTIVE:
        title = f"Scheduler {plan.scheduler_id} healthy"
        content = "Scheduler heartbeat is active. No operational recovery action is required."
    elif plan.status == SchedulerNodeStatus.DEGRADED:
        title = f"Scheduler {plan.scheduler_id} degraded"
        content = (
            f"Scheduler worker {worker_id} is degraded. "
            f"Recommended actions: {', '.join(action.value for action in plan.actions)}."
        )
    else:
        content = (
            f"Scheduler worker {worker_id} is stale. "
            f"Recommended actions: {', '.join(action.value for action in plan.actions)}."
        )
        if plan.running_job_ids:
            content += f" Running jobs requiring review: {', '.join(plan.running_job_ids)}."
        title = f"Scheduler {plan.scheduler_id} stale"

    routing = route_benachrichtigung(
        NotifikationsAusloeser.ESKALATION,
        domain="operations",
        prozess_typ="scheduler",
    )
    return erstelle_benachrichtigung(
        nachricht_id=f"scheduler-recovery-{plan.scheduler_id}",
        ausloeser=NotifikationsAusloeser.ESKALATION,
        titel=title,
        inhalt=content,
        prozess_id=plan.scheduler_id,
        routing=routing,
        jetzt=generated_at,
    )
