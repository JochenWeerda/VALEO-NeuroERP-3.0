"""Central observability for security-relevant block and violation events."""

from __future__ import annotations

import json
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import settings


class SecurityObservability:
    def __init__(
        self,
        max_events: int = 500,
        *,
        persist_enabled: bool | None = None,
        storage_path: str | Path | None = None,
    ) -> None:
        self._max_events = max_events
        self._lock = Lock()
        self._persist_enabled = (
            settings.SECURITY_EVENT_PERSISTENCE_ENABLED
            if persist_enabled is None
            else bool(persist_enabled)
        )
        configured_path = storage_path or settings.SECURITY_EVENT_LOG_PATH
        self._storage_path = Path(configured_path)
        self.reset(clear_persisted=False)

    def reset(self, *, clear_persisted: bool = True) -> None:
        with self._lock:
            self._events: deque[dict[str, Any]] = deque(maxlen=self._max_events)
            self._by_category: Counter[str] = Counter()
            self._by_outcome: Counter[str] = Counter()
            self._by_severity: Counter[str] = Counter()
            if clear_persisted and self._persist_enabled and self._storage_path.exists():
                self._storage_path.unlink()

    def _persist_event(self, event: dict[str, Any]) -> None:
        if not self._persist_enabled:
            return
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            with self._storage_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True))
                handle.write("\n")
        except OSError:
            # Recording must stay non-blocking even if the append-only sink is unavailable.
            return

    def _load_persisted_events(self) -> list[dict[str, Any]]:
        if not self._persist_enabled or not self._storage_path.exists():
            with self._lock:
                return list(self._events)

        events: list[dict[str, Any]] = []
        try:
            with self._storage_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    payload = line.strip()
                    if not payload:
                        continue
                    try:
                        event = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(event, dict):
                        events.append(event)
        except OSError:
            with self._lock:
                return list(self._events)
        return events

    @staticmethod
    def _filter_events(
        events: list[dict[str, Any]],
        *,
        category: str | None = None,
        outcome: str | None = None,
    ) -> list[dict[str, Any]]:
        if category:
            events = [event for event in events if event.get("category") == category]
        if outcome:
            events = [event for event in events if event.get("outcome") == outcome]
        return events

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
        self._persist_event(event)
        return event

    def get_metrics(self) -> dict[str, Any]:
        events = self._load_persisted_events()
        by_category: Counter[str] = Counter()
        by_outcome: Counter[str] = Counter()
        by_severity: Counter[str] = Counter()
        for event in events:
            by_category[str(event.get("category") or "unknown")] += 1
            by_outcome[str(event.get("outcome") or "unknown")] += 1
            by_severity[str(event.get("severity") or "unknown")] += 1
        return {
            "event_count": len(events),
            "by_category": dict(by_category),
            "by_outcome": dict(by_outcome),
            "by_severity": dict(by_severity),
            "persistence_enabled": self._persist_enabled,
            "storage_path": str(self._storage_path) if self._persist_enabled else None,
        }

    def get_recent_events(
        self,
        limit: int = 20,
        *,
        category: str | None = None,
        outcome: str | None = None,
    ) -> list[dict[str, Any]]:
        events = self._filter_events(
            self._load_persisted_events(),
            category=category,
            outcome=outcome,
        )
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
            "persistence_enabled": metrics["persistence_enabled"],
        }


security_observer = SecurityObservability()
