"""Security monitoring surfacing for violation and block events."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.security_observability import security_observer

router = APIRouter(prefix="/security/monitoring", tags=["security", "monitoring"])


@router.get("/metrics", summary="Security metrics abrufen",
    response_model=dict
)
async def get_security_metrics() -> dict:
    return security_observer.get_metrics()


@router.get("/health", summary="Security health abrufen",
    response_model=dict
)
async def get_security_health() -> dict:
    return security_observer.get_health()


@router.get("/events", summary="Security events abrufen",
    response_model=dict
)
async def get_security_events(
    limit: int = Query(20, ge=1, le=200),
    category: str | None = Query(None),
    outcome: str | None = Query(None),
) -> dict:
    events = security_observer.get_recent_events(limit, category=category, outcome=outcome)
    return {
        "limit": limit,
        "category": category,
        "outcome": outcome,
        "event_count": len(events),
        "events": events,
    }
