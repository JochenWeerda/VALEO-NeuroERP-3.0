from __future__ import annotations

import asyncio

from app.api.v1.endpoints import rations_lifecycle
from app.agrar.rations.lifecycle import RationStatus
from app.core.screen_definitions import build_agrar_ration_detail_screen_definition


class DummyDb:
    def __init__(self) -> None:
        self.rollbacks = 0

    def rollback(self) -> None:
        self.rollbacks += 1


class StubLifecycleService:
    def __init__(self, *, status: str = "in_review", blockers: int = 0) -> None:
        self.status = status
        self.blockers = blockers
        self.transitions: list[dict[str, object]] = []

    def get_ration(self, ration_id: str, *, include_audit: bool) -> dict[str, object]:
        assert ration_id == "ration-1"
        assert include_audit is False
        return {
            "latest_version_id": "version-7",
            "latest_status": self.status,
            "latest_readiness_blockers": self.blockers,
        }

    def transition(self, **kwargs: object) -> dict[str, object]:
        self.transitions.append(kwargs)
        return {"superseded_version_ids": ["version-old"]}


def _run(monkeypatch, service: StubLifecycleService, action: str, body: dict[str, object]):
    monkeypatch.setattr(rations_lifecycle, "_service", lambda *_args: service)
    return asyncio.run(
        rations_lifecycle.run_ration_action(
            ration_id="ration-1",
            action_key=action,
            body=body,
            db=DummyDb(),
            tenant_id="tenant-1",
            user={"sub": "advisor-1", "roles": ["FUTTERMITTEL_ADMIN"]},
        )
    )


def test_screen_definition_wires_every_lifecycle_action_to_entity_endpoint() -> None:
    definition = build_agrar_ration_detail_screen_definition()
    actions = {item["key"]: item for item in definition["actions"]}
    expected = {"submit_review", "approve", "schedule", "activate", "retire", "archive"}

    assert expected == actions.keys()
    for key in expected:
        assert actions[key]["commandEndpoint"].endswith(f"/{{entity_id}}/actions/{key}")
        assert actions[key]["method"] == "POST"
        assert "inputFlow" not in actions[key]
    assert actions["approve"]["auditReasonRequired"] is True
    assert actions["activate"]["auditReasonRequired"] is True


def test_dry_run_previews_approval_without_mutation(monkeypatch) -> None:
    service = StubLifecycleService(status="in_review")
    result = _run(
        monkeypatch,
        service,
        "approve",
        {"_mode": "dryRun", "latest_status": "in_review"},
    )

    assert result.success is True
    assert result.mode == "dryRun"
    assert result.proposedChanges[0]["from"] == "in_review"
    assert result.proposedChanges[0]["to"] == "approved"
    assert service.transitions == []


def test_execute_delegates_to_canonical_lifecycle(monkeypatch) -> None:
    service = StubLifecycleService(status="active")
    result = _run(
        monkeypatch,
        service,
        "retire",
        {"latest_status": "active", "_auditReason": "Neue Ration uebernimmt"},
    )

    assert result.success is True
    assert result.affectedIds == ["version-7", "version-old"]
    assert service.transitions == [{
        "version_id": "version-7",
        "target": RationStatus.RETIRED,
        "expected_status": RationStatus.ACTIVE,
        "reason": "Neue Ration uebernimmt",
        "feeding_start": None,
    }]


def test_schedule_requires_feeding_start_and_never_mutates_on_failure(monkeypatch) -> None:
    service = StubLifecycleService(status="approved")
    result = _run(monkeypatch, service, "schedule", {"latest_status": "approved"})

    assert result.success is False
    assert result.validationErrors
    assert service.transitions == []


def test_stale_screen_status_is_rejected_before_execute(monkeypatch) -> None:
    service = StubLifecycleService(status="approved")
    result = _run(
        monkeypatch,
        service,
        "activate",
        {"latest_status": "in_review"},
    )

    assert result.success is False
    assert result.validationErrors[0]["field"] == "latest_status"
    assert service.transitions == []


def test_readiness_blocker_is_visible_in_dry_run(monkeypatch) -> None:
    service = StubLifecycleService(status="in_review", blockers=2)
    result = _run(
        monkeypatch,
        service,
        "approve",
        {"_mode": "validate", "latest_status": "in_review"},
    )

    assert result.success is False
    assert "OVERRIDE:" in result.validationErrors[0]["message"]
    assert service.transitions == []
