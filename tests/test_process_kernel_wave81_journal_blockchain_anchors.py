from __future__ import annotations

from types import SimpleNamespace
import importlib

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.tenant import get_tenant_id

journal_entries_module = importlib.import_module("app.api.v1.endpoints.journal_entries")
router = journal_entries_module.router


class _DummyRepo:
    async def post_entry(self, entry_id: str, tenant_id: str):
        return True

    async def get_by_id(self, entry_id: str, tenant_id: str):
        return SimpleNamespace(
            id=entry_id,
            tenant_id=tenant_id,
            entry_number="JE-1",
            entry_date="2026-03-19",
            posting_date="2026-03-19",
            description="Testbuchung",
            reference="REF-1",
            source="manual",
            status="posted",
            total_debit=100,
            total_credit=100,
            posted_by="dev-user",
            posted_at="2026-03-19T10:00:00Z",
            created_at="2026-03-19T10:00:00Z",
            updated_at="2026-03-19T10:00:00Z",
            lines=[],
        )

    async def reverse_entry(self, entry_id: str, reason: str, tenant_id: str):
        return SimpleNamespace(id="REV-1")


class _DummyAnchor:
    def __init__(self, subject_ref: str):
        self.subject_ref = subject_ref

    def as_dict(self):
        return {
            "anchor_id": "anchor-je-1",
            "subject_ref": self.subject_ref,
            "network_profile": "ORACLE_FABRIC_PERMISSIONED",
        }


def _client(monkeypatch) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[journal_entries_module.get_db] = lambda: object()
    monkeypatch.setattr(journal_entries_module.container, "resolve", lambda cls: _DummyRepo())
    monkeypatch.setattr(journal_entries_module, "log_fibu_audit", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "app.core.blockchain_anchor_runtime.anchor_journal_entry_event",
        lambda db, tenant_id, entry_id, action, payload: _DummyAnchor(entry_id),
    )
    return TestClient(app)


def test_post_journal_entry_returns_blockchain_anchor(monkeypatch):
    client = _client(monkeypatch)
    response = client.post("/JE-1/post")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "JE-1"
    assert body["blockchain_anchor"]["subject_ref"] == "JE-1"


def test_reverse_journal_entry_returns_blockchain_anchor(monkeypatch):
    client = _client(monkeypatch)
    response = client.post("/JE-1/reverse", params={"reason": "Korrektur"})
    assert response.status_code == 200
    body = response.json()
    assert body["reversal_entry_id"] == "REV-1"
    assert body["blockchain_anchor"]["subject_ref"] == "JE-1"
