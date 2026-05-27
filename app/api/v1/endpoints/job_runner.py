"""
Job Runner API.
POST /api/jobs/run (scheduleId, dryRun?), GET /api/jobs, GET /api/jobs/{id}/artifacts
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.background_jobs import (
    JobQueue,
    evaluate_job_routing,
    get_default_job_types,
)
from app.core.tenant import get_tenant_id

router = APIRouter()


# ── Pydantic Models ─────────────────────────────────────────────────────────────

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    schedule_id: Optional[str] = None
    job_type: str
    status: str
    triggered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    dry_run: bool
    created_at: Optional[datetime] = None


class JobRunIn(BaseModel):
    schedule_id: Optional[str] = None
    job_type: str = Field(..., min_length=1, max_length=80)
    dry_run: bool = False


class JobArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    artifact_key: str
    content_type: str
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum_sha256: Optional[str] = None
    created_at: Optional[datetime] = None


class JobRoutingOut(BaseModel):
    job_typ: str
    worker_klasse: str
    prioritaet: str
    timeout_sekunden: int
    meldung: str
    schema_version: int = 1


class JobCatalogOut(BaseModel):
    schema_version: int = 1
    job_count: int
    queue_summary: dict
    routings: list[JobRoutingOut]


# ── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/run", response_model=JobOut, status_code=201, summary="Job ausführen")
async def run_job(
    payload: JobRunIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Start a job run (scheduleId, dryRun?).
    Runner erzeugt Artefakte (CSV/XML/JSON), legt sie in Outbox ab.
    """
    from uuid import uuid4
    from sqlalchemy import text
    uid = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.jobs (id, tenant_id, schedule_id, job_type, status, dry_run)
            VALUES (:id, :tid, :sid, :jtype, 'running', :dry)
            """
        ),
        {
            "id": uid,
            "tid": tenant_id,
            "sid": payload.schedule_id,
            "jtype": payload.job_type,
            "dry": payload.dry_run,
        }
    )
    db.commit()

    # Placeholder: actual job execution would run in background (Celery/APScheduler)
    # For now, mark as completed immediately
    db.execute(
        text(
            "UPDATE domain_shared.jobs SET status = 'completed', completed_at = now() WHERE id = :id"
        ),
        {"id": uid}
    )
    db.commit()

    row = db.execute(
        text(
            "SELECT id, tenant_id, schedule_id, job_type, status, triggered_at, completed_at, error_message, dry_run, created_at "
            "FROM domain_shared.jobs WHERE id = :id"
        ),
        {"id": uid}
    ).fetchone()
    return JobOut(
        id=str(row[0]),
        tenant_id=str(row[1]),
        schedule_id=str(row[2]) if row[2] else None,
        job_type=row[3],
        status=row[4],
        triggered_at=row[5],
        completed_at=row[6],
        error_message=row[7],
        dry_run=row[8],
        created_at=row[9],
    )


@router.get("/catalog", response_model=JobCatalogOut, summary="Job catalog abrufen")
async def get_job_catalog(
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert eine agentenfaehige Sicht auf Queue-Typen und Job-Routing."""
    catalog = get_default_job_types()
    queue = JobQueue()
    queue_summary = queue.as_dict()
    routings = [evaluate_job_routing(job.typ).as_dict() for job in catalog]
    return JobCatalogOut(
        job_count=len(catalog),
        queue_summary=queue_summary,
        routings=[JobRoutingOut.model_validate(item) for item in routings],
    )


@router.get("", response_model=list[JobOut], summary="Jobs auflisten")
async def list_jobs(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List jobs (optional status filter)."""
    from sqlalchemy import text
    if status:
        rows = db.execute(
            text(
                "SELECT id, tenant_id, schedule_id, job_type, status, triggered_at, completed_at, error_message, dry_run, created_at "
                "FROM domain_shared.jobs WHERE tenant_id = :tid AND status = :s ORDER BY triggered_at DESC LIMIT :lim"
            ),
            {"tid": tenant_id, "s": status, "lim": limit}
        ).fetchall()
    else:
        rows = db.execute(
            text(
                "SELECT id, tenant_id, schedule_id, job_type, status, triggered_at, completed_at, error_message, dry_run, created_at "
                "FROM domain_shared.jobs WHERE tenant_id = :tid ORDER BY triggered_at DESC LIMIT :lim"
            ),
            {"tid": tenant_id, "lim": limit}
        ).fetchall()
    return [
        JobOut(
            id=str(r[0]),
            tenant_id=str(r[1]),
            schedule_id=str(r[2]) if r[2] else None,
            job_type=r[3],
            status=r[4],
            triggered_at=r[5],
            completed_at=r[6],
            error_message=r[7],
            dry_run=r[8],
            created_at=r[9],
        )
        for r in rows
    ]


@router.get("/{job_id}", response_model=JobOut, summary="Job abrufen")
async def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get job by ID."""
    from sqlalchemy import text
    row = db.execute(
        text(
            "SELECT id, tenant_id, schedule_id, job_type, status, triggered_at, completed_at, error_message, dry_run, created_at "
            "FROM domain_shared.jobs WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": job_id, "tid": tenant_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut(
        id=str(row[0]),
        tenant_id=str(row[1]),
        schedule_id=str(row[2]) if row[2] else None,
        job_type=row[3],
        status=row[4],
        triggered_at=row[5],
        completed_at=row[6],
        error_message=row[7],
        dry_run=row[8],
        created_at=row[9],
    )


@router.get("/{job_id}/artifacts", response_model=list[JobArtifactOut], summary="Job artifacts abrufen")
async def get_job_artifacts(
    job_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get artifacts for a job (CSV/XML/JSON in Outbox)."""
    from sqlalchemy import text
    job = db.execute(
        text("SELECT id FROM domain_shared.jobs WHERE id = :id AND tenant_id = :tid"),
        {"id": job_id, "tid": tenant_id}
    ).fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    rows = db.execute(
        text(
            "SELECT id, job_id, artifact_key, content_type, file_path, file_size_bytes, checksum_sha256, created_at "
            "FROM domain_shared.job_artifacts WHERE job_id = :jid ORDER BY created_at"
        ),
        {"jid": job_id}
    ).fetchall()
    return [
        JobArtifactOut(
            id=str(r[0]),
            job_id=str(r[1]),
            artifact_key=r[2],
            content_type=r[3],
            file_path=r[4],
            file_size_bytes=r[5],
            checksum_sha256=r[6],
            created_at=r[7],
        )
        for r in rows
    ]
