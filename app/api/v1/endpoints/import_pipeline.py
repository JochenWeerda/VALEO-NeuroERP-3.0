"""
Import Pipeline Endpoints — Wave 3 AP6
Standardisierte Import-Pipelines fuer CSV, EDI, OCR und andere Formate.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ....core.tenant import get_tenant_id
from ....core.import_pipeline import (
    ImportPipelineJob,
    ImportPipelineConfig,
    ImportValidationResult,
    ImportStage,
)

router = APIRouter(prefix="/import-pipeline", tags=["import", "pipeline"])

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_JOBS: dict[str, dict[str, Any]] = {}     # tenant_id → {job_id → job dict}
_CONFIGS: dict[str, dict[str, Any]] = {}  # tenant_id → {config_id → config dict}


def _job_store(tenant_id: str) -> dict[str, Any]:
    return _JOBS.setdefault(tenant_id, {})


def _config_store(tenant_id: str) -> dict[str, Any]:
    return _CONFIGS.setdefault(tenant_id, {})


# ---------------------------------------------------------------------------
# Job endpoints
# ---------------------------------------------------------------------------

@router.get("/jobs", response_model=list[ImportPipelineJob])
async def list_jobs(tenant_id: str = Depends(get_tenant_id)):
    """List all import pipeline jobs for the tenant."""
    store = _job_store(tenant_id)
    return list(store.values())


@router.post("/jobs", response_model=ImportPipelineJob, status_code=201)
async def create_job(
    job: ImportPipelineJob,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create / start a new import pipeline job."""
    store = _job_store(tenant_id)
    now = datetime.now(timezone.utc).isoformat()
    job = job.model_copy(update={
        "tenant_id": tenant_id,
        "created_at": now,
        "updated_at": now,
    })
    store[job.job_id] = job.model_dump()
    return job


@router.get("/jobs/{job_id}", response_model=ImportPipelineJob)
async def get_job(
    job_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get an import pipeline job by ID."""
    store = _job_store(tenant_id)
    if job_id not in store:
        raise HTTPException(status_code=404, detail="Job not found")
    return store[job_id]


@router.post("/jobs/{job_id}/validate", response_model=ImportValidationResult)
async def validate_job(
    job_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Run validation for an import pipeline job."""
    store = _job_store(tenant_id)
    if job_id not in store:
        raise HTTPException(status_code=404, detail="Job not found")

    job = store[job_id]

    # Stub validation: mark as valid if total_rows > 0
    is_valid = job.get("total_rows", 0) > 0
    result = ImportValidationResult(
        is_valid=is_valid,
        error_count=0 if is_valid else 1,
        warning_count=0,
        errors=[] if is_valid else ["No rows to process"],
        warnings=[],
    )

    # Update job stage
    now = datetime.now(timezone.utc).isoformat()
    job["stage"] = ImportStage.validated.value if is_valid else ImportStage.failed.value
    job["validation_result"] = result.model_dump()
    job["updated_at"] = now

    return result


# ---------------------------------------------------------------------------
# Config endpoints
# ---------------------------------------------------------------------------

@router.get("/configs", response_model=list[ImportPipelineConfig])
async def list_configs(tenant_id: str = Depends(get_tenant_id)):
    """List all import pipeline configs for the tenant."""
    store = _config_store(tenant_id)
    return list(store.values())
