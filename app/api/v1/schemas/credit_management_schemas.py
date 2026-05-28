"""Pydantic schemas for the credit management domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class CreditStatusOut(BaseModel):
    customer_id: str
    credit_limit: float
    current_exposure: float
    utilization_percent: float
    status: str  # OK | WARNING | BLOCKED
    warning_threshold_percent: float
    block_threshold_percent: float


class CreditLimitOut(BaseModel):
    id: str
    customer_id: str
    credit_limit_eur: float
    warning_threshold_percent: float
    block_threshold_percent: float
    tenant_id: str


class BlockedCustomerOut(BaseModel):
    customer_id: str
    credit_limit: float
    current_exposure: float
    utilization_percent: float

