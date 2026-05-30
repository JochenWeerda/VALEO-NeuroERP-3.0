"""Auto-generated domain schemas for partiestamm."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class PartiestammOut(BaseSchema):
    """Response schema for partiestamm endpoints."""
    model_config = ConfigDict(extra="allow")
