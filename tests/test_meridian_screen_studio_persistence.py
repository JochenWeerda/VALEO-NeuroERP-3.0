"""Postgres persistence for Masken-Studio drafts (require_db)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.core.screen_definitions import get_screen_definition
from app.infrastructure.models.studio_models import ScreenDefinitionDraft
from app.main import app
from app.services.studio_draft_store import (
    clear_sql_studio_drafts,
    invalidate_studio_table_cache,
    reset_studio_drafts,
    use_sql_studio_drafts,
)
from app.services.studio_propose import propose_studio_draft

pytestmark = pytest.mark.integration

_TENANT_A = "00000000-0000-0000-0000-000000000001"
_TENANT_B = "00000000-0000-0000-0000-000000000002"
_HEADERS_A = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": _TENANT_A,
}
_HEADERS_B = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": _TENANT_B,
}


@pytest.fixture
def studio_db(require_db):
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_shared"))
    ScreenDefinitionDraft.__table__.create(bind=engine, checkfirst=True)
    invalidate_studio_table_cache()
    use_sql_studio_drafts()
    clear_sql_studio_drafts()
    yield
    clear_sql_studio_drafts()
    reset_studio_drafts()


def _client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_sql_save_survives_process_memory_reset(studio_db) -> None:
    client = _client()
    draft = propose_studio_draft("Lieferanten bewerten")
    created = client.post(
        "/api/v1/studio/drafts",
        headers={**_HEADERS_A, "X-Actor-ID": "anna"},
        json={"definition": draft},
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
        json={"definition": draft},
    )
    assert created.status_code == 200, created.text
    draft_id = created.json()["id"]
    other = client.get("/api/v1/studio/drafts", headers=_HEADERS_B)
    assert other.json()["drafts"] == []
    forbidden = client.post(
        f"/api/v1/studio/drafts/{draft_id}/publish",
        headers={**_HEADERS_A, "X-Actor-ID": "anna"},
    )
    assert forbidden.status_code == 403
    published = client.post(
        f"/api/v1/studio/drafts/{draft_id}/publish",
        headers={**_HEADERS_A, "X-Actor-ID": "berta"},
    )
    assert published.status_code == 200, published.text
    screen_id = published.json()["screen_id"]
    visible = get_screen_definition(screen_id, tenant_id=_TENANT_A)
    hidden = get_screen_definition(screen_id, tenant_id=_TENANT_B)
    assert visible is not None
    assert visible["id"] == screen_id
    assert hidden is None
