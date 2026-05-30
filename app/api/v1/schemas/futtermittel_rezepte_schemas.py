"""Pydantic schemas for the futtermittel rezepte domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class FuttermittelRezeptOut(BaseSchema):
    """Typed response schema for FuttermittelRezeptOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class RezeptIn(BaseModel):
    recipe_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    tierart: str = "SONSTIGE"
    produktionsphase: str = "SONSTIGE"
    erstellt_von: Optional[str] = None


class IngredientIn(BaseModel):
    material_id: str = Field(..., min_length=1)
    anteil_percent: float = Field(..., gt=0, le=100)
    min_anteil: Optional[float] = None
    max_anteil: Optional[float] = None
    sort_order: int = 0

