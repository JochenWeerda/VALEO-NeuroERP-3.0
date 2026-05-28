"""Auto-generated domain schemas for ers settlement.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class ErsSettlementOut(BaseSchema):
    """Response schema for ers settlement endpoints."""
    model_config = ConfigDict(extra="allow")
