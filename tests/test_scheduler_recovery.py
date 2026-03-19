from __future__ import annotations

from datetime import datetime, timezone

from app.core.scheduler_heartbeat import HeartbeatHealthResult, SchedulerNodeStatus
from app.core.scheduler_recovery import (
    SchedulerRecoveryAction,
    build_scheduler_recovery_notification,
    build_scheduler_recovery_plan,
    build_scheduler_runtime_component,
)


def _health(status: SchedulerNodeStatus, *, running_job_ids: tuple[str, ...] = ()) -> HeartbeatHealthResult:
    return HeartbeatHealthResult(
        scheduler_id="scheduler-a",
        status=status,
        active_worker_ids=(),
        degraded_worker_ids=("worker-d",) if status == SchedulerNodeStatus.DEGRADED else (),
        stale_worker_ids=("worker-s",) if status == SchedulerNodeStatus.STALE else (),
        running_job_ids=running_job_ids,
        evaluated_at=datetime(2026, 3, 16, 12, 0, tzinfo=timezone.utc),
        stale_after_seconds=120,
        degrade_after_seconds=45,
    )


def test_build_scheduler_recovery_plan_for_active():
    plan = build_scheduler_recovery_plan(_health(SchedulerNodeStatus.ACTIVE))

    assert plan.escalation_level == "OK"
    assert plan.actions == (SchedulerRecoveryAction.NONE,)


def test_build_scheduler_recovery_plan_for_degraded():
    plan = build_scheduler_recovery_plan(_health(SchedulerNodeStatus.DEGRADED))

    assert plan.escalation_level == "WARNUNG"
    assert plan.actions == (SchedulerRecoveryAction.NOTIFY_OPERATIONS,)
    assert plan.degraded_worker_ids == ("worker-d",)


def test_build_scheduler_recovery_plan_for_stale_with_running_jobs():
    plan = build_scheduler_recovery_plan(
        _health(SchedulerNodeStatus.STALE, running_job_ids=("job-1", "job-2"))
    )

    assert plan.escalation_level == "KRITISCH"
    assert SchedulerRecoveryAction.RESTART_WORKER in plan.actions
    assert SchedulerRecoveryAction.REQUEUE_STALE_JOBS in plan.actions
    assert SchedulerRecoveryAction.FAILOVER_SCHEDULER in plan.actions


def test_build_scheduler_runtime_component_maps_status_to_runtime_health():
    component = build_scheduler_runtime_component(
        _health(SchedulerNodeStatus.DEGRADED),
        worker_id="worker-1",
    )

    assert component.component_type == "scheduler_worker"
    assert component.health.value == "degraded"
    assert component.metrics["scheduler_status"] == "DEGRADED"


def test_build_scheduler_recovery_notification_uses_escalation_contract():
    plan = build_scheduler_recovery_plan(_health(SchedulerNodeStatus.STALE, running_job_ids=("job-1",)))
    notification = build_scheduler_recovery_notification(plan, worker_id="worker-1")

    assert notification.ausloeser.value == "ESKALATION"
    assert notification.prozess_id == "scheduler-a"
    assert "worker-1" in notification.inhalt
