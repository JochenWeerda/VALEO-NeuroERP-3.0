"""Pydantic schemas for the budget planning domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class BudgetPlanningOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class BudgetPlanCreate(BaseModel):
    plan_year: int
    plan_name: str
    status: str = "ENTWURF"


class BudgetLineCreate(BaseModel):
    kostenstelle_id: Optional[str] = None
    account_id: str
    period_month: int = Field(..., ge=1, le=12)
    budgeted_amount: Decimal


class BudgetLineUpdate(BaseModel):
    budgeted_amount: Optional[Decimal] = None
    period_month: Optional[int] = Field(None, ge=1, le=12)

