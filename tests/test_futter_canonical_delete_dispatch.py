"""Actual delete dispatch rejects readers and preserves foreign/unassigned articles."""
import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import Boolean, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from starlette.routing import Match

from app.api.v1.endpoints import compat, futter_stamm
from app.core.config import settings
from app.core.exceptions import ValidationFailedError
from app.services import inventory_compat_service as service
from main import app


CASES = [
    ("einzelfuttermittel", "DELETE", compat.delete_futter_einzel_item),
    ("mischfuttermittel", "DELETE", compat.delete_futter_misch_item),
    ("einzelfuttermittel", "POST", compat.bulk_delete_futter_einzel),
    ("mischfuttermittel", "POST", compat.bulk_delete_futter_misch),
]
WRITER = {"sub": "writer", "roles": ["FUTTERMITTEL_BEARBEITEN"]}


def first_handler(kind, method):
    path = settings.API_V1_STR + "/futter/" + kind
    path += "/own" if method == "DELETE" else "/bulk-delete"
    scope = {"type": "http", "method": method, "root_path": "", "path": path}
    return next(route.endpoint for route in app.routes if route.matches(scope)[0] == Match.FULL)


def invoke(kind, method, expected, db, user, ids):
    handler = first_handler(kind, method)
    assert handler is expected
    kwargs = {"tenant_id": "tenant-a", "db": db, "user": user}
    kwargs.update({"item_id": ids[0]} if method == "DELETE" else {"payload": compat.FutterBulkDeleteIn(ids=ids)})
    return asyncio.run(handler(**kwargs))


class NoDatabase:
    def query(self, *args):
        raise AssertionError("Denied request reached the database")


class FeedDeleteBase(DeclarativeBase):
    pass


class FeedArticle(FeedDeleteBase):
    __tablename__ = "delete_guard_articles"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean)


@pytest.fixture(scope="module")
def engine():
    shared = create_engine("sqlite://")
    FeedDeleteBase.metadata.create_all(shared)
    yield shared
    shared.dispose()


@pytest.fixture
def db(engine, monkeypatch):
    monkeypatch.setattr(service, "ArticleModel", FeedArticle)
    with engine.connect() as connection:
        connection.exec_driver_sql("BEGIN")
        transaction = connection.get_transaction()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            session.add_all([
                FeedArticle(id="own", tenant_id="tenant-a", is_active=True),
                FeedArticle(id="foreign", tenant_id="tenant-b", is_active=True),
                FeedArticle(id="unassigned", tenant_id=None, is_active=True),
            ])
            session.flush()
            yield session
        transaction.rollback()


@pytest.mark.parametrize("kind,method,endpoint", CASES)
@pytest.mark.parametrize("roles", [["FUTTERMITTEL_LESEN"], ["FINANCE_READ"]])
def test_reader_and_unrelated_role_denied_before_database(kind, method, endpoint, roles):
    with pytest.raises(HTTPException) as denied:
        invoke(kind, method, endpoint, NoDatabase(), {"sub": "reader", "roles": roles}, ["own"])
    assert denied.value.status_code == 403


@pytest.mark.parametrize("kind,method,endpoint", CASES)
def test_writer_deactivates_only_current_tenant_and_keeps_wire_contract(kind, method, endpoint, db):
    ids = ["own", "foreign", "unassigned", "absent"] if method == "POST" else ["own"]
    result = invoke(kind, method, endpoint, db, WRITER, ids)
    if method == "POST":
        assert result.model_dump() == {"requested": 4, "deleted": 1, "missing_ids": ids[1:], "errors": []}
    else:
        assert result.status_code == 204
        assert result.body == b""
    assert db.get(FeedArticle, "own").is_active is False
    assert db.get(FeedArticle, "foreign").is_active is True
    assert db.get(FeedArticle, "unassigned").is_active is True


@pytest.mark.parametrize("kind,method,endpoint", CASES[:2])
@pytest.mark.parametrize("item_id", ["foreign", "unassigned", "absent"])
def test_single_delete_returns_404_without_exposing_other_tenant(kind, method, endpoint, item_id, db):
    with pytest.raises(HTTPException) as missing:
        invoke(kind, method, endpoint, db, WRITER, [item_id])
    assert missing.value.status_code == 404
    assert all(row.is_active for row in db.query(FeedArticle).all())


@pytest.mark.parametrize("kind,method,endpoint", CASES[2:])
def test_bulk_missing_ids_preserve_all_articles(kind, method, endpoint, db):
    ids = ["foreign", "unassigned", "absent"]
    result = invoke(kind, method, endpoint, db, WRITER, ids)
    assert result.model_dump() == {"requested": 3, "deleted": 0, "missing_ids": ids, "errors": []}
    assert all(row.is_active for row in db.query(FeedArticle).all())


def test_service_requires_tenant_before_database():
    with pytest.raises(ValidationFailedError):
        service.FutterCompatService(NoDatabase(), "").soft_delete_artikel(["own"])


def test_canonical_compound_delete_also_requires_writer():
    with pytest.raises(HTTPException) as denied:
        asyncio.run(futter_stamm.delete_mischfuttermittel(misch_id="own", tenant_id="tenant-a",
            db=NoDatabase(), user={"sub": "reader", "roles": ["FUTTERMITTEL_LESEN"]}))
    assert denied.value.status_code == 403
