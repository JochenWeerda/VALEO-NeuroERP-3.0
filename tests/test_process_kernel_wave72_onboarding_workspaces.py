"""
Wave 72 - Knowledge-backed onboarding workspaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import training
from app.core.database import get_db
from app.core.knowledge_core_contracts import KnowledgeChannel
from app.core.onboarding_workspaces import OnboardingWorkspace, build_onboarding_workspace
from app.core.tenant import get_tenant_id


@dataclass
class _FakeResult:
    row: dict[str, Any] | None = None

    def mappings(self):
        return self

    def first(self):
        return self.row


class _FakeDb:
    def __init__(self, rows: dict[str, dict[str, Any]] | None = None):
        self.rows = rows or {}

    def execute(self, statement, params):
        sql = str(statement)
        if "FROM domain_hr.onboarding_runs" in sql:
            return _FakeResult(self.rows.get(f"run:{params['id']}"))
        if "FROM domain_hr.onboarding_checklists" in sql:
            return _FakeResult(self.rows.get(f"checklist:{params['id']}"))
        return _FakeResult(None)


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(training.router)
    app.dependency_overrides[get_db] = lambda: _FakeDb()
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    return TestClient(app)


class TestOnboardingWorkspaceContracts:

    def test_workspace_uses_checklist_tasks_before_generic_standards(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "app.core.onboarding_workspaces.build_runtime_onboarding_bundle",
            lambda **kwargs: {
                "rolle": "support",
                "tenant_id": "tenant-a",
                "anzahl": 2,
                "wissensobjekte": [{"knowledge_id": "KNW-SUP-001"}, {"knowledge_id": "KNW-COM-001"}],
            },
        )
        monkeypatch.setattr(
            "app.core.onboarding_workspaces.build_runtime_context_pack",
            lambda **kwargs: type(
                "Pack",
                (),
                {
                    "as_dict": lambda self: {
                        "knowledge_ids": ["KNW-SUP-001", "KNW-COM-001"],
                        "standards": ["Kommunikationsstandard aus KNW-COM-001"],
                    }
                },
            )(),
        )

        workspace = build_onboarding_workspace(
            db=_FakeDb(),
            rolle="support",
            kanal=KnowledgeChannel.TEAMS,
            tenant_id="tenant-a",
            checklist={
                "tasks": [
                    {"code": "task-1", "title": "Support-SOP lesen"},
                    {"code": "task-2", "title": "OIDC-Login-Fluss pruefen"},
                ]
            },
            onboarding_run={"state": {"completed_task_codes": ["task-1"]}},
        )

        assert workspace.kanal == "TEAMS"
        assert workspace.empfohlene_naechste_schritte[0] == "OIDC-Login-Fluss pruefen"
        assert "KNW-SUP-001" in workspace.context_pack["knowledge_ids"]


class TestOnboardingWorkspaceApi:

    def test_workspace_endpoint_returns_knowledge_backed_workspace(
        self,
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(
            "app.api.v1.endpoints.training.build_onboarding_workspace",
            lambda **kwargs: OnboardingWorkspace(
                rolle="support",
                kanal="TEAMS",
                tenant_id="tenant-a",
                employee_ref="emp-1",
                capability_key="onboarding_assistant",
                checklist=None,
                onboarding_run=None,
                knowledge_bundle={"anzahl": 2, "wissensobjekte": [{"knowledge_id": "KNW-SUP-001"}]},
                context_pack={"knowledge_ids": ["KNW-SUP-001"], "standards": ["Kommunikationsstandard aus KNW-COM-001"]},
                empfohlene_naechste_schritte=["Support-SOP lesen"],
                channel_message="Onboarding-Workspace fuer Rolle 'support' erstellt.",
            ),
        )

        response = client.post(
            "/training/onboarding/workspaces",
            json={"rolle": "support", "employee_ref": "emp-1", "kanal": "TEAMS"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["rolle"] == "support"
        assert body["kanal"] == "TEAMS"
        assert body["knowledge_bundle"]["anzahl"] == 2
        assert body["context_pack"]["knowledge_ids"] == ["KNW-SUP-001"]

    def test_workspace_endpoint_loads_existing_run_and_checklist(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ):
        app = FastAPI()
        fake_db = _FakeDb(
            rows={
                "run:run-1": {
                    "id": "run-1",
                    "tenant_id": "tenant-a",
                    "checklist_id": "check-1",
                    "employee_ref": "emp-1",
                    "status": "in_progress",
                    "state": {"completed_task_codes": ["task-1"]},
                },
                "checklist:check-1": {
                    "id": "check-1",
                    "tenant_id": "tenant-a",
                    "checklist_code": "ONB-SUP-001",
                    "title": "Support-Onboarding",
                    "tasks": [{"code": "task-2", "title": "OIDC-Login-Fluss pruefen"}],
                },
            }
        )
        app.include_router(training.router)
        app.dependency_overrides[get_db] = lambda: fake_db
        app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
        captured: dict[str, Any] = {}

        def _fake_builder(**kwargs):
            captured.update(kwargs)
            return OnboardingWorkspace(
                rolle=kwargs["rolle"],
                kanal="SLACK",
                tenant_id=kwargs["tenant_id"],
                employee_ref=kwargs["employee_ref"],
                capability_key=kwargs["capability_key"],
                checklist=kwargs["checklist"],
                onboarding_run=kwargs["onboarding_run"],
                knowledge_bundle={"anzahl": 1, "wissensobjekte": [{"knowledge_id": "KNW-SUP-001"}]},
                context_pack={"knowledge_ids": ["KNW-SUP-001"], "standards": []},
                empfohlene_naechste_schritte=["OIDC-Login-Fluss pruefen"],
                channel_message="Slack workspace ready.",
            )

        monkeypatch.setattr("app.api.v1.endpoints.training.build_onboarding_workspace", _fake_builder)
        client = TestClient(app)

        response = client.post(
            "/training/onboarding/workspaces",
            json={"rolle": "support", "run_id": "run-1", "employee_ref": "emp-1", "kanal": "SLACK"},
        )

        assert response.status_code == 200
        assert captured["checklist"]["id"] == "check-1"
        assert captured["onboarding_run"]["id"] == "run-1"
        assert response.json()["kanal"] == "SLACK"

    def test_workspace_endpoint_requires_role(self, client: TestClient):
        response = client.post("/training/onboarding/workspaces", json={"rolle": "   "})
        assert response.status_code == 400
