"""Pydantic schemas for the admin mobile domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AdminStationOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tenant_id: str
    station_code: str
    name: str
    station_type: Optional[str] = None
    location_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AdminStationDeviceOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tenant_id: str
    station_id: str
    device_id: str
    device_role: str
    priority: int = 1
    is_fallback: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AdminRoutingRuleOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tenant_id: str
    rule_code: str
    name: str
    document_type: str
    process_code: str
    priority: int = 100
    is_active: bool = True
    station_id: Optional[str] = None
    device_id: Optional[str] = None
    output_profile_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AdminScanProfileOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tenant_id: str
    profile_code: str
    name: str
    source_type: Optional[str] = None
    target_action: str
    is_active: bool = True
    error_mode: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AdminMobileDeviceOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tenant_id: str
    device_code: str
    name: str
    device_type: Optional[str] = None
    ownership_type: Optional[str] = None
    platform: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    station_id: Optional[str] = None
    scan_profile_id: Optional[str] = None
    status: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AdminConnectorConfigOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tenant_id: str
    config_code: str
    name: str
    connector_type: str
    status: Optional[str] = None
    auth_type: Optional[str] = None
    rate_limit_per_minute: Optional[int] = None
    last_health_at: Optional[str] = None
    last_error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AdminConnectorEventOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tenant_id: str
    connector_id: str
    event_type: str
    status: Optional[str] = None
    message: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[str] = None
    created_at: Optional[str] = None


class JsonPayload(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)

