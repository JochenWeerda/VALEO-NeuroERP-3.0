"""EventBusObserver erhoeht Prometheus-Counter parallel zu In-Memory-Metriken."""

from __future__ import annotations

from prometheus_client import REGISTRY

from app.infrastructure.eventbus.observability import EventBusObserver


def _sample(name: str) -> float:
    v = REGISTRY.get_sample_value(name)
    return 0.0 if v is None else float(v)


def test_event_bus_observer_increments_prometheus_counters() -> None:
    o = EventBusObserver()

    r0 = _sample("valeo_event_bus_events_received_total")
    o.record_event_received("t.test")
    assert _sample("valeo_event_bus_events_received_total") == r0 + 1.0

    p0 = _sample("valeo_event_bus_events_processed_total")
    o.record_event_processed("t.test", "h1", 1.0)
    assert _sample("valeo_event_bus_events_processed_total") == p0 + 1.0

    f0 = _sample("valeo_event_bus_events_failed_total")
    o.record_event_failed("t.test", "err")
    assert _sample("valeo_event_bus_events_failed_total") == f0 + 1.0

    d0 = _sample("valeo_event_bus_dlq_entries_total")
    o.record_dlq_entry("t.test")
    assert _sample("valeo_event_bus_dlq_entries_total") == d0 + 1.0
