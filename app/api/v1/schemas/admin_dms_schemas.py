"""Pydantic schemas for the admin dms domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class DmsStatusResponse(BaseModel):
    ok: bool
    configured: bool
    base: Optional[str] = None
    document_types: Optional[List[str]] = None
    metadata_types: Optional[List[str]] = None
    message: Optional[str] = None


class DmsConnectionRequest(BaseModel):
    base: str
    token: str


class DmsTestResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


class DmsBootstrapResponse(BaseModel):
    ok: bool
    created: Optional[int] = None
    updated: Optional[int] = None
    message: Optional[str] = None
    document_types: Optional[List[str]] = None
    metadata_types: Optional[List[str]] = None

