"""Pydantic schemas for the case management api domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class CaseManagementOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class DecideRequest(BaseModel):
    decision: str = Field(..., description="GENEHMIGT | ABGELEHNT | ESKALIERT")
    decided_by: str = Field(...)
    comment: str = Field("")


class AssignRequest(BaseModel):
    user_id: str = Field(...)


class EscalateRequest(BaseModel):
    escalate_to: str = Field(...)
    reason: str = Field("")

