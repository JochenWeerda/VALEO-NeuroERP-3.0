"""Type-preserving immutable history comparison and tenant boundaries."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.endpoints import studio_drafts
from app.core.tenant import get_tenant_id
from app.auth.deps import get_current_user
from app.services import studio_draft_store as store
from app.services.studio_history_view import definition_diff
from app.core.screen_definitions_studio_history import STUDIO_HISTORY_BUILDERS


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


@pytest.fixture
def history_client():
    store.reset_studio_drafts()
    app = FastAPI()
    app.include_router(studio_drafts.router)
    app.dependency_overrides[get_tenant_id] = lambda: "own"
    app.dependency_overrides[get_current_user] = lambda: {"sub": "synthetic-viewer"}
    yield TestClient(app)
    store.use_sql_studio_drafts()


def test_types_and_removed_values_are_not_hidden():
    rows = definition_diff({"enabled": True, "x": 1}, {"enabled": 1, "new": None})
    assert len(rows) == 3
    assert rows[0]["before"] == "true" and rows[0]["after"] == "1"
    assert rows[-1]["after"] == "Nicht vorhanden"


def test_same_timestamp_has_same_revision_across_database_timezones():
    record={"id":"own","tenant_id":"own","definition":{},"status":"draft","updated_by":"editor"}
    utc=store._with_revision({**record,"updated_at":"2026-10-14T21:13:50.770363+00:00"})
    local=store._with_revision({**record,"updated_at":"2026-10-14T23:13:50.770363+02:00"})
    assert utc["revision"]==local["revision"]


def test_history_view_and_diff_stay_in_tenant(history_client):
    first = store.save_draft("own", "synthetic-editor", {"id": "tenant/history", "title": "Before"})
    store.save_draft("own", "synthetic-editor", {"id": "tenant/history", "title": "After"},
                     draft_id=first["id"], expected_revision=first["revision"])
    foreign = store.save_draft("foreign", "synthetic-other", {"id": "tenant/foreign"})
    response = history_client.get(f"/studio/drafts/{first['id']}/history-view?skip=1&limit=1")
    assert response.status_code == 200
    row = response.json()["items"][0]
    assert response.json()["total"] == 2
    diff = history_client.get(f"/studio/drafts/{first['id']}/history-diff?entry_id={row['id']}")
    assert history_client.get(f"/studio/history-events/{row['id']}/diff").json() == diff.json()
    foreign_event = store.list_history("foreign", foreign["id"])[0]
    assert history_client.get(f"/studio/history-events/{foreign_event['id']}/diff").status_code == 404
    assert diff.status_code == 200
    assert diff.json()["items"] == [{"id": "/title", "path": "/title", "before": '"Before"', "after": '"After"'}]
    assert history_client.get(f"/studio/drafts/{foreign['id']}/history-view").status_code == 404
    assert history_client.get(f"/studio/drafts/{foreign['id']}/history-diff?entry_id={row['id']}").status_code == 404


def test_masks_are_native_audit_definitions():
    for screen_id, build in STUDIO_HISTORY_BUILDERS.items():
        definition = build()
        assert definition["adapter"] == {"type": "native", "sourceId": screen_id, "temporary": False}
        assert definition["layout"]["tableProfile"] == "audit"
