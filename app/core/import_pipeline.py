"""
Import Pipeline Standard — Wave 3 AP6
Standardisiertes Modell fuer CSV, EDI, OCR Import-Pipelines.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ImportFormat(str, Enum):
    csv = "csv"
    edifact = "edifact"
    ocr_pdf = "ocr_pdf"
    json = "json"
    xml_ubl = "xml_ubl"
    excel = "excel"


class ImportStage(str, Enum):
    received = "received"
    validated = "validated"
    staged = "staged"
    enriched = "enriched"
    posted = "posted"
    failed = "failed"
    rejected = "rejected"


class ImportValidationResult(BaseModel):
    is_valid: bool
    error_count: int = 0
    warning_count: int = 0
    errors: list[str] = []
    warnings: list[str] = []


class ImportPipelineJob(BaseModel):
    job_id: str
    tenant_id: str
    import_format: ImportFormat
    domain: str  # e.g. "finance", "agrar"
    entity_type: str  # e.g. "ap_invoice", "harvest_acceptance"
    stage: ImportStage = ImportStage.received
    total_rows: int = 0
    processed_rows: int = 0
    failed_rows: int = 0
    validation_result: ImportValidationResult | None = None
    source_reference: str | None = None
    created_at: str
    updated_at: str
    audit_trail: bool = True
    schema_version: int = 1


class ImportPipelineConfig(BaseModel):
    config_id: str
    tenant_id: str
    import_format: ImportFormat
    domain: str
    entity_type: str
    column_mappings: dict[str, str] = {}
    required_columns: list[str] = []
    validation_rules: list[str] = []
    auto_post: bool = False
    require_approval_before_post: bool = True
    schema_version: int = 1
