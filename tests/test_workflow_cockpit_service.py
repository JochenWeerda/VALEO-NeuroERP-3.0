from datetime import datetime, timedelta, timezone

from app.services.workflow_cockpit_service import (
    WorkflowCockpitBlocker,
    WorkflowCockpitEvent,
    WorkflowCockpitService,
    WorkflowCockpitStatus,
    WorkflowEventKind,
    WorkflowReplayPermissionError,
)


def test_cockpit_lists_only_tenant_processes():
    service = WorkflowCockpitService()
    service.upsert_process(
        tenant_id="tenant-a",
        process_instance_id="wf-1",
        process_key="o2c.invoice",
        status=WorkflowCockpitStatus.RUNNING,
        correlation_id="corr-1",
    )
    service.upsert_process(
        tenant_id="tenant-b",
        process_instance_id="wf-2",
        process_key="o2c.invoice",
        status=WorkflowCockpitStatus.FAILED,
        correlation_id="corr-2",
    )

    result = service.list_processes(tenant_id="tenant-a")

    assert [item.process_instance_id for item in result] == ["wf-1"]


def test_external_blocker_is_not_treated_as_failed():
    service = WorkflowCockpitService()
    process = service.upsert_process(
        tenant_id="tenant-a",
        process_instance_id="wf-tse-1",
        process_key="pos.daily-close",
        status="blocked_external_gate",
        correlation_id="corr-tse",
        blockers=[
            WorkflowCockpitBlocker(
                blocker_id="blk-tse",
                blocker_type="external_gate",
                external_system="TSE",
                message="TSE signature timeout",
                retryable=True,
            )
        ],
    )

    assert process.status == WorkflowCockpitStatus.BLOCKED_EXTERNAL_GATE
    assert process.active_blockers[0].external_system == "TSE"
    assert process.replayable is True
    assert service.summary(tenant_id="tenant-a")["by_status"]["failed"] == 0


def test_events_are_returned_chronologically():
    service = WorkflowCockpitService()
    base = datetime(2026, 6, 23, 8, 0, tzinfo=timezone.utc)
    process = service.upsert_process(
        tenant_id="tenant-a",
        process_instance_id="wf-chronology",
        process_key="wms.lot-link",
        status="running",
        correlation_id="corr-chronology",
        events=[
            WorkflowCockpitEvent(
                event_id="evt-2",
                kind=WorkflowEventKind.DOMAIN_EVENT,
                message="second",
                occurred_at=base + timedelta(minutes=2),
            ),
            WorkflowCockpitEvent(
                event_id="evt-1",
                kind=WorkflowEventKind.DOMAIN_EVENT,
                message="first",
                occurred_at=base + timedelta(minutes=1),
            ),
        ],
    )

    messages = [event["message"] for event in process.to_dict()["events"]]

    assert messages.index("first") < messages.index("second")


def test_replay_requires_explicit_role():
    service = WorkflowCockpitService()
    service.upsert_process(
        tenant_id="tenant-a",
        process_instance_id="wf-failed",
        process_key="match",
        status="failed",
        correlation_id="corr-failed",
    )

    try:
        service.request_replay(
            tenant_id="tenant-a",
            process_instance_id="wf-failed",
            requested_by="operator",
            roles={"workflow:read"},
            reason="retry after source correction",
        )
    except WorkflowReplayPermissionError:
        pass
    else:
        raise AssertionError("Replay without workflow:replay must fail closed")


def test_replay_request_is_audited_for_replayable_process():
    service = WorkflowCockpitService()
    service.upsert_process(
        tenant_id="tenant-a",
        process_instance_id="wf-failed",
        process_key="match",
        status="failed",
        correlation_id="corr-failed",
    )

    event = service.request_replay(
        tenant_id="tenant-a",
        process_instance_id="wf-failed",
        requested_by="operator",
        roles={"workflow:replay"},
        reason="corrected mapping available",
    )
    process = service.get_process(tenant_id="tenant-a", process_instance_id="wf-failed")

    assert event.kind == WorkflowEventKind.REPLAY_REQUESTED
    assert process.events[-1].payload["reason"] == "corrected mapping available"


def test_completed_process_is_not_replayable():
    service = WorkflowCockpitService()
    service.upsert_process(
        tenant_id="tenant-a",
        process_instance_id="wf-completed",
        process_key="o2c.invoice",
        status="completed",
        correlation_id="corr-completed",
    )

    try:
        service.request_replay(
            tenant_id="tenant-a",
            process_instance_id="wf-completed",
            requested_by="operator",
            roles={"workflow:replay"},
            reason="should not replay terminal status",
        )
    except ValueError as exc:
        assert "not replayable" in str(exc)
    else:
        raise AssertionError("Completed process must not be replayable")
