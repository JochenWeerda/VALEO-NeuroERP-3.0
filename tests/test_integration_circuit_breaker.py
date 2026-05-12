"""COV-INT-002: Tests fuer integration_circuit_breaker.py.

Abdeckung: allow_request, record_success, record_failure, state transitions.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import pytest

from app.integrations.services.integration_circuit_breaker import IntegrationCircuitBreaker


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_initial_state_closed():
    cb = IntegrationCircuitBreaker(name="test")
    assert cb.state == "closed"
    assert cb.failure_count == 0


def test_new_breaker_allows_requests():
    cb = IntegrationCircuitBreaker(name="test")
    assert cb.allow_request() is True


# ---------------------------------------------------------------------------
# record_failure → opening the breaker
# ---------------------------------------------------------------------------

def test_single_failure_does_not_open():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=3)
    cb.record_failure()
    assert cb.state == "closed"
    assert cb.failure_count == 1


def test_failures_at_threshold_open_breaker():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=3)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == "open"


def test_open_breaker_rejects_requests():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=2)
    cb.record_failure()
    cb.record_failure()
    assert cb.allow_request() is False


def test_failure_records_opened_at():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=1)
    before = datetime.now(UTC)
    cb.record_failure()
    assert cb.opened_at is not None
    assert cb.opened_at >= before


# ---------------------------------------------------------------------------
# Recovery: open → half_open after timeout
# ---------------------------------------------------------------------------

def test_half_open_after_recovery_timeout():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=1, recovery_timeout_seconds=30)
    cb.record_failure()
    future = cb.opened_at + timedelta(seconds=31)
    assert cb.allow_request(now=future) is True
    assert cb.state == "half_open"


def test_still_blocked_before_recovery_timeout():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=1, recovery_timeout_seconds=60)
    cb.record_failure()
    near_future = cb.opened_at + timedelta(seconds=10)
    assert cb.allow_request(now=near_future) is False


# ---------------------------------------------------------------------------
# record_success → closing the breaker
# ---------------------------------------------------------------------------

def test_record_success_closes_open_breaker():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=1)
    cb.record_failure()
    cb.record_success()
    assert cb.state == "closed"
    assert cb.failure_count == 0
    assert cb.opened_at is None


def test_record_success_resets_failure_count():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=5)
    for _ in range(3):
        cb.record_failure()
    cb.record_success()
    assert cb.failure_count == 0


# ---------------------------------------------------------------------------
# Custom threshold
# ---------------------------------------------------------------------------

def test_custom_failure_threshold_respected():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=1)
    cb.record_failure()
    assert cb.state == "open"


def test_allow_request_half_open_state():
    cb = IntegrationCircuitBreaker(name="test", failure_threshold=1, recovery_timeout_seconds=0)
    cb.record_failure()
    future = cb.opened_at + timedelta(seconds=1)
    result = cb.allow_request(now=future)
    assert result is True
