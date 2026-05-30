"""Pydantic schemas for the master data domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class MasterDataOut(BaseSchema):
    id: str
    category: str
    code: str
    label: str
    sort_order: int = 0


class MasterDataCreate(BaseModel):
    category: str
    code: str
    label: str
    sort_order: int = 0


class DispatcherOut(BaseSchema):
    id: str
    name: str
    code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class DispatcherCreate(BaseModel):
    name: str
    code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

