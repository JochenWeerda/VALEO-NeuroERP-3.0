from __future__ import annotations

import time
from typing import Optional


class CircuitBreaker:
    def __init__(self, failure_threshold: int, open_seconds: int) -> None:
        self.failure_threshold = failure_threshold
        self.open_seconds = open_seconds
        self.failures = 0
        self.open_until: Optional[float] = None

    @property
    def is_open(self) -> bool:
        if self.open_until is None:
            return False
        if time.monotonic() >= self.open_until:
            # Half-open: reset and allow a trial
            self.failures = 0
            self.open_until = None
            return False
        return True

    def record_success(self) -> None:
        self.failures = 0
        self.open_until = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.open_until = time.monotonic() + self.open_seconds

