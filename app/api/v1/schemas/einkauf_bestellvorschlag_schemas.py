"""Auto-generated domain schemas for einkauf bestellvorschlag."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class EinkaufBestellvorschlagOut(BaseSchema):
    """Response schema for einkauf bestellvorschlag endpoints."""
    model_config = ConfigDict(extra="allow")
