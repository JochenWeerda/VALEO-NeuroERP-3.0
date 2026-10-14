"""Postgres persistence for Masken-Studio drafts (require_db)."""

from __future__ import annotations
from studio_review_helper import publish_reviewed

import pytest
from uuid import uuid4
from app.auth.deps import get_current_user
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.screen_definitions import get_screen_definition
from app.infrastructure.models.studio_models import ScreenDefinitionDraft
from app.main import app
from app.services.studio_draft_store import (
    invalidate_studio_table_cache,
    reset_studio_drafts,
    use_sql_studio_drafts,
)
from app.services.studio_propose import propose_studio_draft

pytestmark = pytest.mark.integration

_TENANT_A = "studio-a-" + uuid4().hex
_TENANT_B = "studio-b-" + uuid4().hex
_HEADERS_A = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": _TENANT_A,
}
_HEADERS_B = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": _TENANT_B,
}


_USER: dict = {}


@pytest.fixture
def studio_db(require_db, monkeypatch):
    assert engine.url.database == "valeo_probe" or "test" in (engine.url.database or "").lower()
    _USER.clear()
    _USER.update(sub="anna", roles=["admin"], raw={"identity_type": "human"})
    previous_user = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: _USER
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_shared"))
    ScreenDefinitionDraft.__table__.create(bind=engine, checkfirst=True)
    invalidate_studio_table_cache()
    use_sql_studio_drafts()
    with engine.begin() as conn:
        for tenant in (_TENANT_A, _TENANT_B):
            conn.execute(text("INSERT INTO domain_shared.tenants(id,name) VALUES (:id,'Studio Test') ON CONFLICT(id) DO NOTHING"), {"id": tenant})
    connection = engine.connect()
    transaction = connection.begin()
    factory = lambda: Session(bind=connection, join_transaction_mode="create_savepoint")
    from app.services import studio_draft_store
    monkeypatch.setattr(studio_draft_store, "_sql_session", factory)
    monkeypatch.setattr(__import__(__name__), "SessionLocal", factory)
    yield
    transaction.rollback()
    connection.close()
    if previous_user is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = previous_user
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM domain_shared.screen_definition_drafts WHERE tenant_id IN (:a,:b)"), {"a": _TENANT_A, "b": _TENANT_B})
        conn.execute(text("DELETE FROM domain_shared.tenants WHERE id IN (:a,:b)"), {"a": _TENANT_A, "b": _TENANT_B})
    reset_studio_drafts()


def _client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_sql_save_survives_process_memory_reset(studio_db) -> None:
    client = _client()
    draft = propose_studio_draft("Lieferanten bewerten")
    created = client.post(
        "/api/v1/studio/drafts",
        headers={**_HEADERS_A, "X-Actor-ID": "anna"},
        json={"definition": draft, 'idempotency_key': str(uuid4())},
    )
    assert created.status_code == 200, created.text
    draft_id = created.json()["id"]
    session = SessionLocal()
    try:
        count = session.execute(
            text("SELECT count(*) FROM domain_shared.screen_definition_drafts WHERE id = :id"),
            {"id": draft_id},
        ).scalar()
    finally:
        session.close()
    assert count == 1
    listed = client.get("/api/v1/studio/drafts", headers=_HEADERS_A)
    assert any(item["id"] == draft_id for item in listed.json()["drafts"])


def test_sql_tenant_isolation_and_four_eyes(studio_db) -> None:
    client = _client()
    draft = propose_studio_draft("Artikel")
    created = client.post(
        "/api/v1/studio/drafts",
        headers={**_HEADERS_A, "X-Actor-ID": "anna"},
        json={"definition": draft, 'idempotency_key': str(uuid4())},
    )
    assert created.status_code == 200, created.text
    draft_id = created.json()["id"]
    other = client.get("/api/v1/studio/drafts", headers=_HEADERS_B)
    assert other.json()["drafts"] == []
    assert client.get(f"/api/v1/studio/drafts/{draft_id}", headers=_HEADERS_B).status_code == 404
    forbidden = publish_reviewed(
        client, f"/api/v1/studio/drafts/{draft_id}/publish",
        headers={**_HEADERS_A, "X-Actor-ID": "anna"},
    )
    assert forbidden.status_code == 403
    _USER["sub"] = "berta"
    published = publish_reviewed(
        client, f"/api/v1/studio/drafts/{draft_id}/publish",
        headers={**_HEADERS_A, "X-Actor-ID": "berta"},
    )
    assert published.status_code == 200, published.text
    screen_id = published.json()["screen_id"]
    visible = get_screen_definition(screen_id, tenant_id=_TENANT_A)
    hidden = get_screen_definition(screen_id, tenant_id=_TENANT_B)
    assert visible is not None
    assert visible["id"] == screen_id
    assert hidden is None
