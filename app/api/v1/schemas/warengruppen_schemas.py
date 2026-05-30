"""Pydantic schemas for the warengruppen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class HauptwarengruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str


class HauptwarengruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    aktiv: bool
    created_at: datetime


class OberwarengruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    haupt_id: str


class OberwarengruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    haupt_id: str
    aktiv: bool
    created_at: datetime


class WarengruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    ober_id: str


class WarengruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    ober_id: str
    aktiv: bool
    created_at: datetime


class WarengruppeHierarchieOut(BaseModel):
    warengruppe: WarengruppeOut
    oberwarengruppe: OberwarengruppeOut
    hauptwarengruppe: HauptwarengruppeOut

