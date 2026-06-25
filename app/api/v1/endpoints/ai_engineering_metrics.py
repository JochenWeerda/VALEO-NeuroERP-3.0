"""P2.2 — AI-Engineering-Metriken API."""

from __future__ import annotations

from fastapi import APIRouter
from typing import Any

from app.services.ai_engineering_metrics_service import ai_engineering_metrics_service

router = APIRouter(prefix="/ai-engineering/metrics", tags=["ai-engineering", "metrics"])


@router.get("/dashboard", summary="Vollstaendiges Metriken-Dashboard", response_model=dict[str, Any])
async def full_dashboard() -> dict[str, Any]:
    return ai_engineering_metrics_service.full_dashboard()


@router.get("/slices", summary="Slice-Metriken", response_model=list[dict[str, Any]])
async def slice_metrics() -> list[dict[str, Any]]:
    return ai_engineering_metrics_service.slice_metrics()


@router.get("/cycle-time", summary="Cycle-Time-Zusammenfassung", response_model=dict[str, Any])
async def cycle_time() -> dict[str, Any]:
    return ai_engineering_metrics_service.cycle_time_summary()


@router.get("/coverage", summary="Coverage-Zusammenfassung", response_model=dict[str, Any])
async def coverage() -> dict[str, Any]:
    return ai_engineering_metrics_service.coverage_summary()


@router.get("/gate-blockers", summary="Gate-Blocker-Zusammenfassung", response_model=dict[str, Any])
async def gate_blockers() -> dict[str, Any]:
    return ai_engineering_metrics_service.gate_blocker_summary()


@router.get("/rework", summary="Rework-Indikator", response_model=dict[str, Any])
async def rework() -> dict[str, Any]:
    return ai_engineering_metrics_service.rework_indicator()


@router.get("/owner-distribution", summary="Slice-Eigentuemer-Verteilung", response_model=dict[str, Any])
async def owner_distribution() -> dict[str, Any]:
    return ai_engineering_metrics_service.owner_distribution()
