"""Pydantic schemas for the agribusiness domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class FarmerResponse(BaseModel):
    id: str
    farmerNumber: str
    firstName: str
    lastName: str
    fullName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    farmerType: str
    status: str
    portalAccessEnabled: bool
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FarmerListResponse(BaseModel):
    items: List[FarmerResponse]
    total: int


class DeleteFarmerRequest(BaseModel):
    reason: str

