"""Pydantic schemas for the config service domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ConnectorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    connector_key: str
    connector_type: str
    display_name: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConnectorCreateIn(BaseModel):
    connector_key: str = Field(..., min_length=1, max_length=80)
    connector_type: str = Field(..., min_length=1, max_length=40)  # api, oauth2, cert, basic, file-drop, https, sftp, email, provider
    display_name: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool = True


class ConnectorUpdateIn(BaseModel):
    display_name: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None


class ReportingUnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    unit_key: str
    display_name: str
    connector_id: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReportingUnitCreateIn(BaseModel):
    unit_key: str = Field(..., min_length=1, max_length=80)
    display_name: str = Field(..., min_length=1, max_length=200)
    connector_id: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool = True


class ReportingUnitUpdateIn(BaseModel):
    display_name: Optional[str] = None
    connector_id: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    schedule_key: str
    display_name: str
    reporting_unit_id: Optional[str] = None
    cron_expr: Optional[str] = None
    lead_days: int
    use_workday_rule: bool
    output_format: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScheduleCreateIn(BaseModel):
    schedule_key: str = Field(..., min_length=1, max_length=80)
    display_name: str = Field(..., min_length=1, max_length=200)
    reporting_unit_id: Optional[str] = None
    cron_expr: Optional[str] = None
    lead_days: int = 5
    use_workday_rule: bool = False
    output_format: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool = True


class ScheduleUpdateIn(BaseModel):
    display_name: Optional[str] = None
    reporting_unit_id: Optional[str] = None
    cron_expr: Optional[str] = None
    lead_days: Optional[int] = None
    use_workday_rule: Optional[bool] = None
    output_format: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None

