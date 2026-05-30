from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.api.v1.schemas.base import BaseSchema


class SubResponse(BaseModel):
    id: str
    status: int
    body: Any


class BatchResponse(BaseModel):
    responses: list[SubResponse]

