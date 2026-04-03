"""Small in-memory circuit breaker for external integration transport clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass
class IntegrationCircuitBreaker:
    """Simple integration-scoped breaker used by outbound adapter clients."""

    name: str
    failure_threshold: int = 3
    recovery_timeout_seconds: int = 30
    failure_count: int = 0
    opened_at: datetime | None = None
    state: str = field(default="closed")

    def allow_request(self, now: datetime | None = None) -> bool:
        current_time = now or datetime.now(UTC)
        if self.state != "open":
            return True
        if self.opened_at is None:
            return False
        if current_time - self.opened_at >= timedelta(seconds=self.recovery_timeout_seconds):
            self.state = "half_open"
            return True
        return False

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None
        self.state = "closed"

    def record_failure(self, now: datetime | None = None) -> None:
        current_time = now or datetime.now(UTC)
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.opened_at = current_time

