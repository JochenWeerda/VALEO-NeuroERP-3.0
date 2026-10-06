"""Real GET dispatch must enforce feed roles and query the tenant's existing article projection."""
import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from starlette.routing import Match

from app.api.v1.endpoints import futter_stamm, futter_read
from app.infrastructure.models import Article
from types import SimpleNamespace
from app.core.config import settings
from main import app


CASES = [
    ("einzelfuttermittel", futter_read.futter_einzel, Article, 500),
    ("mischfuttermittel", futter_read.futter_misch, Article, 200),
]


def first_handler(kind):
    scope = {"type": "http", "method": "GET", "root_path": "",
             "path": settings.API_V1_STR + "/futter/" + kind}
    return next(route.endpoint for route in app.routes
                if route.matches(scope)[0] == Match.FULL)


class QueryRecorder:
    def __init__(self, expected_model):
        self.model = expected_model
        self.filters = []
        self.queries = 0

    def query(self, model):
        assert model is self.model
        self.queries += 1
        return self

    def filter(self, *predicates):
        self.filters.extend(predicates)
        return self

    def order_by(self, *columns):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def all(self):
        return [SimpleNamespace(id="own-feed", tenant_id="tenant-a", name="Futter",
            article_number="F-1", category="Futter", custom_properties={}, sales_price=12, unit="t")]

    def rollback(self):
        raise AssertionError("Unexpected fallback from the canonical query")


@pytest.mark.parametrize("kind,endpoint,model,bound", CASES)
def test_dispatch_keeps_tenant_active_filters_and_response_contract(kind, endpoint, model, bound):
    handler = first_handler(kind)
    assert handler is endpoint
    db = QueryRecorder(model)
    result = asyncio.run(handler(tenant_id="tenant-a", db=db,
        user={"sub": "feed-reader", "roles": ["FUTTERMITTEL_LESEN"]}))
    assert result[0]["id"] == "own-feed"
    assert result[0]["artikelnummer"] == "F-1"
    assert result[0]["preis"] == 12
    assert db.limit_value == bound
    statement = select(model).where(*db.filters).compile()
    assert "tenant_id" in str(statement)
    assert "is_active = true" in str(statement)
    assert "tenant-a" in statement.params.values()
    assert db.queries == 1


@pytest.mark.parametrize("kind,endpoint,model,bound", CASES)
def test_unrelated_role_is_rejected_before_database_access(kind, endpoint, model, bound):
    handler = first_handler(kind)
    assert handler is endpoint
    db = QueryRecorder(model)
    with pytest.raises(HTTPException) as denied:
        asyncio.run(handler(tenant_id="tenant-a",
            db=db, user={"sub": "crm-reader", "roles": ["CRM_LESEN"]}))
    assert denied.value.status_code == 403
    assert db.queries == 0


def test_compound_feed_fachhandler_also_rejects_unrelated_roles():
    with pytest.raises(HTTPException) as denied:
        asyncio.run(futter_stamm.list_mischfuttermittel(tierart=None, aktiv=True,
            tenant_id="tenant-a", db=object(), user={"roles": ["CRM_LESEN"]}))
    assert denied.value.status_code == 403
