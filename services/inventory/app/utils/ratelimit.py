from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, Tuple


class TokenBucket:
    def __init__(self, capacity: int, refill_per_minute: int) -> None:
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate_per_sec = refill_per_minute / 60.0
        self.last_refill_ts = time.monotonic()

    def allow(self, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill_ts
        refill = elapsed * self.refill_rate_per_sec
        if refill > 0:
            self.tokens = min(self.capacity, self.tokens + refill)
            self.last_refill_ts = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class RateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = limit_per_minute
        self._buckets: Dict[str, TokenBucket] = {}

    def check(self, key: str) -> bool:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = TokenBucket(capacity=self.limit_per_minute, refill_per_minute=self.limit_per_minute)
            self._buckets[key] = bucket
        return bucket.allow(1)

