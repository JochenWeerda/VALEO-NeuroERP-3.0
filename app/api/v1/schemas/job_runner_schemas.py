"""Pydantic schemas for the job runner domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


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

