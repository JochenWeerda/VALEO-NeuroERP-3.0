"""Queue-backed background job API for heavy process operations."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.background_jobs import (
    JobEnqueueRequest,
    JobPrioritaet,
    JobStatus,
    JobTyp,
    create_job_from_request,
    get_background_job_registry,
    get_default_job_types,
)

router = APIRouter(prefix="/process/background-jobs", tags=["process-kernel", "jobs"])


class BackgroundJobEnqueueIn(BaseModel):
    typ: JobTyp
    angefordert_von: str = Field(min_length=1)
    parameter: dict[str, Any] = Field(default_factory=dict)
    prioritaet_override: JobPrioritaet | None = None
    tenant_id: str = Field(default="")


class BackgroundJobMutationIn(BaseModel):
    ergebnis_summary: str = ""
    fehler_meldung: str = ""


@router.get("/types", response_model=dict)
def list_job_types() -> dict[str, Any]:
    definitions = get_default_job_types()
    return {
        "schema_version": 1,
        "job_type_count": len(definitions),
        "job_types": [definition.as_dict() for definition in definitions],
    }


@router.get("", response_model=dict)
def list_background_jobs(
    status: str = "",
    tenant_id: str = "",
    typ: str = "",
    limit: int = Query(default=100, ge=1, le=500),
) -> dict[str, Any]:
    registry = get_background_job_registry()
    status_enum = JobStatus(status) if status else None
    typ_enum = JobTyp(typ) if typ else None
    jobs = registry.list(status=status_enum, tenant_id=tenant_id or None, typ=typ_enum, limit=limit)
    return {
        "schema_version": 1,
        "summary": registry.summary(),
        "job_count": len(jobs),
        "jobs": [job.as_dict() for job in jobs],
    }


@router.get("/queue", response_model=dict)
def get_background_job_queue() -> dict[str, Any]:
    registry = get_background_job_registry()
    summary = registry.summary()
    return {
        "schema_version": 1,
        "queue": summary["queue"],
        "counts_by_status": summary["counts_by_status"],
        "running_jobs": summary["running_jobs"],
        "pending_jobs": summary["pending_jobs"],
    }


@router.post("/enqueue", response_model=dict, status_code=201)
def enqueue_background_job(body: BackgroundJobEnqueueIn) -> dict[str, Any]:
    registry = get_background_job_registry()
    req = JobEnqueueRequest(
        typ=body.typ,
        angefordert_von=body.angefordert_von,
        parameter=body.parameter,
        prioritaet_override=body.prioritaet_override,
        tenant_id=body.tenant_id,
    )
    job, routing = registry.enqueue(req)
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "routing": routing.as_dict(),
        "queue": registry.summary()["queue"],
    }


@router.post("/dequeue", response_model=dict)
def dequeue_background_job() -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.dequeue_next()
    if job is None:
        raise HTTPException(status_code=404, detail="No pending jobs in queue")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "queue": registry.summary()["queue"],
    }


@router.get("/{job_id}", response_model=dict)
def get_background_job(job_id: str) -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Background job not found")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
    }


@router.post("/{job_id}/complete", response_model=dict)
def complete_background_job(job_id: str, body: BackgroundJobMutationIn | None = None) -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.complete(job_id, ergebnis_summary=(body.ergebnis_summary if body else ""))
    if job is None:
        raise HTTPException(status_code=404, detail="Background job not found")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "queue": registry.summary()["queue"],
    }


@router.post("/{job_id}/fail", response_model=dict)
def fail_background_job(job_id: str, body: BackgroundJobMutationIn | None = None) -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.fail(job_id, fehler_meldung=(body.fehler_meldung if body else "Unspecified failure"))
    if job is None:
        raise HTTPException(status_code=404, detail="Background job not found")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "queue": registry.summary()["queue"],
    }
