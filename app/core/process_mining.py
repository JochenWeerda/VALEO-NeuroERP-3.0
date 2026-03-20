from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from app.core.iot_telemetry import DeviceManifest, DeviceStatus, TelemetryReading
from app.core.runtime_operations import ComponentHealth, RuntimeHealthReport


class ProjectionStatusEntryLike(Protocol):
    projection_key: str
    item_count: int
    cached: bool
    cursor_status: str | None
    cursor_source: str | None
    last_processed_event_id: str | None


class ProjectionStatusLike(Protocol):
    tenant_id: str
    projections: list[ProjectionStatusEntryLike]


MiningState = Literal["ready", "lagging", "cache-only", "unknown"]


class ProcessMiningTrace(BaseModel):
    projection_key: str
    item_count: int = 0
    cached: bool = False
    cursor_status: str | None = None
    cursor_source: str | None = None
    last_event_processed: str | None = None
    state: MiningState = "unknown"
    schema_version: int = 1


class ProcessMiningBottleneck(BaseModel):
    bottleneck_id: str
    source_type: str
    source_key: str
    severity: str
    detail: str
    schema_version: int = 1


class ProcessObservabilitySignal(BaseModel):
    signal_id: str
    source_type: str
    source_key: str
    severity: Literal["healthy", "warning", "critical"]
    process_context: str | None = None
    detail: str
    schema_version: int = 1


class ProcessMiningReport(BaseModel):
    tenant_id: str
    traces: list[ProcessMiningTrace] = Field(default_factory=list)
    observability_signals: list[ProcessObservabilitySignal] = Field(default_factory=list)
    bottlenecks: list[ProcessMiningBottleneck] = Field(default_factory=list)
    ready_count: int = 0
    lagging_count: int = 0
    cache_only_count: int = 0
    unknown_count: int = 0
    warning_signal_count: int = 0
    critical_signal_count: int = 0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class ProcessMiningProcessSummary(BaseModel):
    projection_key: str
    item_count: int
    state: MiningState
    bottleneck_count: int = 0
    bottleneck_severity: str = "none"
    cached: bool = False
    cursor_status: str | None = None
    cursor_source: str | None = None
    last_event_processed: str | None = None
    schema_version: int = 1


class ProcessMiningDrilldown(BaseModel):
    projection_key: str
    trace: ProcessMiningTrace | None = None
    bottlenecks: list[ProcessMiningBottleneck] = Field(default_factory=list)
    signals: list[ProcessObservabilitySignal] = Field(default_factory=list)
    schema_version: int = 1


def build_process_mining_report(
    projection_status: ProjectionStatusLike,
    runtime_report: RuntimeHealthReport,
    device_manifests: list[DeviceManifest] | None = None,
    latest_readings: list[TelemetryReading] | None = None,
) -> ProcessMiningReport:
    traces = [_trace_from_projection(entry) for entry in projection_status.projections]
    observability_signals = _build_observability_signals(
        device_manifests=device_manifests or [],
        latest_readings=latest_readings or [],
    )
    bottlenecks = _build_bottlenecks(traces, runtime_report, observability_signals)
    return ProcessMiningReport(
        tenant_id=projection_status.tenant_id,
        traces=traces,
        observability_signals=observability_signals,
        bottlenecks=bottlenecks,
        ready_count=sum(1 for trace in traces if trace.state == "ready"),
        lagging_count=sum(1 for trace in traces if trace.state == "lagging"),
        cache_only_count=sum(1 for trace in traces if trace.state == "cache-only"),
        unknown_count=sum(1 for trace in traces if trace.state == "unknown"),
        warning_signal_count=sum(1 for signal in observability_signals if signal.severity == "warning"),
        critical_signal_count=sum(1 for signal in observability_signals if signal.severity == "critical"),
    )


def build_process_mining_top_processes(
    report: ProcessMiningReport,
    limit: int = 10,
) -> list[ProcessMiningProcessSummary]:
    bottleneck_counts: dict[str, int] = {}
    bottleneck_severity_by_projection: dict[str, str] = {}
    for bottleneck in report.bottlenecks:
        if bottleneck.source_type != "projection":
            continue
        bottleneck_counts[bottleneck.source_key] = bottleneck_counts.get(bottleneck.source_key, 0) + 1
        current = bottleneck_severity_by_projection.get(bottleneck.source_key, "none")
        if current == "high":
            continue
        if bottleneck.severity == "high":
            bottleneck_severity_by_projection[bottleneck.source_key] = "high"
        elif bottleneck.severity == "medium" and current != "high":
            bottleneck_severity_by_projection[bottleneck.source_key] = "medium"
        else:
            bottleneck_severity_by_projection.setdefault(bottleneck.source_key, bottleneck.severity)

    summaries = [
        ProcessMiningProcessSummary(
            projection_key=trace.projection_key,
            item_count=trace.item_count,
            state=trace.state,
            bottleneck_count=bottleneck_counts.get(trace.projection_key, 0),
            bottleneck_severity=bottleneck_severity_by_projection.get(trace.projection_key, "none"),
            cached=trace.cached,
            cursor_status=trace.cursor_status,
            cursor_source=trace.cursor_source,
            last_event_processed=trace.last_event_processed,
        )
        for trace in report.traces
    ]
    summaries.sort(key=lambda item: (-item.bottleneck_count, -item.item_count, item.projection_key))
    return summaries[:limit]


def build_process_mining_drilldown(
    report: ProcessMiningReport,
    projection_key: str,
) -> ProcessMiningDrilldown:
    trace = next((item for item in report.traces if item.projection_key == projection_key), None)
    bottlenecks = [item for item in report.bottlenecks if item.source_key == projection_key]
    signals = [item for item in report.observability_signals if item.source_key == projection_key]
    return ProcessMiningDrilldown(
        projection_key=projection_key,
        trace=trace,
        bottlenecks=bottlenecks,
        signals=signals,
    )


def _trace_from_projection(entry) -> ProcessMiningTrace:
    state: MiningState
    cursor_status = (entry.cursor_status or "").lower()
    if cursor_status in {"pending-replay", "replaying", "lagging"}:
        state = "lagging"
    elif entry.cursor_status or entry.cursor_source or entry.last_processed_event_id:
        state = "ready"
    elif entry.cached:
        state = "cache-only"
    else:
        state = "unknown"

    return ProcessMiningTrace(
        projection_key=entry.projection_key,
        item_count=entry.item_count,
        cached=entry.cached,
        cursor_status=entry.cursor_status,
        cursor_source=entry.cursor_source,
        last_event_processed=entry.last_processed_event_id,
        state=state,
    )


def _build_bottlenecks(
    traces: list[ProcessMiningTrace],
    runtime_report: RuntimeHealthReport,
    observability_signals: list[ProcessObservabilitySignal],
) -> list[ProcessMiningBottleneck]:
    bottlenecks: list[ProcessMiningBottleneck] = []

    for trace in traces:
        if trace.state != "lagging":
            continue
        bottlenecks.append(
            ProcessMiningBottleneck(
                bottleneck_id=f"projection:{trace.projection_key}",
                source_type="projection",
                source_key=trace.projection_key,
                severity="high",
                detail=f"Cursor status {trace.cursor_status or 'unknown'} blocks clean replay progress",
            )
        )
    for component in runtime_report.components:
        if component.health == ComponentHealth.HEALTHY:
            continue
        bottlenecks.append(
            ProcessMiningBottleneck(
                bottleneck_id=f"component:{component.component_id}",
                source_type="runtime_component",
                source_key=component.component_id,
                severity="high" if component.health == ComponentHealth.UNHEALTHY else "medium",
                detail=f"Runtime component health is {component.health.value}",
            )
        )
    for signal in observability_signals:
        if signal.severity == "healthy":
            continue
        bottlenecks.append(
            ProcessMiningBottleneck(
                bottleneck_id=f"observability:{signal.source_key}",
                source_type="observability",
                source_key=signal.source_key,
                severity="high" if signal.severity == "critical" else "medium",
                detail=signal.detail,
            )
        )
    return bottlenecks


def _build_observability_signals(
    device_manifests: list[DeviceManifest],
    latest_readings: list[TelemetryReading],
) -> list[ProcessObservabilitySignal]:
    latest_reading_by_device = {reading.device_id: reading for reading in latest_readings}
    signals: list[ProcessObservabilitySignal] = []

    for manifest in device_manifests:
        latest_reading = latest_reading_by_device.get(manifest.device_id)
        severity: Literal["healthy", "warning", "critical"] = "healthy"
        detail = f"Device status is {manifest.status.value}"

        if manifest.status == DeviceStatus.error:
            severity = "critical"
        elif manifest.status in {DeviceStatus.offline, DeviceStatus.calibrating}:
            severity = "warning"

        if latest_reading is not None:
            detail += f"; latest reading quality is {latest_reading.quality}"
            if latest_reading.quality == "bad":
                severity = "critical"
            elif latest_reading.quality == "uncertain" and severity == "healthy":
                severity = "warning"

        signals.append(
            ProcessObservabilitySignal(
                signal_id=f"device:{manifest.device_id}",
                source_type="device",
                source_key=manifest.device_id,
                severity=severity,
                process_context=manifest.process_context,
                detail=detail,
            )
        )
    return signals
