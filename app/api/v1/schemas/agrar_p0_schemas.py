"""Auto-generated domain schemas for agrar p0.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class AgrarP0Out(BaseSchema):
    """Response schema for agrar p0 endpoints."""
    model_config = ConfigDict(extra="allow")
