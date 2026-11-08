"""Real GET dispatch serves the feed lists from their master data, with feed roles and tenant filter.

Until 20.10.2026 a compat projection of *all* active articles answered these paths first: the list showed
fertiliser and seed as feed, and its ids opened no detail view (the detail reads the feed tables). The canonical
handlers are ``futter_stamm`` (feed catalog ``futtermittel_einzelfutter`` and ``futtermittel_mischfutter``).
"""
import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from starlette.routing import Match

from app.api.v1.endpoints import futter_stamm
from app.core.config import settings
from app.infrastructure.models.futtermittel_models import Einzelfuttermittel, Mischfuttermittel
from main import app


CASES = [
    ("einzelfuttermittel", futter_stamm.list_einzelfuttermittel, Einzelfuttermittel, "art"),
    ("mischfuttermittel", futter_stamm.list_mischfuttermittel, Mischfuttermittel, "tierart"),
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

    def all(self):
        return ["own-feed"]


@pytest.mark.parametrize("kind,endpoint,model,filter_name", CASES)
def test_dispatch_reads_feed_master_data_for_the_own_tenant(kind, endpoint, model, filter_name):
    handler = first_handler(kind)
    assert handler is endpoint
    db = QueryRecorder(model)
    result = asyncio.run(handler(**{filter_name: None}, aktiv=True, tenant_id="tenant-a", db=db,
                                 user={"sub": "feed-reader", "roles": ["FUTTERMITTEL_LESEN"]}))
    assert result == ["own-feed"]
    statement = select(model).where(*db.filters).compile()
    assert "tenant_id" in str(statement)
    assert "aktiv IS true" in str(statement)
    assert "tenant-a" in statement.params.values()
    assert db.queries == 1


@pytest.mark.parametrize("kind,endpoint,model,filter_name", CASES)
def test_unrelated_role_is_rejected_before_database_access(kind, endpoint, model, filter_name):
    handler = first_handler(kind)
    assert handler is endpoint
    db = QueryRecorder(model)
    with pytest.raises(HTTPException) as denied:
        asyncio.run(handler(**{filter_name: None}, aktiv=True, tenant_id="tenant-a",
                            db=db, user={"sub": "crm-reader", "roles": ["CRM_LESEN"]}))
    assert denied.value.status_code == 403
    assert db.queries == 0
