"""Pydantic schemas for the gap domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class GapOut(BaseSchema):
    """Typed response schema for GapOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class GapPipelineRequest(BaseModel):
    """Request-Modell für GAP-Pipeline-Ausführung"""
    year: int
    csv_path: Optional[str] = None
    batch_id: Optional[str] = None


class GapPipelineResponse(BaseModel):
    """Response-Modell für GAP-Pipeline-Ausführung"""
    success: bool
    message: str
    job_id: Optional[str] = None


class PipelineProgressResponse(BaseModel):
    """Response-Modell für Pipeline-Progress"""
    job_id: str
    year: int
    current_step: str
    progress: int
    total_steps: int
    percentage: int
    message: str
    status: str  # running, completed, error
    updated_at: str
    steps: Dict[str, Dict[str, Any]]

