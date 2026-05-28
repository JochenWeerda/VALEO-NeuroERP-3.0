"""Auto-generated domain schemas for crm account hierarchy.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class CrmAccountHierarchyOut(BaseSchema):
    """Response schema for crm account hierarchy endpoints."""
    model_config = ConfigDict(extra="allow")
