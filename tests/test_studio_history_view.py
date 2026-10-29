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


def test_single_label_change_does_not_dump_the_entire_mask():
    import copy
    before = {'tabs': [{'key': 'kopf', 'fields': [
        {'key': 'number', 'label': 'Kunden-Nr.'},
        *[{'key': f'field-{index}', 'label': f'Feld {index}'} for index in range(200)],
    ]}]}
    after = copy.deepcopy(before)
    after['tabs'][0]['fields'][0]['label'] = 'Betriebsnummer'
    original = copy.deepcopy((before, after))
    assert definition_diff(before, after) == [{
        'id': '/tabs/0/fields/0/label', 'path': '/tabs/0/fields/0/label',
        'before': '"Kunden-Nr."', 'after': '"Betriebsnummer"',
    }]
    assert (before, after) == original


@pytest.mark.parametrize('before,after,path,old,new', [
    ([True], [1], '/0', 'true', '1'),
    ([1], ['1'], '/0', '1', '"1"'),
    ([1], [1, None], '/1', 'Nicht vorhanden', 'null'),
    ([1, None], [1], '/1', 'null', 'Nicht vorhanden'),
    ({}, {'empty': []}, '/empty', 'Nicht vorhanden', '[]'),
    ({'empty': {}}, {}, '/empty', '{}', 'Nicht vorhanden'),
    ([{'a/b~c': 1}], [{'a/b~c': 2}], '/0/a~1b~0c', '1', '2'),
    ({}, {'tabs': [{'label': 'Neu'}]}, '/tabs/0/label', 'Nicht vorhanden', '"Neu"'),
    ({'tabs': [{'label': 'Alt'}]}, {}, '/tabs/0/label', '"Alt"', 'Nicht vorhanden'),
])
def test_array_and_missing_values_keep_types_and_unambiguous_paths(before, after, path, old, new):
    assert definition_diff(before, after) == [{'id': path, 'path': path, 'before': old, 'after': new}]


def test_array_reordering_is_a_visible_ordered_change():
    before = [{'key': 'a'}, {'key': 'b'}]
    after = list(reversed(before))
    rows = definition_diff(before, after)
    assert [row['path'] for row in rows] == ['/0/key', '/1/key']
    assert rows[0]['before'] == '"a"' and rows[0]['after'] == '"b"'
    assert definition_diff(before, before) == []


def test_http_nested_comparison_is_small_paginated_and_does_not_rewrite_history(history_client):
    import copy
    first = store.save_draft('own', 'synthetic-editor', {'id': 'tenant/nested', 'tabs': [{'fields': [
        {'key': 'a', 'label': 'Vorher'}, {'key': 'b', 'label': 'Unveraendert'},
    ]}]})
    changed = copy.deepcopy(first['definition'])
    changed['tabs'][0]['fields'][0]['label'] = 'Nachher'
    store.save_draft('own', 'synthetic-editor', changed, draft_id=first['id'], expected_revision=first['revision'])
    events = copy.deepcopy(store.list_history('own', first['id']))
    entry = events[-1]
    response = history_client.get(f"/studio/history-events/{entry['id']}/diff?skip=0&limit=1")
    assert response.status_code == 200, response.text
    assert response.json()['total'] == 1
    assert response.json()['items'][0]['path'] == '/tabs/0/fields/0/label'
    assert response.json()['items'][0]['before'] == '"Vorher"'
    assert response.json()['items'][0]['after'] == '"Nachher"'
    assert history_client.get(f"/studio/history-events/{entry['id']}/diff?skip=1&limit=1").json()['items'] == []
    assert store.list_history('own', first['id']) == events
