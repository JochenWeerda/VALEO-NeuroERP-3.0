"""
Runtime Operations API — Wave 4 AP6

Betriebsmetriken, Rebuild und Replay für den Process Kernel.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends

from ....core.database import get_db
from ....core.endpoint_gateways import get_projection_status_loader, register_runtime_report_loader
from ....core.projection_cursor_service import persist_projection_cursor, REPLAY_PROJECTION_CONSUMER_ID
from ....core.tenant import get_tenant_id
from ....core.runtime_operations import (
    RuntimeHealthReport,
    RuntimeComponent,
    ReplayRequest,
    RebuildRequest,
    ComponentHealth,
)
from ....core.scheduler_heartbeat import HeartbeatHealthResult, SchedulerNodeStatus
from ....core.scheduler_recovery import build_scheduler_runtime_component
from ....services.scheduler_service import get_scheduler_status
router = APIRouter(prefix="/runtime", tags=["runtime", "operations"])

_replay_requests: list[ReplayRequest] = []
_rebuild_requests: list[RebuildRequest] = []


def _build_runtime_report(tenant_id: str, db: Any = None) -> RuntimeHealthReport:
    report = RuntimeHealthReport.build_default(tenant_id)
    projection_status_loader = get_projection_status_loader()
    if projection_status_loader is None:
        return report
    projection_status = projection_status_loader(tenant_id, db)

    projection_component = RuntimeComponent(
        component_id="finance-projections-01",
        component_type="projection_consumer",
        health=(
            ComponentHealth.DEGRADED
            if projection_status.cache_misses > projection_status.cache_hits and projection_status.projection_count > 0
            else ComponentHealth.HEALTHY
        ),
        metrics={
            "projection_count": projection_status.projection_count,
            "persisted_snapshot_count": projection_status.persisted_snapshot_count,
            "persisted_cursor_count": projection_status.persisted_cursor_count,
            "cache_hits": projection_status.cache_hits,
            "cache_misses": projection_status.cache_misses,
            "last_rebuilt_at": projection_status.last_rebuilt_at,
            "last_snapshot_at": projection_status.last_snapshot_at,
            "last_cursor_advanced_at": projection_status.last_cursor_advanced_at,
            "last_event_processed": projection_status.last_processed_event_id,
            "projection_cursors": [
                {
                    "projection_key": entry.projection_key,
                    "cursor_status": entry.cursor_status,
                    "cursor_source": entry.cursor_source,
                    "cursor_updated_at": entry.cursor_updated_at,
                    "last_event_processed": entry.last_processed_event_id,
                }
                for entry in projection_status.projections
                if entry.cursor_status or entry.cursor_source or entry.cursor_updated_at or entry.last_processed_event_id
            ],
        },
    )
    report.components.append(projection_component)
    report.active_replays = sum(
        1 for r in _replay_requests
        if r.tenant_id == tenant_id and r.status == "pending"
    )
    report.active_rebuilds = sum(
        1 for r in _rebuild_requests
        if r.tenant_id == tenant_id and r.status == "pending"
    )
    scheduler_status = get_scheduler_status()
    heartbeat = scheduler_status.get("heartbeat") or {}
    if heartbeat:
        scheduler_component = build_scheduler_runtime_component(
            HeartbeatHealthResult(
                scheduler_id=heartbeat["scheduler_id"],
                status=SchedulerNodeStatus(heartbeat["status"]),
                active_worker_ids=tuple(heartbeat.get("active_worker_ids", [])),
                degraded_worker_ids=tuple(heartbeat.get("degraded_worker_ids", [])),
                stale_worker_ids=tuple(heartbeat.get("stale_worker_ids", [])),
                running_job_ids=tuple(heartbeat.get("running_job_ids", [])),
                evaluated_at=datetime.fromisoformat(heartbeat["evaluated_at"]),
                stale_after_seconds=int(heartbeat["stale_after_seconds"]),
                degrade_after_seconds=int(heartbeat["degrade_after_seconds"]),
            ),
            worker_id=scheduler_status.get("worker_id", "scheduler-worker"),
            last_heartbeat_at=(
                datetime.fromisoformat(heartbeat["last_heartbeat"]["heartbeat_at"])
                if heartbeat.get("last_heartbeat")
                else None
            ),
        )
        report.components.append(scheduler_component)
    report.overall_health = report.compute_overall_health()
    return report


register_runtime_report_loader(_build_runtime_report)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=dict)
async def get_runtime_health(
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
):
    """Liefert den aktuellen Gesundheitsbericht des Process Kernels."""
    report = _build_runtime_report(tenant_id, db=db)
    return report.model_dump(mode="json")


@router.get("/components", response_model=list[dict])
async def list_runtime_components(
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
):
    """Listet alle bekannten Process-Kernel-Komponenten."""
    report = _build_runtime_report(tenant_id, db=db)
    return [c.model_dump(mode="json") for c in report.components]


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------

@router.post("/replay", response_model=dict, status_code=202)
async def create_replay_request(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
):
    """Erstellt einen Event-Replay-Auftrag (202 Accepted)."""
    req = ReplayRequest(
        replay_id=body.get("replay_id") or str(uuid.uuid4()),
        tenant_id=tenant_id,
        target_type=body.get("target_type", "projection"),
        target_id=body.get("target_id", ""),
        from_event_id=body.get("from_event_id"),
        to_event_id=body.get("to_event_id"),
        requested_by=body.get("requested_by", "system"),
        reason=body.get("reason", ""),
        status="pending",
    )
    _replay_requests.append(req)
    if req.target_type == "projection" and req.target_id:
        persist_projection_cursor(
            db,
            tenant_id,
            body.get("consumer_id", REPLAY_PROJECTION_CONSUMER_ID),
            req.target_id,
            cursor_token=req.to_event_id or req.from_event_id or req.replay_id,
            last_event_id=req.to_event_id or req.from_event_id,
            replay_from_event_id=req.from_event_id,
            replay_to_event_id=req.to_event_id,
            status="pending-replay",
        )
    return req.model_dump(mode="json")


@router.get("/replay", response_model=list[dict])
async def list_replay_requests(
    tenant_id: str = Depends(get_tenant_id),
):
    """Listet alle Replay-Anforderungen des Mandanten."""
    reqs = [r for r in _replay_requests if r.tenant_id == tenant_id]
    return [r.model_dump(mode="json") for r in reqs]


# ---------------------------------------------------------------------------
# Rebuild
# ---------------------------------------------------------------------------

@router.post("/rebuild", response_model=dict, status_code=202)
async def create_rebuild_request(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt einen Projektion-Rebuild-Auftrag (202 Accepted)."""
    req = RebuildRequest(
        rebuild_id=body.get("rebuild_id") or str(uuid.uuid4()),
        tenant_id=tenant_id,
        projection_name=body.get("projection_name", ""),
        requested_by=body.get("requested_by", "system"),
        reason=body.get("reason", ""),
        status="pending",
    )
    _rebuild_requests.append(req)
    return req.model_dump(mode="json")


@router.get("/rebuild", response_model=list[dict])
async def list_rebuild_requests(
    tenant_id: str = Depends(get_tenant_id),
):
    """Listet alle Rebuild-Anforderungen des Mandanten."""
    reqs = [r for r in _rebuild_requests if r.tenant_id == tenant_id]
    return [r.model_dump(mode="json") for r in reqs]
