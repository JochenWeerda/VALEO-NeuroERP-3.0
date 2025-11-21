"""Schemas für Sanktionslistenscreening."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ScreeningSubject(BaseModel):
    name: str
    subject_type: str = Field(description="customer, supplier, employee, etc.")
    country: Optional[str] = None
    identifiers: dict[str, str] = Field(default_factory=dict)


class ScreeningRequest(BaseModel):
    tenant_id: str
    subject: ScreeningSubject


class ScreeningResult(BaseModel):
    list_name: str
    entry_id: str
    score: float
    matched_fields: dict[str, str] = Field(default_factory=dict)


class ScreeningResponse(BaseModel):
    status: str
    matches: List[ScreeningResult]
