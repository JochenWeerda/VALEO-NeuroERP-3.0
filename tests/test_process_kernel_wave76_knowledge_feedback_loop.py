"""
Wave 76 - Knowledge feedback loop and standardization back into the knowledge core.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api


class _DummyAnchor:
    def __init__(self, subject_ref: str):
        self.subject_ref = subject_ref

    def as_dict(self):
        return {
            "anchor_id": "anchor-1",
            "subject_ref": self.subject_ref,
            "network_profile": "ORACLE_FABRIC_PERMISSIONED",
        }


class _DummyRepo:
    def __init__(self, db):
        self.db = db

    def list_proposals(self):
        return [type("Proposal", (), {"proposal_id": "p-1"})()]

    def proposal_as_dict(self, proposal):
        if getattr(proposal, "proposal_id", None) == "p-1":
            return {
                "proposal_id": "p-1",
                "tenant_id": "t1",
                "status": "EINGEREICHT",
                "titel": "Neue Support-SOP",
                "typ": "SOP",
                "format": "MARKDOWN",
                "inhalt": "Nutze den neuen Login-Fallback.",
            }
        return proposal

    def get_proposal(self, proposal_id: str):
        if proposal_id != "p-1":
            return None
        return type("Proposal", (), {"proposal_id": "p-1"})()

    def create_proposal(self, **kwargs):
        return {
            "proposal_id": "p-created",
            "tenant_id": kwargs["tenant_id"],
            "status": "EINGEREICHT",
            "titel": kwargs["titel"],
            "typ": kwargs["typ"],
            "format": kwargs["format"],
            "inhalt": kwargs["inhalt"],
            "vorgeschlagen_von_ref": kwargs["vorgeschlagen_von_ref"],
            "quelle": kwargs.get("quelle"),
        }

    def review_proposal(self, proposal_id: str, **kwargs):
        if proposal_id != "p-1":
            return None, None
        proposal = {
            "proposal_id": "p-1",
            "tenant_id": "t1",
            "status": "UEBERNOMMEN" if kwargs["entscheidung"] == "GENEHMIGT" else "ABGELEHNT",
            "applied_knowledge_id": "KNW-SUP-001",
            "applied_version": 2 if kwargs["entscheidung"] == "GENEHMIGT" else None,
        }
        if kwargs["entscheidung"] == "ABGELEHNT":
            return proposal, None
        applied_record = type(
            "KnowledgeRecord",
            (),
            {
                "knowledge_id": "KNW-SUP-001",
                "titel": "Supportwissen OIDC Anmeldung",
                "typ": "SUPPORTWISSEN",
                "status": "FREIGEGEBEN",
                "tenant_id": "system",
                "tags": ["support", "oidc"],
                "zielrollen": ["support"],
                "agentenfreigabe": True,
                "beschreibung": "",
                "versionen": [
                    type(
                        "Version",
                        (),
                        {
                            "version": 2,
                            "format": "MARKDOWN",
                            "inhalt": "Neuer Fallback aktiv.",
                            "strukturierte_daten": {},
                            "erstellt_am": None,
                            "quelle": "improvement-workflow",
                        },
                    )()
                ],
            },
        )()
        return proposal, applied_record

    def to_domain_object(self, record):
        return type(
            "DomainObj",
            (),
            {
                "as_dict": lambda self: {
                    "knowledge_id": "KNW-SUP-001",
                    "version": 2,
                    "format": "MARKDOWN",
                    "status": "FREIGEGEBEN",
                }
            },
        )()


class _DummyNeuroAssistService:
    async def get_run_status(self, run_id: str):
        if run_id != "run-1":
            raise KeyError(f"Run {run_id!r} nicht gefunden")
        return {
            "run_id": "run-1",
            "correlation_id": "corr-1",
            "capability_key": "system_optimizer",
            "status": "completed",
            "started_at": "2026-03-19T10:00:00Z",
            "runtime": {
                "workflow_schema_key": "improvement_runbook",
                "result_refs": ["system_optimizer", "improvement_runbook", "audit-1"],
            },
            "result": {
                "summary": "Der bestehende Freigabeprozess wurde als Standardisierungspotenzial markiert.",
            },
        }


def _create_client(monkeypatch) -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    app.dependency_overrides[process_kernel_api.get_db] = lambda: object()
    monkeypatch.setattr("app.repositories.knowledge_repository.KnowledgeRepository", _DummyRepo)
    monkeypatch.setattr("app.agents.get_neuroassist_service", lambda: _DummyNeuroAssistService())
    monkeypatch.setattr(
        "app.core.blockchain_anchor_runtime.anchor_knowledge_object",
        lambda db, knowledge_record, version, proposal_id=None: _DummyAnchor(
            f"{knowledge_record.knowledge_id}:v{version}"
        ),
    )
    monkeypatch.setattr(
        "app.core.blockchain_anchor_runtime.anchor_governance_proposal",
        lambda db, proposal: _DummyAnchor(
            f"proposal:{proposal['proposal_id'] if isinstance(proposal, dict) else proposal.proposal_id}"
        ),
    )
    return TestClient(app)


def test_create_improvement_proposal(monkeypatch):
    client = _create_client(monkeypatch)
    response = client.post(
        "/process/knowledge/store/proposals",
        json={
            "tenant_id": "t1",
            "titel": "Neue Support-SOP",
            "typ": "SOP",
            "format": "MARKDOWN",
            "inhalt": "Nutze den neuen Login-Fallback.",
            "vorgeschlagen_von_ref": "agent-1",
            "vorgeschlagen_von_typ": "agent",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["proposal_id"] == "p-created"
    assert body["status"] == "EINGEREICHT"


def test_list_improvement_proposals(monkeypatch):
    client = _create_client(monkeypatch)
    response = client.get("/process/knowledge/store/proposals")
    assert response.status_code == 200
    body = response.json()
    assert body[0]["proposal_id"] == "p-1"


def test_review_improvement_proposal_and_apply(monkeypatch):
    client = _create_client(monkeypatch)
    response = client.post(
        "/process/knowledge/store/proposals/p-1/review",
        json={
            "entscheidung": "GENEHMIGT",
            "reviewer_ref": "lead-1",
            "reviewer_rolle": "knowledge_owner",
            "review_notiz": "In Standard uebernehmen",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["proposal"]["status"] == "UEBERNOMMEN"
    assert body["applied_knowledge_object"]["knowledge_id"] == "KNW-SUP-001"
    assert body["blockchain_anchor"]["subject_ref"] == "KNW-SUP-001:v2"


def test_review_requires_decision(monkeypatch):
    client = _create_client(monkeypatch)
    response = client.post(
        "/process/knowledge/store/proposals/p-1/review",
        json={"reviewer_ref": "lead-1"},
    )
    assert response.status_code == 400


def test_create_improvement_proposal_from_neuroassist_run(monkeypatch):
    client = _create_client(monkeypatch)
    response = client.post(
        "/process/knowledge/store/proposals/from-neuroassist-run",
        json={
            "run_id": "run-1",
            "tenant_id": "t1",
            "titel": "System-Optimizer als Prozessstandard uebernehmen",
            "vorgeschlagen_von_ref": "system-optimizer",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["proposal_id"] == "p-created"
    assert body["status"] == "EINGEREICHT"
    assert body["quelle"] == "neuroassist-run-feedback"
    assert body["blockchain_anchor"]["subject_ref"] == "proposal:p-created"
