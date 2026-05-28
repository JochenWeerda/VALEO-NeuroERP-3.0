"""Neuro Event Bus Monitoring Surfacing - NC-G8."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.infrastructure.eventbus.observability import event_bus_observer

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/neuro/event-bus", tags=["neuro-event-bus", "monitoring"])


_PROMETHEUS_COUNTERS = (
    "valeo_event_bus_events_received_total",
    "valeo_event_bus_events_processed_total",
    "valeo_event_bus_events_failed_total",
    "valeo_event_bus_dlq_entries_total",
)


@router.get("/metrics", summary="Event bus metrics abrufen",
    response_model=CompatFlexOut
)
async def get_event_bus_metrics() -> dict:
    out = event_bus_observer.get_metrics()
    out["prometheus"] = {
        "scrape_path": "/metrics",
        "counter_names": list(_PROMETHEUS_COUNTERS),
    }
    return out


@router.get("/health", summary="Event bus health abrufen",
    response_model=CompatFlexOut
)
async def get_event_bus_health() -> dict:
    return event_bus_observer.get_health()


@router.get("/errors", summary="Event bus errors abrufen",
    response_model=CompatFlexOut
)
async def get_event_bus_errors(limit: int = Query(20, ge=1, le=200)) -> dict:
    return {
        "limit": limit,
        "errors": event_bus_observer.get_recent_errors(limit),
        "error_count": len(event_bus_observer.get_recent_errors(limit)),
    }
