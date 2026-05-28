"""Auto-generated domain schemas for portal shop.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class PortalShopOut(BaseSchema):
    """Response schema for portal shop endpoints."""
    model_config = ConfigDict(extra="allow")
