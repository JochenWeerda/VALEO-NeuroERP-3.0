from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.neuro_event_monitoring import router
from app.infrastructure.eventbus.observability import event_bus_observer


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


def test_event_bus_metrics_endpoint():
    event_bus_observer.reset()
    event_bus_observer.record_event_received("order.state_changed")
    event_bus_observer.record_event_processed("order.state_changed", "handle_order", 12.5)

    response = _client().get("/api/v1/neuro/event-bus/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["events_received"] == 1
    assert body["events_processed"] == 1
    assert body["by_type"]["order.state_changed"] == 1


def test_event_bus_health_endpoint():
    event_bus_observer.reset()
    event_bus_observer.record_event_received("invoice.created")
    event_bus_observer.record_dlq_entry("invoice.created")

    response = _client().get("/api/v1/neuro/event-bus/health")

    assert response.status_code == 200
    assert response.json()["status"] == "warning"


def test_event_bus_errors_endpoint_honors_limit():
    event_bus_observer.reset()
    for idx in range(5):
        event_bus_observer.record_event_failed("test", f"error-{idx}")

    response = _client().get("/api/v1/neuro/event-bus/errors?limit=3")

    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 3
    assert body["error_count"] == 3
    assert len(body["errors"]) == 3
    assert body["errors"][-1]["error"] == "error-4"
