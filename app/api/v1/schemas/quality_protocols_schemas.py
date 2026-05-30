"""Pydantic schemas for the quality protocols domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class QualityProtocolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Output-Model für Qualitätsprotokoll."""
    id: str
    tenant_id: str
    harvest_acceptance_id: Optional[str] = None
    protocol_number: str
    version: int
    moisture_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight_kg_per_hl: Optional[float] = None
    protein_pct: Optional[float] = None
    mycotoxin_ppb: Optional[float] = None
    other_values: Optional[dict] = None
    source_type: Optional[str] = None
    source_device_id: Optional[str] = None
    source_file_name: Optional[str] = None
    is_final: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class QualityProtocolCreateIn(BaseModel):
    """Input-Model für Protokoll-Erstellung."""
    harvest_acceptance_id: Optional[str] = None
    protocol_number: Optional[str] = None
    moisture_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight_kg_per_hl: Optional[float] = None
    protein_pct: Optional[float] = None
    mycotoxin_ppb: Optional[float] = None
    other_values: Optional[dict] = None
    source_type: str = "manual"
    source_device_id: Optional[str] = None


class QualityProtocolUpdateIn(BaseModel):
    """Input-Model für Protokoll-Update."""
    moisture_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight_kg_per_hl: Optional[float] = None
    protein_pct: Optional[float] = None
    mycotoxin_ppb: Optional[float] = None
    other_values: Optional[dict] = None


class QualityProtocolFinalizeIn(BaseModel):
    """Input-Model für Protokoll-Finalisierung."""
    approved_by: str = Field(..., min_length=1)

