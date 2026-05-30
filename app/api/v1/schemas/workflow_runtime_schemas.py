"""Pydantic schemas for the workflow runtime domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class WorkflowRuntimeOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class CreateInstanceRequest(BaseModel):
    instance_id: str
    process_key: str
    definition_version: str
    aggregate_type: str
    aggregate_id: str
    context: dict[str, Any] = {}
    schema_version: int = 1


class CheckpointRequest(BaseModel):
    step_name: str
    state_snapshot: dict[str, Any]
    schema_version: int = 1

