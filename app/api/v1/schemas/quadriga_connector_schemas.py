"""Auto-generated domain schemas for quadriga connector.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class QuadrigaConnectorOut(BaseSchema):
    """Response schema for quadriga connector endpoints."""
    model_config = ConfigDict(extra="allow")
