"""Response-Schemas fuer Reporting (SPEC-P1-06 Welle 10).

Ersetzt ``response_model=dict`` / ``list[dict]`` in:
- ``l3_report_catalog.py``
- ``query_center.py``
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── L3 Berichtskatalog ──────────────────────────────────────────────────────


class L3ReportCatalogItemOut(BaseSchema):
    id: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    legacy_menu: Optional[str] = None
    dimension: Optional[str] = None
    parameters: list[str] = Field(default_factory=list)
    sums: list[str] = Field(default_factory=list)
    export_formats: list[str] = Field(default_factory=list)
    drilldown: Optional[bool] = None


class L3ReportCatalogOut(BaseSchema):
    """``GET /l3-report-catalog``"""

    items: list[L3ReportCatalogItemOut] = Field(default_factory=list)
    count: Optional[int] = None


class L3BonusRunOut(BaseSchema):
    id: Optional[str] = None
    report_id: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    rate_pct: Optional[Decimal] = None
    status: Optional[str] = None
    total_basis: Optional[Decimal] = None
    total_bonus: Optional[Decimal] = None
    currency: Optional[str] = None
    correction_of: Optional[str] = None
    reason: Optional[str] = None
    actor: Optional[str] = None
    created_at: Optional[datetime] = None


class L3BonusRunListOut(BaseSchema):
    """``GET /l3-report-catalog/bonus-runs``"""

    items: list[L3BonusRunOut] = Field(default_factory=list)
    total: Optional[int] = None
    calculated: Optional[int] = None
    corrections: Optional[int] = None
    total_bonus: Optional[Decimal] = None


class L3BonusRunCreatedOut(BaseSchema):
    """``POST /l3-report-catalog/bonus-runs``"""

    id: Optional[str] = None
    status: Optional[str] = None
    lines: Optional[int] = None
    total_basis: Optional[Decimal] = None
    total_bonus: Optional[Decimal] = None


class L3BonusCorrectionOut(BaseSchema):
    """``POST /l3-report-catalog/bonus-runs/{id}/corrections``"""

    id: Optional[str] = None
    status: Optional[str] = None
    correction_of: Optional[str] = None
    total_bonus: Optional[Decimal] = None


class L3FactProjectedOut(BaseSchema):
    """``POST /l3-report-catalog/facts``"""

    id: Optional[str] = None
    payload_hash: Optional[str] = None


class L3ReportRowOut(BaseSchema):
    dimension_id: Optional[str] = None
    dimension_name: Optional[str] = None
    document_count: Optional[int] = None
    quantity: Optional[float] = None
    net_amount: Optional[float] = None
    gross_amount: Optional[float] = None
    currency: Optional[str] = None


class L3ReportTotalsOut(BaseSchema):
    document_count: Optional[int] = None
    quantity: Optional[float] = None
    net_amount: Optional[float] = None
    gross_amount: Optional[float] = None


class L3ReportRunOut(BaseSchema):
    """``GET /l3-report-catalog/{report_id}/run``"""

    report_id: Optional[str] = None
    title: Optional[str] = None
    items: list[L3ReportRowOut] = Field(default_factory=list)
    totals: Optional[L3ReportTotalsOut] = None
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class L3DrilldownRowOut(BaseSchema):
    """``GET /l3-report-catalog/{report_id}/drilldown``"""

    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    source_number: Optional[str] = None
    source_route: Optional[str] = None
    occurred_on: Optional[date] = None
    fact_type: Optional[str] = None
    quantity: Optional[float] = None
    net_amount: Optional[float] = None
    gross_amount: Optional[float] = None
    currency: Optional[str] = None
    payload_hash: Optional[str] = None


# ── Query-Center ────────────────────────────────────────────────────────────


class QueryCatalogItemOut(BaseSchema):
    id: Optional[str] = None
    fields: list[str] = Field(default_factory=list)
    aggregations: list[str] = Field(default_factory=list)


class QueryCatalogOut(BaseSchema):
    """``GET /query-center/catalog``"""

    items: list[QueryCatalogItemOut] = Field(default_factory=list)
    count: Optional[int] = None


class QueryDefinitionOut(BaseSchema):
    id: Optional[str] = None
    name: Optional[str] = None
    data_product_id: Optional[str] = None
    selected_fields: list[str] = Field(default_factory=list)
    filter_spec: dict[str, Any] = Field(default_factory=dict)
    aggregations: list[str] = Field(default_factory=list)
    is_favorite: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QueryDefinitionPageOut(BaseSchema):
    """``GET /query-center``"""

    items: list[QueryDefinitionOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class QueryPreviewOut(BaseSchema):
    """``POST /query-center/preview`` — Zeilen sind datenproduktabhaengig."""

    items: list[dict[str, Any]] = Field(default_factory=list)
    total: Optional[int] = None
    limit: Optional[int] = None
    truncated: Optional[bool] = None


class QueryDefinitionSavedOut(BaseSchema):
    """``POST /query-center`` und Import."""

    id: Optional[str] = None
    name: Optional[str] = None
    data_product_id: Optional[str] = None
    selected_fields: list[str] = Field(default_factory=list)
    filter_spec: dict[str, Any] = Field(default_factory=dict)
    aggregations: list[str] = Field(default_factory=list)
    is_favorite: Optional[bool] = None


class QueryExportBundleOut(BaseSchema):
    """``POST /query-center/{id}/export``"""

    schema_version: Optional[int] = None
    definition: Optional[QueryDefinitionSavedOut] = None
    algorithm: Optional[str] = None
    signature: Optional[str] = None
