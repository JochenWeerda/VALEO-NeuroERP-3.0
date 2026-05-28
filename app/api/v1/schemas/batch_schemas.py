"""Pydantic schemas for the batch domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class SubRequest(BaseModel):
    id: str = Field(description="Client-assigned correlation id")
    path: str = Field(description="Relative API path, e.g. /api/v1/contacts?skip=0&limit=25")

    @field_validator("path")
    @classmethod
    def _validate_path(cls, v: str) -> str:
        if not v.startswith(ALLOWED_PATH_PREFIX):
            raise ValueError(f"Only paths starting with {ALLOWED_PATH_PREFIX} are allowed")
        return v


class BatchRequest(BaseModel):
    requests: list[SubRequest] = Field(max_length=MAX_SUBREQUESTS)


class SubResponse(BaseModel):
    id: str
    status: int
    body: Any


class BatchResponse(BaseModel):
    responses: list[SubResponse]

