"""Pydantic schemas for the admin devices domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AdminDeviceIn(BaseModel):
    device_type: str = Field(..., pattern="^(printer|scanner)$")
    name: str = Field(..., min_length=1, max_length=120)
    vendor: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    station_code: str | None = Field(default=None, max_length=80)
    connection_uri: str | None = Field(default=None, max_length=255)
    capabilities: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class AdminDeviceOut(AdminDeviceIn):
    id: str
    created_at: datetime
    updated_at: datetime


class AdminDeviceMappingIn(BaseModel):
    device_id: str
    document_type: str = Field(..., min_length=1, max_length=60)
    process_code: str = Field(..., min_length=1, max_length=60)
    output_format: str = Field(default="pdf", pattern="^(pdf|zpl|epl|raw)$")
    copies: int = Field(default=1, ge=1, le=20)
    is_default: bool = False
    settings: dict[str, Any] = Field(default_factory=dict)


class AdminDeviceMappingOut(AdminDeviceMappingIn):
    id: str
    created_at: datetime
    updated_at: datetime


class AdminOutputTemplateCreate(BaseModel):
    template_code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=120)
    document_type: str = Field(..., min_length=1, max_length=60)
    output_format: str = Field(default="pdf", pattern="^(pdf|zpl|epl|html|txt)$")
    language: str | None = Field(default=None, max_length=10)
    content: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    change_note: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class AdminOutputTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    language: str | None = Field(default=None, max_length=10)
    content: str | None = None
    metadata: dict[str, Any] | None = None
    change_note: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class AdminOutputTemplateOut(BaseModel):
    id: str
    template_code: str
    name: str
    document_type: str
    output_format: str
    language: str | None
    is_active: bool
    current_version: int
    created_at: datetime
    updated_at: datetime


class AdminOutputTemplateVersionOut(BaseModel):
    id: str
    template_id: str
    version_no: int
    content: str
    metadata: dict[str, Any]
    change_note: str | None
    created_by: str | None
    created_at: datetime


class AdminOutputProfileIn(BaseModel):
    profile_code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=120)
    document_type: str = Field(..., min_length=1, max_length=60)
    process_code: str = Field(..., min_length=1, max_length=60)
    template_id: str | None = None
    device_id: str | None = None
    output_channel: str = Field(default="print", pattern="^(print|email|dms|pdf)$")
    archive_mode: str = Field(default="dms", pattern="^(none|dms|worm)$")
    archive_retention_days: int | None = Field(default=None, ge=0)
    is_active: bool = True
    settings: dict[str, Any] = Field(default_factory=dict)


class AdminOutputProfileOut(AdminOutputProfileIn):
    id: str
    created_at: datetime
    updated_at: datetime

