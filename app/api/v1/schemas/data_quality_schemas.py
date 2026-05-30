"""Pydantic schemas for the data quality domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class DataQualityOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class RuleOut(BaseModel):
    id: str
    entity_type: str
    label: str
    rule_type: str


class ViolationOut(BaseModel):
    rule_id: str
    entity_type: str
    entity_id: str | None
    detail: str
    severity: str = "error"


class ValidationResultOut(BaseModel):
    entity_type: str
    violations: list[ViolationOut]
    total_count: int


class ValidateRequest(BaseModel):
    entity_types: list[str] | None = Field(default=None, description="Entity-Typen zu prüfen; leer = alle")

