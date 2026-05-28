"""
Import Pipeline Endpoints — Wave 3 AP6
Standardisierte Import-Pipelines fuer CSV, EDI, OCR und andere Formate.
"""

from __future__ import annotations

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

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


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

@router.get("/jobs", response_model=list[ImportPipelineJob], summary="Jobs auflisten")
async def list_jobs(tenant_id: str = Depends(get_tenant_id)):
    """List all import pipeline jobs for the tenant."""
    store = _job_store(tenant_id)
    return list(store.values())


@router.post("/jobs", response_model=ImportPipelineJob, status_code=201, summary="Job anlegen")
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


@router.get("/jobs/{job_id}", response_model=ImportPipelineJob, summary="Job abrufen")
async def get_job(
    job_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get an import pipeline job by ID."""
    store = _job_store(tenant_id)
    if job_id not in store:
        raise HTTPException(status_code=404, detail="Job not found")
    return store[job_id]


@router.post("/jobs/{job_id}/validate", response_model=ImportValidationResult, summary="Job validieren")
async def validate_job(
    job_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Run validation for an import pipeline job."""
    store = _job_store(tenant_id)
    if job_id not in store:
        raise HTTPException(status_code=404, detail="Job not found")

    job = store[job_id]

    total_rows = job.get("total_rows", 0)
    errors: list[str] = []
    warnings: list[str] = []

    if total_rows == 0:
        errors.append("Keine Zeilen zum Verarbeiten vorhanden")

    source_format = job.get("source_format", "")
    if source_format and source_format not in ("csv", "xlsx", "edi", "json", "xml"):
        errors.append(f"Unbekanntes Quellformat: {source_format}")

    if total_rows > 50000:
        warnings.append(f"Grosse Datei mit {total_rows} Zeilen — Import kann laenger dauern")

    target = job.get("target_entity", "")
    valid_targets = {"articles", "customers", "suppliers", "invoices", "orders", "inventory", "contacts"}
    if target and target not in valid_targets:
        warnings.append(f"Ziel-Entitaet '{target}' ist nicht in der Standardliste")

    is_valid = len(errors) == 0
    result = ImportValidationResult(
        is_valid=is_valid,
        error_count=len(errors),
        warning_count=len(warnings),
        errors=errors,
        warnings=warnings,
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

@router.get("/configs", response_model=list[ImportPipelineConfig], summary="Configs auflisten")
async def list_configs(tenant_id: str = Depends(get_tenant_id)):
    """List all import pipeline configs for the tenant."""
    store = _config_store(tenant_id)
    return list(store.values())
