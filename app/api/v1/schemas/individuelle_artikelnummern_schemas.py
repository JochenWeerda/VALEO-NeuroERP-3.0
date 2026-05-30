"""Auto-generated domain schemas for individuelle artikelnummern."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class IndividuelleArtikelNrOut(BaseSchema):
    """Response schema for individuelle artikelnummern endpoints."""
    model_config = ConfigDict(extra="allow")
