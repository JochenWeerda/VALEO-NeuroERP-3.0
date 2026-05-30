"""Auto-generated domain schemas for agrar feldbuch."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class AgrarFeldbuchOut(BaseSchema):
    """Response schema for agrar feldbuch endpoints."""
    model_config = ConfigDict(extra="allow")
