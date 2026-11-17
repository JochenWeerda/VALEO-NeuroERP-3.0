"""Auto-generated domain schemas for einkauf kpis.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from typing import Optional

from pydantic import ConfigDict, Field


class EinkaufKpisOut(BaseSchema):
    """Response schema for einkauf kpis endpoints."""
    model_config = ConfigDict(extra="allow")

    offenes_bestellobligo_netto: Optional[float] = Field(
        default=None, description="Offene Bestellmenge freigegebener Bestellungen zum Bestellpreis (Stichtag, netto)")
