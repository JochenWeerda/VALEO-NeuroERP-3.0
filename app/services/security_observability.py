"""Central in-memory observability for security-relevant block and violation events."""

from __future__ import annotations

from collections import Counter, deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any


class SecurityObservability:
    def __init__(self, max_events: int = 500) -> None:
        self._max_events = max_events
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._events: deque[dict[str, Any]] = deque(maxlen=self._max_events)
            self._by_category: Counter[str] = Counter()
            self._by_outcome: Counter[str] = Counter()
            self._by_severity: Counter[str] = Counter()

    def record_event(
        self,
        *,
        category: str,
        outcome: str,
        severity: str,
        message: str,
        tenant_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": category,
            "outcome": outcome,
            "severity": severity,
            "message": message,
            "tenant_id": tenant_id,
            "details": details or {},
        }
        with self._lock:
            self._events.append(event)
            self._by_category[category] += 1
            self._by_outcome[outcome] += 1
            self._by_severity[severity] += 1
        return event

    def get_metrics(self) -> dict[str, Any]:
        with self._lock:
            return {
                "event_count": len(self._events),
                "by_category": dict(self._by_category),
                "by_outcome": dict(self._by_outcome),
                "by_severity": dict(self._by_severity),
            }

    def get_recent_events(
        self,
        limit: int = 20,
        *,
        category: str | None = None,
        outcome: str | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            events = list(self._events)
        if category:
            events = [event for event in events if event["category"] == category]
        if outcome:
            events = [event for event in events if event["outcome"] == outcome]
        return events[-limit:]

    def get_health(self) -> dict[str, Any]:
        metrics = self.get_metrics()
        blocked = metrics["by_outcome"].get("blocked", 0)
        denied = metrics["by_outcome"].get("denied", 0)
        critical = metrics["by_severity"].get("critical", 0)

        status = "ok"
        if blocked or denied:
            status = "warning"
        if critical:
            status = "critical"

        return {
            "status": status,
            "event_count": metrics["event_count"],
            "blocked_count": blocked,
            "denied_count": denied,
            "critical_count": critical,
        }


security_observer = SecurityObservability()
