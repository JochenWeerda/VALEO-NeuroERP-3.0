from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import collab_notes
from app.core.database import get_db
from app.core.security import require_bearer_token


HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-collab-a"}
NOW = datetime(2026, 7, 7, 8, tzinfo=UTC)


class _Result:
    def __init__(self, rows: list[dict[str, Any]] | None = None):
        self.rows = rows or []

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self.rows

    def first(self) -> dict[str, Any] | None:
        return self.rows[0] if self.rows else None


class _CollabDb:
    def __init__(self) -> None:
        self.notes: dict[str, dict[str, Any]] = {}
        self.messages: list[dict[str, Any]] = []
        self.users: dict[str, set[str]] = {
            "tenant-collab-a": {"dev-user", "u-mentioned"},
            "tenant-collab-b": {"dev-user", "u-mentioned"},
        }
        self.commits = 0
        self.rollbacks = 0

    def seed_note(
        self,
        *,
        note_id: str,
        tenant_id: str = "tenant-collab-a",
        entity_type: str = "crm/customer-360",
        entity_id: str = "cust-1",
        created_by: str = "dev-user",
        body: str = "Bestehende Notiz",
    ) -> dict[str, Any]:
        row = {
            "id": note_id,
            "tenant_id": tenant_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "body": body,
            "mentions": [],
            "created_by": created_by,
            "created_at": NOW,
            "updated_at": NOW,
            "deleted_at": None,
        }
        self.notes[note_id] = row
        return row

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _Result:
        sql = str(statement)
        params = params or {}
        if "FROM domain_shared.users" in sql:
            existing = self.users.get(params["tenant_id"], set())
            return _Result([{"id": user_id} for user_id in params["user_ids"] if user_id in existing])

        if "INSERT INTO domain_shared.entity_notes" in sql:
            mentions = params.get("mentions") or "[]"
            row = {
                "id": params["id"],
                "tenant_id": params["tenant_id"],
                "entity_type": params["entity_type"],
                "entity_id": params["entity_id"],
                "body": params["body"],
                "mentions": json.loads(mentions) if isinstance(mentions, str) else mentions,
                "created_by": params["created_by"],
                "created_at": NOW,
                "updated_at": NOW,
                "deleted_at": None,
            }
            self.notes[row["id"]] = row
            return _Result([row])

        if "INSERT INTO domain_shared.internal_messages" in sql:
            self.messages.append(dict(params))
            return _Result([])

        if "FROM domain_shared.entity_notes" in sql and "AND id = :id" in sql:
            row = self.notes.get(params["id"])
            if row and row["tenant_id"] == params["tenant_id"] and row["deleted_at"] is None:
                return _Result([row])
            return _Result([])

        if "FROM domain_shared.entity_notes" in sql:
            rows = [
                row
                for row in self.notes.values()
                if row["tenant_id"] == params["tenant_id"]
                and row["entity_type"] == params["entity_type"]
                and row["entity_id"] == params["entity_id"]
                and row["deleted_at"] is None
            ]
            return _Result(rows)

        if "UPDATE domain_shared.entity_notes" in sql and "deleted_at = now()" in sql:
            row = self.notes.get(params["id"])
            if row and row["tenant_id"] == params["tenant_id"] and row["deleted_at"] is None:
                row["deleted_at"] = NOW
                row["updated_at"] = NOW
            return _Result([])

        if "UPDATE domain_shared.entity_notes" in sql:
            row = self.notes.get(params["id"])
            if not row or row["tenant_id"] != params["tenant_id"] or row["deleted_at"] is not None:
                return _Result([])
            if params["body_update"]:
                row["body"] = params["body"]
            if params["mentions_update"]:
                mentions = params.get("mentions") or "[]"
                row["mentions"] = json.loads(mentions) if isinstance(mentions, str) else mentions
            row["updated_at"] = NOW
            return _Result([row])

        return _Result([])

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _client_with_db(db: _CollabDb, monkeypatch):
    events: list[dict[str, Any]] = []
    app = FastAPI()
    app.include_router(collab_notes.router, prefix="/api/v1", dependencies=[Depends(require_bearer_token)])

    async def fake_enqueue_event(*args: Any, **kwargs: Any) -> None:
        events.append(kwargs)

    def override_db():
        yield db

    monkeypatch.setattr(collab_notes, "enqueue_event", fake_enqueue_event)
    app.dependency_overrides[get_db] = override_db
    return app, TestClient(app, raise_server_exceptions=False), events


def test_create_note_writes_message_and_outbox(monkeypatch) -> None:
    db = _CollabDb()
    app, client, events = _client_with_db(db, monkeypatch)
    try:
        response = client.post(
            "/api/v1/collab/notes",
            headers=HEADERS,
            json={
                "entity_type": "crm/customer-360",
                "entity_id": "cust-1",
                "body": "Bitte pruefen @u-mentioned",
                "mentions": [{"user_id": "u-mentioned", "display": "Mentioned User"}],
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["tenant_id"] == "tenant-collab-a"
    assert body["created_by"] == "dev-user"
    assert body["mentions"][0]["user_id"] == "u-mentioned"
    assert len(db.messages) == 1
    assert db.messages[0]["recipient_id"] == "u-mentioned"
    assert events[0]["event_type"] == "collab.note.created"
    assert events[0]["tenant_id"] == "tenant-collab-a"


def test_list_notes_is_tenant_isolated_and_soft_delete_hides_rows(monkeypatch) -> None:
    db = _CollabDb()
    note = db.seed_note(note_id="note-a")
    db.seed_note(note_id="note-b", tenant_id="tenant-collab-b")
    app, client, _events = _client_with_db(db, monkeypatch)
    try:
        response_a = client.get(
            "/api/v1/collab/notes",
            headers=HEADERS,
            params={"entity_type": "crm/customer-360", "entity_id": "cust-1"},
        )
        delete_response = client.delete(f"/api/v1/collab/notes/{note['id']}", headers=HEADERS)
        response_after_delete = client.get(
            "/api/v1/collab/notes",
            headers=HEADERS,
            params={"entity_type": "crm/customer-360", "entity_id": "cust-1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response_a.status_code == 200, response_a.text
    assert [row["id"] for row in response_a.json()] == ["note-a"]
    assert delete_response.status_code == 204, delete_response.text
    assert response_after_delete.status_code == 200
    assert response_after_delete.json() == []


def test_cross_tenant_patch_returns_404_and_non_creator_returns_403(monkeypatch) -> None:
    db = _CollabDb()
    db.seed_note(note_id="note-a")
    db.seed_note(note_id="note-other", created_by="other-user")
    app, client, _events = _client_with_db(db, monkeypatch)
    try:
        cross_tenant = client.patch(
            "/api/v1/collab/notes/note-a",
            headers={**HEADERS, "X-Tenant-ID": "tenant-collab-b"},
            json={"body": "Cross tenant"},
        )
        forbidden = client.patch(
            "/api/v1/collab/notes/note-other",
            headers=HEADERS,
            json={"body": "Nicht erlaubt"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert cross_tenant.status_code == 404, cross_tenant.text
    assert forbidden.status_code == 403, forbidden.text


def test_patch_validates_mentions_and_updates_creator_note(monkeypatch) -> None:
    db = _CollabDb()
    db.seed_note(note_id="note-a")
    app, client, _events = _client_with_db(db, monkeypatch)
    try:
        invalid = client.patch(
            "/api/v1/collab/notes/note-a",
            headers=HEADERS,
            json={"mentions": [{"user_id": "missing-user"}]},
        )
        valid = client.patch(
            "/api/v1/collab/notes/note-a",
            headers=HEADERS,
            json={"body": "Aktualisiert", "mentions": [{"user_id": "u-mentioned"}]},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert invalid.status_code == 422, invalid.text
    assert valid.status_code == 200, valid.text
    assert valid.json()["body"] == "Aktualisiert"
    assert valid.json()["mentions"][0]["user_id"] == "u-mentioned"
