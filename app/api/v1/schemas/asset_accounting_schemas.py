"""Pydantic schemas for the asset accounting domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AssetAccountingOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class AssetCreate(BaseModel):
    asset_number: str
    description: str
    asset_class: str = Field(..., description="GEBAEUDE/FAHRZEUG/MASCHINE/IT/BUERO")
    acquisition_date: date
    acquisition_cost: Decimal
    useful_life_years: int = Field(..., gt=0)
    residual_value: Decimal = Decimal("0")
    depreciation_method: str = Field("LINEAR", description="LINEAR/DEGRESSIV")


class AssetUpdate(BaseModel):
    description: Optional[str] = None
    asset_class: Optional[str] = None
    residual_value: Optional[Decimal] = None
    useful_life_years: Optional[int] = None
    depreciation_method: Optional[str] = None


class DepreciationRunRequest(BaseModel):
    year: int
    month: int = Field(..., ge=1, le=12)
    dry_run: bool = False


class BudgetLineIn(BaseModel):
    pass  # reused name; not used here

