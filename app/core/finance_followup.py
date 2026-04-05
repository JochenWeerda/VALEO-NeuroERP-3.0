"""
Finance Follow-up Contracts — Wave 4 AP5

Explizite Backend-Contracts für Mahnwesen-Export und Lastschriften-Export.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class MahnwesenExportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    SEPA_XML = "sepa_xml"


class MahnwesenPreview(BaseModel):
    tenant_id: str
    open_items_count: int
    total_overdue_amount: float
    dunning_level_counts: dict[str, int]   # {"1": 5, "2": 3, "3": 1}
    export_ready: bool
    schema_version: int = 1


class MahnwesenExportRequest(BaseModel):
    tenant_id: str
    format: MahnwesenExportFormat
    dunning_level_filter: Optional[int] = None  # None = alle
    requested_by: str
    schema_version: int = 1


class MahnwesenExportResult(BaseModel):
    export_id: str
    tenant_id: str
    format: MahnwesenExportFormat
    record_count: int
    download_url: Optional[str] = None     # in Produktion: S3/DMS-URL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class LastschriftPreview(BaseModel):
    tenant_id: str
    direct_debit_run_id: str
    total_amount: float
    debitor_count: int
    mandate_valid_count: int
    mandate_expired_count: int
    sepa_ready: bool                        # alle Mandate gültig
    schema_version: int = 1


class LastschriftExportResult(BaseModel):
    export_id: str
    tenant_id: str
    direct_debit_run_id: str
    format: str = "sepa_xml"
    record_count: int
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class KassenfolgePreview(BaseModel):
    """Vorschau fuer POS-/Kassen-Folge (TSE/Compliance-Nachzug)."""

    tenant_id: str
    pos_compliance_records: int
    pending_export_count: int
    export_ready: bool
    schema_version: int = 1


class KassenfolgeExportResult(BaseModel):
    export_id: str
    tenant_id: str
    format: str = "zip"
    record_count: int
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1
