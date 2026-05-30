"""Auto-generated domain schemas for versandprofile."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class VersandprofileOut(BaseSchema):
    """Response schema for versandprofile endpoints."""
    model_config = ConfigDict(extra="allow")
