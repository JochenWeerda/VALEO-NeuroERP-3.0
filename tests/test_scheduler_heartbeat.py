from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.scheduler_heartbeat import (
    SchedulerNodeStatus,
    evaluate_scheduler_heartbeats,
    record_worker_heartbeat,
)


def test_record_worker_heartbeat_sets_lease_and_payload():
    now = datetime(2026, 3, 16, 12, 0, tzinfo=timezone.utc)

    heartbeat = record_worker_heartbeat(
        scheduler_id="scheduler-a",
        worker_id="worker-1",
        worker_klasse="FINANCE",
        heartbeat_at=now,
        lease_duration_seconds=90,
        running_job_ids=["job-1"],
        metadata={"host": "node-1"},
    )

    assert heartbeat.lease_until == now + timedelta(seconds=90)
    assert heartbeat.running_job_ids == ("job-1",)
    assert heartbeat.as_dict()["worker_klasse"] == "FINANCE"


def test_evaluate_scheduler_heartbeats_reports_active_status():
    now = datetime(2026, 3, 16, 12, 0, tzinfo=timezone.utc)
    heartbeats = [
        record_worker_heartbeat(
            scheduler_id="scheduler-a",
            worker_id="worker-1",
            worker_klasse="GENERAL",
            heartbeat_at=now - timedelta(seconds=10),
            running_job_ids=["job-1"],
        )
    ]

    result = evaluate_scheduler_heartbeats(
        heartbeats,
        scheduler_id="scheduler-a",
        evaluated_at=now,
    )

    assert result.status == SchedulerNodeStatus.ACTIVE
    assert result.active_worker_ids == ("worker-1",)
    assert result.running_job_ids == ("job-1",)


def test_evaluate_scheduler_heartbeats_reports_degraded_before_stale():
    now = datetime(2026, 3, 16, 12, 0, tzinfo=timezone.utc)
    heartbeats = [
        record_worker_heartbeat(
            scheduler_id="scheduler-a",
            worker_id="worker-1",
            worker_klasse="GENERAL",
            heartbeat_at=now - timedelta(seconds=60),
            lease_duration_seconds=90,
        )
    ]

    result = evaluate_scheduler_heartbeats(
        heartbeats,
        scheduler_id="scheduler-a",
        evaluated_at=now,
        degrade_after_seconds=45,
        stale_after_seconds=120,
    )

    assert result.status == SchedulerNodeStatus.DEGRADED
    assert result.degraded_worker_ids == ("worker-1",)


def test_evaluate_scheduler_heartbeats_reports_stale_when_lease_expired():
    now = datetime(2026, 3, 16, 12, 0, tzinfo=timezone.utc)
    heartbeats = [
        record_worker_heartbeat(
            scheduler_id="scheduler-a",
            worker_id="worker-1",
            worker_klasse="GENERAL",
            heartbeat_at=now - timedelta(seconds=90),
            lease_duration_seconds=30,
        )
    ]

    result = evaluate_scheduler_heartbeats(
        heartbeats,
        scheduler_id="scheduler-a",
        evaluated_at=now,
        degrade_after_seconds=45,
        stale_after_seconds=120,
    )

    assert result.status == SchedulerNodeStatus.STALE
    assert result.stale_worker_ids == ("worker-1",)


def test_evaluate_scheduler_heartbeats_validates_thresholds():
    with pytest.raises(ValueError, match="degrade_after_seconds must be < stale_after_seconds"):
        evaluate_scheduler_heartbeats(
            [],
            scheduler_id="scheduler-a",
            degrade_after_seconds=60,
            stale_after_seconds=60,
        )
