from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.core.process_mining import (
    ProcessMiningBottleneck,
    ProcessMiningReport,
    ProcessMiningTrace,
    ProcessObservabilitySignal,
)


class ProcessMiningObservationEntry(BaseModel):
    projection_key: str
    risk_score: int
    state: str
    item_count: int
    bottleneck_count: int
    observability_signal_count: int
    detail: str
    recommended_action: str
    trace: ProcessMiningTrace
    bottlenecks: list[ProcessMiningBottleneck] = Field(default_factory=list)
    observability_signals: list[ProcessObservabilitySignal] = Field(default_factory=list)
    schema_version: int = 1


class ProcessMiningObservationReadModel(BaseModel):
    tenant_id: str
    top_n: int
    total_traces: int
    ready_count: int
    lagging_count: int
    cache_only_count: int
    unknown_count: int
    selected_projection_key: str | None = None
    selected_process: ProcessMiningObservationEntry | None = None
    top_processes: list[ProcessMiningObservationEntry] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


def _state_score(state: str) -> int:
    return {
        "lagging": 100,
        "unknown": 70,
        "cache-only": 55,
        "ready": 25,
    }.get(state, 40)


def _recommended_action(state: str, bottleneck_count: int) -> str:
    if state == "lagging":
        return "Replay- oder Cursor-Rueckstand pruefen und priorisieren"
    if state == "cache-only":
        return "Projection persistieren und Rebuild pfad validieren"
    if state == "unknown":
        return "Projection-Wiring, Events und Observer-Signale analysieren"
    if bottleneck_count > 0:
        return "Aktuelle Bottlenecks beobachten und Drilldown verfolgen"
    return "Weiter beobachten und in den Top-Prozessen belassen"


def _signals_for_trace(
    trace: ProcessMiningTrace,
    observability_signals: list[ProcessObservabilitySignal],
) -> list[ProcessObservabilitySignal]:
    matches: list[ProcessObservabilitySignal] = []
    for signal in observability_signals:
        if signal.process_context == trace.projection_key:
            matches.append(signal)
    return matches


def _bottlenecks_for_trace(
    trace: ProcessMiningTrace,
    bottlenecks: list[ProcessMiningBottleneck],
) -> list[ProcessMiningBottleneck]:
    return [
        bottleneck
        for bottleneck in bottlenecks
        if bottleneck.source_type == "projection" and bottleneck.source_key == trace.projection_key
    ]


def build_process_mining_observation_read_model(
    report: ProcessMiningReport,
    top_n: int = 10,
    selected_projection_key: str | None = None,
) -> ProcessMiningObservationReadModel:
    entries: list[ProcessMiningObservationEntry] = []

    for trace in report.traces:
        bottlenecks = _bottlenecks_for_trace(trace, report.bottlenecks)
        signals = _signals_for_trace(trace, report.observability_signals)
        risk_score = (
            _state_score(trace.state)
            + min(trace.item_count, 50)
            + (len(bottlenecks) * 25)
            + (len(signals) * 10)
        )
        entries.append(
            ProcessMiningObservationEntry(
                projection_key=trace.projection_key,
                risk_score=risk_score,
                state=trace.state,
                item_count=trace.item_count,
                bottleneck_count=len(bottlenecks),
                observability_signal_count=len(signals),
                detail=(
                    f"State={trace.state}, items={trace.item_count}, "
                    f"bottlenecks={len(bottlenecks)}, signals={len(signals)}"
                ),
                recommended_action=_recommended_action(trace.state, len(bottlenecks)),
                trace=trace,
                bottlenecks=bottlenecks,
                observability_signals=signals,
            )
        )

    entries.sort(
        key=lambda entry: (
            entry.risk_score,
            entry.bottleneck_count,
            entry.item_count,
            entry.projection_key,
        ),
        reverse=True,
    )
    top_processes = entries[: max(top_n, 0)]
    selected_process = None
    if selected_projection_key:
        selected_process = next(
            (entry for entry in entries if entry.projection_key == selected_projection_key),
            None,
        )

    return ProcessMiningObservationReadModel(
        tenant_id=report.tenant_id,
        top_n=top_n,
        total_traces=len(report.traces),
        ready_count=report.ready_count,
        lagging_count=report.lagging_count,
        cache_only_count=report.cache_only_count,
        unknown_count=report.unknown_count,
        selected_projection_key=selected_projection_key,
        selected_process=selected_process,
        top_processes=top_processes,
    )
