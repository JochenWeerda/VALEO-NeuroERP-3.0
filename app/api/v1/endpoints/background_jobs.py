"""Queue-backed background job API for heavy process operations."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.tenant import get_tenant_id
from app.core.background_jobs import (
    JobEnqueueRequest,
    JobPrioritaet,
    JobStatus,
    JobTyp,
    get_background_job_registry,
    get_default_job_types,
)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


class BackgroundJobOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


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


@router.get("/types", response_model=BackgroundJobOut, summary="Job types auflisten")
def list_job_types() -> dict[str, Any]:
    definitions = get_default_job_types()
    return {
        "schema_version": 1,
        "job_type_count": len(definitions),
        "job_types": [definition.as_dict() for definition in definitions],
    }


@router.get("", response_model=BackgroundJobOut, summary="Background jobs auflisten")
def list_background_jobs(
    status: str = "",
    tenant_id: str = "",
    typ: str = "",
    limit: int = Query(default=100, ge=1, le=500),
    page: int = Query(default=1, ge=1),
    active_tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    registry = get_background_job_registry()
    if tenant_id and tenant_id != active_tenant_id:
        raise HTTPException(403, "Requested tenant does not match the verified context")
    status_enum = JobStatus(status) if status else None
    typ_enum = JobTyp(typ) if typ else None
    jobs = registry.list(status=status_enum, tenant_id=active_tenant_id, typ=typ_enum)
    offset = (page - 1) * limit
    page_jobs = [job.as_dict() for job in jobs[offset:offset + limit]]
    return {
        "schema_version": 1,
        "summary": registry.summary(tenant_id=active_tenant_id),
        "job_count": len(page_jobs),
        "total": len(jobs),
        "items": page_jobs,
        "jobs": page_jobs,
    }


@router.get("/queue", response_model=BackgroundJobOut, summary="Background job queue abrufen")
def get_background_job_queue(active_tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    registry = get_background_job_registry()
    summary = registry.summary(tenant_id=active_tenant_id)
    return {
        "schema_version": 1,
        "queue": summary["queue"],
        "counts_by_status": summary["counts_by_status"],
        "running_jobs": summary["running_jobs"],
        "pending_jobs": summary["pending_jobs"],
    }


@router.post("/enqueue", response_model=BackgroundJobOut, status_code=201, summary="Background job enqueue", dependencies=SCHREIBEN["FACHLICH"])
def enqueue_background_job(body: BackgroundJobEnqueueIn, active_tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    registry = get_background_job_registry()
    if body.tenant_id and body.tenant_id != active_tenant_id:
        raise HTTPException(403, "Requested tenant does not match the verified context")
    req = JobEnqueueRequest(
        typ=body.typ,
        angefordert_von=body.angefordert_von,
        parameter=body.parameter,
        prioritaet_override=body.prioritaet_override,
        tenant_id=active_tenant_id,
    )
    job, routing = registry.enqueue(req)
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "routing": routing.as_dict(),
        "queue": registry.summary(tenant_id=active_tenant_id)["queue"],
    }


@router.post("/dequeue", response_model=BackgroundJobOut, summary="Background job dequeue", dependencies=SCHREIBEN["FACHLICH"])
def dequeue_background_job(active_tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.dequeue_next(tenant_id=active_tenant_id)
    if job is None:
        raise HTTPException(status_code=404, detail="No pending jobs in queue")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "queue": registry.summary(tenant_id=active_tenant_id)["queue"],
    }


@router.get("/{job_id}", response_model=BackgroundJobOut, summary="Background job abrufen")
def get_background_job(job_id: str, active_tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.get(job_id, tenant_id=active_tenant_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Background job not found")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
    }


@router.post("/{job_id}/complete", response_model=BackgroundJobOut, summary="Background job complete", dependencies=SCHREIBEN["FACHLICH"])
def complete_background_job(
    job_id: str,
    body: BackgroundJobMutationIn | None = None,
    active_tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.complete(job_id, ergebnis_summary=(body.ergebnis_summary if body else ""), tenant_id=active_tenant_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Background job not found")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "queue": registry.summary(tenant_id=active_tenant_id)["queue"],
    }


@router.post("/{job_id}/fail", response_model=BackgroundJobOut, summary="Background job fail", dependencies=SCHREIBEN["FACHLICH"])
def fail_background_job(
    job_id: str,
    body: BackgroundJobMutationIn | None = None,
    active_tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    registry = get_background_job_registry()
    job = registry.fail(job_id, fehler_meldung=(body.fehler_meldung if body else "Unspecified failure"), tenant_id=active_tenant_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Background job not found")
    return {
        "schema_version": 1,
        "job": job.as_dict(),
        "queue": registry.summary(tenant_id=active_tenant_id)["queue"],
    }
