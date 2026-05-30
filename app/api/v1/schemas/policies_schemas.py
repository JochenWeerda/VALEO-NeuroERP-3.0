"""Pydantic schemas for the policies domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class UpsertRequest(BaseModel):
    """Upsert-Request (einzeln oder bulk)"""
    rules: List[Rule]


class DeleteRequest(BaseModel):
    """Delete-Request"""
    id: str


class TestRequest(BaseModel):
    """Test-Request (Simulator)"""
    alert: Alert
    roles: List[str]


class TestResponse(BaseModel):
    """Test-Response"""
    ok: bool
    decision: Decision
    override_resolution: PolicyOverrideResolution
    explainability: ExplainabilityView


class RestoreRequest(BaseModel):
    """Restore-Request (JSON-String der wiederherzustellenden Policies)."""
    json_payload: str = Field(..., alias="json", description="JSON-String der Policy-Daten")

