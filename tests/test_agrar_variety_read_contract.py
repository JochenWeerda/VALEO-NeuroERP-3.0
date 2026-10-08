"""Canonical register HTTP contract without a database or application startup."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.agrar_varieties import router
from app.core.database import get_db
from app.core.tenant import get_tenant_id


def client_with(rows):
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.count.return_value = 1  # Existing tenant inventory; no read-time seeding.
    query.all.return_value = rows
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/agrar/varieties")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-contract"
    return TestClient(app), db, query


def test_register_returns_canonical_nullable_and_inactive_fields():
    row = SimpleNamespace(id="variety-contract", variety_number="245", name="Weizen",
                          crop_type="WHEAT", description=None, zuechter=None,
                          zulassungsjahr=2025, reifezahl=None, qualitaetsgruppe="A", aktiv=False)
    client, db, query = client_with([row])
    response = client.get("/api/v1/agrar/varieties/?aktiv=false")
    assert response.status_code == 200
    assert response.json() == [vars(row)]
    filters = [call.args[0] for call in query.filter.call_args_list]
    assert len(filters) == 2  # Seed presence and listing are both tenant-bound.
    assert all(condition.right.value == "tenant-contract" for condition in filters)
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_register_empty_response_has_no_fabricated_ui_properties():
    client, db, _ = client_with([])
    response = client.get("/api/v1/agrar/varieties/?aktiv=false")
    assert response.status_code == 200
    assert response.json() == []
    db.commit.assert_not_called()


def test_missing_tenant_variety_is_not_reported_as_success():
    client, db, query = client_with([])
    query.first.return_value = None
    response = client.get("/api/v1/agrar/varieties/foreign-variety")
    assert response.status_code == 404
    predicate = query.filter.call_args.args[0]
    assert [clause.right.value for clause in predicate.clauses] == ["foreign-variety", "tenant-contract"]
    db.commit.assert_not_called()
