"""
Event Bus Observability — NC-14
Metriken, Health-Checks und Monitoring fuer den Event Bus.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EventMetrics:
    """Aggregierte Event-Metriken fuer Observability."""
    events_received: int = 0
    events_processed: int = 0
    events_failed: int = 0
    events_dlq: int = 0
    avg_processing_ms: float = 0.0
    max_processing_ms: float = 0.0
    by_type: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    by_handler: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_event_at: str | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)


class EventBusObserver:
    """
    Sammelt Metriken und Health-Informationen zum Event Bus.
    Kann an Prometheus, OTEL oder beliebiges Monitoring exportiert werden.
    """

    def __init__(self, max_error_history: int = 100) -> None:
        self._metrics = EventMetrics()
        self._max_error_history = max_error_history
        self._processing_times: list[float] = []
        self._started_at = datetime.now(timezone.utc).isoformat()

    def record_event_received(self, event_type: str) -> None:
        self._metrics.events_received += 1
        self._metrics.by_type[event_type] += 1
        self._metrics.last_event_at = datetime.now(timezone.utc).isoformat()

    def record_event_processed(self, event_type: str, handler_name: str, duration_ms: float) -> None:
        self._metrics.events_processed += 1
        self._metrics.by_handler[handler_name] += 1
        self._processing_times.append(duration_ms)

        if len(self._processing_times) > 10_000:
            self._processing_times = self._processing_times[-5_000:]

        self._metrics.avg_processing_ms = sum(self._processing_times) / len(self._processing_times)
        self._metrics.max_processing_ms = max(self._metrics.max_processing_ms, duration_ms)

    def record_event_failed(self, event_type: str, error: str) -> None:
        self._metrics.events_failed += 1
        self._metrics.errors.append({
            "event_type": event_type,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if len(self._metrics.errors) > self._max_error_history:
            self._metrics.errors = self._metrics.errors[-self._max_error_history:]

    def record_dlq_entry(self, event_type: str) -> None:
        self._metrics.events_dlq += 1

    def get_metrics(self) -> dict[str, Any]:
        return {
            "events_received": self._metrics.events_received,
            "events_processed": self._metrics.events_processed,
            "events_failed": self._metrics.events_failed,
            "events_dlq": self._metrics.events_dlq,
            "avg_processing_ms": round(self._metrics.avg_processing_ms, 2),
            "max_processing_ms": round(self._metrics.max_processing_ms, 2),
            "by_type": dict(self._metrics.by_type),
            "by_handler": dict(self._metrics.by_handler),
            "last_event_at": self._metrics.last_event_at,
            "started_at": self._started_at,
            "error_count": len(self._metrics.errors),
        }

    def get_health(self) -> dict[str, Any]:
        total = self._metrics.events_received
        failed = self._metrics.events_failed
        dlq = self._metrics.events_dlq

        if total == 0:
            status = "idle"
        elif failed > total * 0.1:
            status = "degraded"
        elif dlq > 0:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "events_received": total,
            "events_failed": failed,
            "events_dlq": dlq,
            "success_rate": round((total - failed) / total * 100, 1) if total > 0 else 0.0,
            "last_event_at": self._metrics.last_event_at,
        }

    def get_recent_errors(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._metrics.errors[-limit:]

    def reset(self) -> None:
        self._metrics = EventMetrics()
        self._processing_times.clear()
        self._started_at = datetime.now(timezone.utc).isoformat()


event_bus_observer = EventBusObserver()
