"""Auto-generated domain schemas for vat codes.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class VatCodesOut(BaseSchema):
    """Response schema for vat codes endpoints."""
    model_config = ConfigDict(extra="allow")
