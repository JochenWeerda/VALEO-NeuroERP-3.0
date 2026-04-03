from __future__ import annotations

from app.services.security_observability import SecurityObservability


def test_security_observability_persists_events_to_append_only_file(tmp_path):
    log_path = tmp_path / "security-events.jsonl"
    observer = SecurityObservability(
        persist_enabled=True,
        storage_path=log_path,
    )
    observer.reset()

    observer.record_event(
        category="outbound_http",
        outcome="blocked",
        severity="warning",
        message="Blocked localhost target",
        tenant_id=None,
        details={"target": "http://127.0.0.1"},
    )

    assert log_path.exists() is True

    reloaded = SecurityObservability(
        persist_enabled=True,
        storage_path=log_path,
    )
    metrics = reloaded.get_metrics()
    events = reloaded.get_recent_events(limit=10)

    assert metrics["event_count"] == 1
    assert metrics["by_category"]["outbound_http"] == 1
    assert events[0]["details"]["target"] == "http://127.0.0.1"
