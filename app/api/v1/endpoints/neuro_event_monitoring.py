"""Neuro Event Bus Monitoring Surfacing - NC-G8."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.infrastructure.eventbus.observability import event_bus_observer

router = APIRouter(prefix="/neuro/event-bus", tags=["neuro-event-bus", "monitoring"])


@router.get("/metrics")
async def get_event_bus_metrics() -> dict:
    return event_bus_observer.get_metrics()


@router.get("/health")
async def get_event_bus_health() -> dict:
    return event_bus_observer.get_health()


@router.get("/errors")
async def get_event_bus_errors(limit: int = Query(20, ge=1, le=200)) -> dict:
    return {
        "limit": limit,
        "errors": event_bus_observer.get_recent_errors(limit),
        "error_count": len(event_bus_observer.get_recent_errors(limit)),
    }
