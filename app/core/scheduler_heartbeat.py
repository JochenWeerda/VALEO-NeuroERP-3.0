"""
scheduler_heartbeat.py — Scheduler- und Worker-Heartbeat-Contracts

Ergaenzt die queue-basierten Background-Job-Contracts um Worker-Liveness,
Lease-Fristen und Stale-Detection fuer Scheduler-/Worker-Setups.

Ziel:
- keine still haengenden Jobs ohne sichtbaren Owner
- deterministische Bewertung von ACTIVE / DEGRADED / STALE
- worker-agnostisch fuer Celery, ARQ, APScheduler, Threads oder externe Runner
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum


class SchedulerNodeStatus(str, Enum):
    """Gesundheitsstatus eines Scheduler-/Worker-Knotens."""

    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    STALE = "STALE"


@dataclass(frozen=True)
class WorkerHeartbeat:
    """Ein Heartbeat eines Worker-/Scheduler-Knotens."""

    scheduler_id: str
    worker_id: str
    worker_klasse: str
    heartbeat_at: datetime
    lease_until: datetime
    running_job_ids: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "scheduler_id": self.scheduler_id,
            "worker_id": self.worker_id,
            "worker_klasse": self.worker_klasse,
            "heartbeat_at": self.heartbeat_at.isoformat(),
            "lease_until": self.lease_until.isoformat(),
            "running_job_ids": list(self.running_job_ids),
            "metadata": dict(self.metadata),
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class HeartbeatHealthResult:
    """Aggregierte Bewertung eines Heartbeat-Bestands."""

    scheduler_id: str
    status: SchedulerNodeStatus
    active_worker_ids: tuple[str, ...]
    degraded_worker_ids: tuple[str, ...]
    stale_worker_ids: tuple[str, ...]
    running_job_ids: tuple[str, ...]
    evaluated_at: datetime
    stale_after_seconds: int
    degrade_after_seconds: int
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "scheduler_id": self.scheduler_id,
            "status": self.status.value,
            "active_worker_ids": list(self.active_worker_ids),
            "degraded_worker_ids": list(self.degraded_worker_ids),
            "stale_worker_ids": list(self.stale_worker_ids),
            "running_job_ids": list(self.running_job_ids),
            "evaluated_at": self.evaluated_at.isoformat(),
            "stale_after_seconds": self.stale_after_seconds,
            "degrade_after_seconds": self.degrade_after_seconds,
            "schema_version": self.schema_version,
        }


def record_worker_heartbeat(
    *,
    scheduler_id: str,
    worker_id: str,
    worker_klasse: str,
    heartbeat_at: datetime | None = None,
    lease_duration_seconds: int = 60,
    running_job_ids: list[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> WorkerHeartbeat:
    """Erzeugt einen neuen Worker-Heartbeat mit Lease-Frist."""

    if lease_duration_seconds <= 0:
        raise ValueError("lease_duration_seconds must be > 0")
    ts = heartbeat_at or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return WorkerHeartbeat(
        scheduler_id=scheduler_id,
        worker_id=worker_id,
        worker_klasse=worker_klasse,
        heartbeat_at=ts,
        lease_until=ts + timedelta(seconds=lease_duration_seconds),
        running_job_ids=tuple(running_job_ids or ()),
        metadata=dict(metadata or {}),
    )


def evaluate_scheduler_heartbeats(
    heartbeats: list[WorkerHeartbeat],
    *,
    scheduler_id: str,
    evaluated_at: datetime | None = None,
    stale_after_seconds: int = 120,
    degrade_after_seconds: int = 45,
) -> HeartbeatHealthResult:
    """
    Bewertet Worker-Heartbeats fuer einen Scheduler.

    ACTIVE:
    - Heartbeat juenger oder gleich `degrade_after_seconds`

    DEGRADED:
    - Heartbeat aelter als `degrade_after_seconds`
    - aber Lease/Frist noch nicht abgelaufen und nicht aelter als `stale_after_seconds`

    STALE:
    - Lease abgelaufen oder Heartbeat aelter als `stale_after_seconds`
    """

    if stale_after_seconds <= 0:
        raise ValueError("stale_after_seconds must be > 0")
    if degrade_after_seconds <= 0:
        raise ValueError("degrade_after_seconds must be > 0")
    if degrade_after_seconds >= stale_after_seconds:
        raise ValueError("degrade_after_seconds must be < stale_after_seconds")

    ts = evaluated_at or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    relevant = [hb for hb in heartbeats if hb.scheduler_id == scheduler_id]
    active: list[str] = []
    degraded: list[str] = []
    stale: list[str] = []
    running_jobs: set[str] = set()

    for hb in relevant:
        running_jobs.update(hb.running_job_ids)
        age_seconds = (ts - hb.heartbeat_at).total_seconds()
        lease_expired = hb.lease_until <= ts
        if lease_expired or age_seconds > stale_after_seconds:
            stale.append(hb.worker_id)
        elif age_seconds > degrade_after_seconds:
            degraded.append(hb.worker_id)
        else:
            active.append(hb.worker_id)

    if stale:
        status = SchedulerNodeStatus.STALE
    elif degraded:
        status = SchedulerNodeStatus.DEGRADED
    else:
        status = SchedulerNodeStatus.ACTIVE

    return HeartbeatHealthResult(
        scheduler_id=scheduler_id,
        status=status,
        active_worker_ids=tuple(sorted(active)),
        degraded_worker_ids=tuple(sorted(degraded)),
        stale_worker_ids=tuple(sorted(stale)),
        running_job_ids=tuple(sorted(running_jobs)),
        evaluated_at=ts,
        stale_after_seconds=stale_after_seconds,
        degrade_after_seconds=degrade_after_seconds,
    )
