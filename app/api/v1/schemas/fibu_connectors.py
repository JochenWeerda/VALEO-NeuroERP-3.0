"""Pydantic-Schemas für FIBU Connectors (Profile, Runs, Run-Items)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConnectorProfileBase(BaseModel):
    connector_type: str = Field(..., pattern="^(PAYROLL|ASSET_LEDGER)$")
    name: str = Field(..., max_length=120)
    is_default: bool = False
    settings: Dict[str, Any] = Field(default_factory=dict)
    mapping: Dict[str, Any] = Field(default_factory=dict)


class ConnectorProfileCreate(ConnectorProfileBase):
    pass


class ConnectorProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    is_default: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    mapping: Optional[Dict[str, Any]] = None
    version: Optional[int] = None


class ConnectorProfile(ConnectorProfileBase):
    id: str
    tenant_id: str
    version: int = 1
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class ConnectorRunSummary(BaseModel):
    id: str
    tenant_id: str
    connector_type: str
    direction: str = "IMPORT"
    profile_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    status: str
    counts: Optional[Dict[str, Any]] = None
    totals: Optional[Dict[str, Any]] = None
    error_summary: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class ConnectorRunItem(BaseModel):
    id: str
    run_id: str
    line_no: int
    item_type: str = "JOURNAL_ENTRY_LINE"
    payload: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[Any]] = None
    posted_entity_id: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class ImportUploadResponse(BaseModel):
    run_id: str
    status: str = "DRAFT"
    message: str = "Upload erfolgreich; Parse auslösen."


class IdempotencyBody(BaseModel):
    idempotency_key: Optional[str] = Field(None, max_length=255)
