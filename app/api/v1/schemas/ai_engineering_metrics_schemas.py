"""Response-Schemas fuer die AI-Engineering-Metriken (P2.2).

SPEC-P1-06 Welle 4: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/ai_engineering_metrics.py``.

Feldlisten aus ``ai_engineering_metrics_service``. Die Coverage-Auswertung hat
zwei Zweige: ohne ``coverage.xml`` liefert sie nur ``status`` mit einem Hinweis,
sonst die Kennzahlen.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class SliceMetricOut(BaseSchema):
    """Kennzahlen eines einzelnen Slice-YAML."""

    slice_id: Optional[str] = None
    title: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = Field(default=None, description="ISO-Datum")
    closed_at: Optional[str] = Field(default=None, description="ISO-Datum")
    cycle_time_days: Optional[float] = None
    has_tests: Optional[bool] = None
    has_all_harness_fields: Optional[bool] = Field(
        default=None, description="Alle sieben Vertrags-Ebenen im YAML vorhanden"
    )
    test_count: Optional[int] = None


class CycleTimeSummaryOut(BaseSchema):
    """``GET /ai-engineering/metrics/cycle-time``"""

    total_slices: Optional[int] = None
    completed_slices: Optional[int] = None
    avg_cycle_time_days: Optional[float] = None
    max_cycle_time_days: Optional[float] = None
    min_cycle_time_days: Optional[float] = None
    slices_without_tests: Optional[int] = None
    slices_missing_harness: Optional[int] = None


class CoverageSummaryOut(BaseSchema):
    """``GET /ai-engineering/metrics/coverage``.

    Ohne ``coverage.xml`` liefert der Service nur ``status`` mit einem Hinweis;
    die Kennzahlen bleiben dann leer.
    """

    status: Optional[str] = Field(
        default=None, description="Nur gesetzt, wenn coverage.xml fehlt"
    )
    total_files: Optional[int] = None
    avg_coverage_pct: Optional[float] = None
    files_below_50pct: Optional[int] = None
    files_below_70pct: Optional[int] = None
    top_3_lowest: list[tuple[str, float]] = Field(
        default_factory=list, description="Die drei schwaechsten Dateien als (Pfad, Prozent)"
    )


class GateBlockerSummaryOut(BaseSchema):
    """``GET /ai-engineering/metrics/gate-blockers`` — Heuristik aus dem Workboard."""

    workboard_open_items: Optional[int] = None
    external_gate_mentions: Optional[int] = None
    hinweis: Optional[str] = None


class ReworkDetailOut(BaseSchema):
    """Slice mit unvollstaendigem Harness oder ohne Tests."""

    slice_id: Optional[str] = None
    has_tests: Optional[bool] = None
    has_all_harness_fields: Optional[bool] = None


class ReworkIndicatorOut(BaseSchema):
    """``GET /ai-engineering/metrics/rework``"""

    slices_with_incomplete_harness_or_tests: Optional[int] = None
    details: list[ReworkDetailOut] = Field(default_factory=list)
    rework_rate_pct: Optional[float] = None


class MetricsDashboardOut(BaseSchema):
    """``GET /ai-engineering/metrics/dashboard`` — alle Teilauswertungen."""

    generated_at: Optional[str] = None
    cycle_time: Optional[CycleTimeSummaryOut] = None
    coverage: Optional[CoverageSummaryOut] = None
    gate_blockers: Optional[GateBlockerSummaryOut] = None
    rework: Optional[ReworkIndicatorOut] = None
    owner_distribution: dict[str, int] = Field(
        default_factory=dict, description="Anzahl Slices je Eigentuemer"
    )
