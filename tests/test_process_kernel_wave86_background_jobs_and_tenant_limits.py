from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import background_jobs, tenant_limits
from app.core.background_jobs import get_background_job_registry


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(background_jobs.router)
    app.include_router(tenant_limits.router)
    return TestClient(app)


def setup_function() -> None:
    get_background_job_registry().clear()


def test_background_job_queue_enqueue_dequeue_complete():
    client = _client()

    enqueue = client.post(
        "/process/background-jobs/enqueue",
        json={
            "typ": "REPORT_GENERATION",
            "angefordert_von": "user-1",
            "tenant_id": "tenant-a",
            "parameter": {"report_typ": "INTRASTAT"},
        },
    )
    assert enqueue.status_code == 201
    body = enqueue.json()
    job_id = body["job"]["job_id"]
    assert body["job"]["status"] == "PENDING"

    queue = client.get("/process/background-jobs/queue")
    assert queue.status_code == 200
    assert queue.json()["queue"]["pending_count"] == 1

    dequeue = client.post("/process/background-jobs/dequeue")
    assert dequeue.status_code == 200
    assert dequeue.json()["job"]["job_id"] == job_id
    assert dequeue.json()["job"]["status"] == "RUNNING"

    complete = client.post(
        f"/process/background-jobs/{job_id}/complete",
        json={"ergebnis_summary": "ok"},
    )
    assert complete.status_code == 200
    assert complete.json()["job"]["status"] == "COMPLETED"

    lookup = client.get(f"/process/background-jobs/{job_id}")
    assert lookup.status_code == 200
    assert lookup.json()["job"]["ergebnis_summary"] == "ok"


def test_background_job_listing_filters_by_tenant_and_status():
    client = _client()

    client.post(
        "/process/background-jobs/enqueue",
        json={
            "typ": "REPORT_GENERATION",
            "angefordert_von": "user-1",
            "tenant_id": "tenant-a",
        },
    )
    client.post(
        "/process/background-jobs/enqueue",
        json={
            "typ": "EDI_EXPORT",
            "angefordert_von": "user-2",
            "tenant_id": "tenant-b",
        },
    )

    listing = client.get("/process/background-jobs", params={"tenant_id": "tenant-a"})
    assert listing.status_code == 200
    assert listing.json()["job_count"] == 1
    assert listing.json()["jobs"][0]["tenant_id"] == "tenant-a"


def test_tenant_limit_overview_surfaces_cache_namespace_and_policies():
    client = _client()

    response = client.get("/process/tenant-limits/overview", params={"tenant_id": "tenant-a", "domain": "agrar"})
    assert response.status_code == 200
    body = response.json()
    assert body["overview"]["tenant_id"] == "tenant-a"
    assert body["overview"]["cache_namespace"] == "tenant:tenant-a"
    assert body["overview"]["policy_count"] >= 1
    assert body["overview"]["tenant_isolated_policies"] >= 1
    assert body["rate_limits"]


def test_tenant_limit_check_and_cache_config():
    client = _client()

    check = client.post(
        "/process/tenant-limits/rate-limits/check",
        json={
            "tenant_id": "tenant-a",
            "user_id": "user-1",
            "endpoint": "/api/v1/agrar/contracts",
            "domain": "agrar",
            "aktuelle_zaehlung": 5,
            "zeitfenster_sekunden": 60,
        },
    )
    assert check.status_code == 200
    assert check.json()["result"]["typ"] == "ERLAUBT"

    cache = client.get("/process/tenant-limits/cache-configs/tenant-a")
    assert cache.status_code == 200
    assert cache.json()["cache_config"]["tenant_id"] == "tenant-a"
    assert cache.json()["cache_namespace"] == "tenant:tenant-a"
