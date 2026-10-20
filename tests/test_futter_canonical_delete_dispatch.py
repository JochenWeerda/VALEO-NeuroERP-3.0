"""Actual delete dispatch retires feed master data only, with writer role and tenant isolation.

Until 20.10.2026 compat routes answered these paths first and deactivated *any* active article of the tenant
(fertiliser, seed …) — the feed list showed every article. The canonical handlers are ``futter_stamm``: single feed
retirement through the feed catalog, compound feed ``aktiv = false`` in ``futtermittel_mischfutter``. The generic
``/futter/{kategorie}/bulk-delete`` (hard delete in tables that do not exist) is gone.
"""
import asyncio

import pytest
from fastapi import HTTPException
from starlette.routing import Match

from app.api.v1.endpoints import futter_stamm
from app.core.config import settings
from main import app


WRITER = {"sub": "writer", "roles": ["FUTTERMITTEL_BEARBEITEN"]}
CASES = [
    ("einzelfuttermittel", futter_stamm.delete_einzelfuttermittel, "futter_id"),
    ("mischfuttermittel", futter_stamm.delete_mischfuttermittel, "misch_id"),
]


def first_handler(path, method):
    scope = {"type": "http", "method": method, "root_path": "", "path": settings.API_V1_STR + path}
    return next((route.endpoint for route in app.routes if route.matches(scope)[0] == Match.FULL), None)


class NoDatabase:
    def query(self, *args):
        raise AssertionError("Denied request reached the database")


class CompoundStore:
    """Answers the tenant-scoped lookup of ``delete_mischfuttermittel`` like the database would."""

    def __init__(self, rows):
        self.rows = rows
        self.committed = False

    def query(self, model):
        return self

    def filter(self, predicate):
        clauses = predicate.clauses
        self.wanted = {clause.left.key: clause.right.value for clause in clauses}
        return self

    def first(self):
        return next((row for row in self.rows if row.id == self.wanted["id"]
                     and row.tenant_id == self.wanted["tenant_id"]), None)

    def commit(self):
        self.committed = True


class Row:
    def __init__(self, id, tenant_id):  # noqa: A002
        self.id, self.tenant_id, self.aktiv = id, tenant_id, True


@pytest.mark.parametrize("kind,endpoint,param", CASES)
def test_dispatch_reaches_the_feed_master_data_handler(kind, endpoint, param):
    assert first_handler(f"/futter/{kind}/own", "DELETE") is endpoint


@pytest.mark.parametrize("kind", ["einzelfuttermittel", "mischfuttermittel"])
def test_generic_bulk_delete_is_gone(kind):
    assert first_handler(f"/futter/{kind}/bulk-delete", "POST") is None


@pytest.mark.parametrize("kind,endpoint,param", CASES)
@pytest.mark.parametrize("roles", [["FUTTERMITTEL_LESEN"], ["FINANCE_READ"]])
def test_reader_and_unrelated_role_denied_before_database(kind, endpoint, param, roles):
    with pytest.raises(HTTPException) as denied:
        asyncio.run(endpoint(**{param: "own"}, tenant_id="tenant-a", db=NoDatabase(),
                             user={"sub": "reader", "roles": roles}))
    assert denied.value.status_code == 403


def test_compound_feed_delete_retires_only_the_own_tenant():
    own, foreign = Row("own", "tenant-a"), Row("foreign", "tenant-b")
    store = CompoundStore([own, foreign])
    result = asyncio.run(futter_stamm.delete_mischfuttermittel(misch_id="own", tenant_id="tenant-a", db=store,
                                                                 user=WRITER))
    assert result.status_code == 204 and own.aktiv is False and store.committed
    with pytest.raises(HTTPException) as missing:
        asyncio.run(futter_stamm.delete_mischfuttermittel(misch_id="foreign", tenant_id="tenant-a",
                                                          db=CompoundStore([foreign]), user=WRITER))
    assert missing.value.status_code == 404
    assert foreign.aktiv is True
