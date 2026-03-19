from __future__ import annotations

from app.services.scheduler_service import SchedulerService


def test_scheduler_service_exposes_heartbeat_status():
    service = SchedulerService()

    service._record_heartbeat()
    status = service.get_job_status()

    assert status["scheduler_id"] == "default_scheduler"
    assert status["worker_id"].startswith("scheduler-worker-")
    assert status["heartbeat"]["status"] == "ACTIVE"
    assert status["heartbeat"]["last_heartbeat"]["worker_klasse"] == "SCHEDULER"


def test_scheduler_service_tracks_active_job_tags_in_heartbeat():
    service = SchedulerService()

    result = service._execute_job(
        "test-job",
        lambda: {"success": True},
        "test job",
    )

    assert result["success"] is True
    heartbeat = service.get_heartbeat_status()
    assert heartbeat["last_heartbeat"]["running_job_ids"] == []
