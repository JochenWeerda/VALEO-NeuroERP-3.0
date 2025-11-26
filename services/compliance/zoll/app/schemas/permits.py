"""Schemas für Exportgenehmigungen."""

from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ExportPermitBase(BaseModel):
    tenant_id: str
    permit_number: str
    country_destination: str = Field(min_length=2, max_length=2)
    validity_start: date
    validity_end: date
    goods_description: str
    control_list_entries: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ExportPermitCreate(ExportPermitBase):
    pass


class ExportPermitUpdate(BaseModel):
    status: Optional[str] = None
    validity_end: Optional[date] = None
    metadata: Optional[dict] = None


class ExportPermitRead(ExportPermitBase):
    id: UUID
    status: str
