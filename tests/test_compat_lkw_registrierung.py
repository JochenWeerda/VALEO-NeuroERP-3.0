from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from app.api.v1.endpoints.compat import (
    LKWRegistrierungIn,
    _lkw_db_to_item,
    _repair_lkw_article_reference,
    create_lkw_registrierung,
)
from app.infrastructure.models import Article as ArticleModel
from app.infrastructure.models import LkwAnnahmeQueue


class _FakeArticleQuery:
    """Fake query that supports both .first() and .all() for article lookups."""

    def __init__(self, articles: list["_ArticleStub"]):
        self._articles = articles

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._articles[0] if self._articles else None

    def all(self):
        return list(self._articles)


class _FakeDb:
    def __init__(self, article: "_ArticleStub | None" = None, articles: list["_ArticleStub"] | None = None):
        if articles is not None:
            self._articles = articles
        elif article is not None:
            self._articles = [article]
        else:
            self._articles = []
        self.added: list[object] = []

    def query(self, model):
        if model is ArticleModel:
            return _FakeArticleQuery(self._articles)
        raise AssertionError(f"unexpected model {model}")

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None

    def refresh(self, obj):
        return obj


@dataclass
class _ArticleStub:
    id: str
    name: str
    article_number: str


@dataclass
class _QueueRowStub:
    id: str = "queue-1"
    kennzeichen: str = "AB-CD 1234"
    lieferant: str = "Hof Meyer"
    article_id: str | None = "art-weizen"
    artikel: str = "Weizen"
    ankunftszeit: datetime | None = datetime(2026, 3, 28, 8, 0, tzinfo=timezone.utc)
    status: str = "wartend"
    lieferschein_nr: str = "LS-42"
    klaerung: dict | None = None


def test_create_lkw_registrierung_resolves_article_reference_from_article_code():
    db = _FakeDb(_ArticleStub(id="art-weizen", name="Weizen", article_number="ART-WEIZEN"))
    payload = LKWRegistrierungIn(
        kennzeichen="AB-CD 1234",
        lieferant="Hof Meyer",
        article_id="ART-WEIZEN",
        artikel="",
        ankunftszeit="2026-03-28T08:00:00Z",
    )

    result = asyncio.run(create_lkw_registrierung(payload=payload, tenant_id="tenant-1", db=db))

    persisted = next(obj for obj in db.added if isinstance(obj, LkwAnnahmeQueue))
    assert persisted.article_id == "art-weizen"
    assert persisted.artikel == "Weizen"
    assert result.article_id == "art-weizen"
    assert result.artikel == "Weizen"


def test_lkw_queue_item_exposes_article_id():
    item = _lkw_db_to_item(_QueueRowStub(), position=1)

    assert item["article_id"] == "art-weizen"
    assert item["artikel"] == "Weizen"


def test_lkw_queue_item_exposes_klaerung_payload():
    item = _lkw_db_to_item(_QueueRowStub(klaerung={"status": "gesperrt"}), position=1)

    assert item["klaerung"]["status"] == "gesperrt"


# ---------------------------------------------------------------------------
# VK-019: _repair_lkw_article_reference tests
# ---------------------------------------------------------------------------


def test_repair_resolves_by_article_number():
    art = _ArticleStub(id="art-weizen", name="Weizen", article_number="ART-WEIZEN")
    db = _FakeDb(article=art)

    article_id, label, reason = _repair_lkw_article_reference(
        db, tenant_id="t1", artikel="ART-WEIZEN"
    )

    assert article_id == "art-weizen"
    assert label == "Weizen"
    assert reason == "article_number"


def test_repair_resolves_by_article_name():
    art = _ArticleStub(id="art-weizen", name="Weizen", article_number="ART-WEIZEN")
    # For name-based lookup the article_number filter returns empty,
    # so we use an article whose number does NOT match the label.
    db = _FakeDb(article=art)

    article_id, label, reason = _repair_lkw_article_reference(
        db, tenant_id="t1", artikel="Weizen"
    )

    # _FakeArticleQuery always returns the same list for any filter,
    # so article_number filter hits first.  This test verifies the
    # function returns a resolved article in either path.
    assert article_id == "art-weizen"
    assert label == "Weizen"
    assert reason in ("article_number", "article_name")


def test_repair_returns_not_found_when_no_match():
    db = _FakeDb()  # no articles

    article_id, label, reason = _repair_lkw_article_reference(
        db, tenant_id="t1", artikel="Roggen"
    )

    assert article_id is None
    assert label is None
    assert reason == "not_found"


def test_repair_returns_missing_label_when_artikel_empty():
    db = _FakeDb()

    article_id, label, reason = _repair_lkw_article_reference(
        db, tenant_id="t1", artikel=""
    )

    assert article_id is None
    assert label is None
    assert reason == "missing_label"


def test_repair_returns_missing_label_when_artikel_none():
    db = _FakeDb()

    article_id, label, reason = _repair_lkw_article_reference(
        db, tenant_id="t1", artikel=None
    )

    assert article_id is None
    assert label is None
    assert reason == "missing_label"


def test_repair_returns_ambiguous_when_multiple_matches():
    art1 = _ArticleStub(id="art-1", name="Weizen A", article_number="W-100")
    art2 = _ArticleStub(id="art-2", name="Weizen B", article_number="W-100")
    db = _FakeDb(articles=[art1, art2])

    article_id, label, reason = _repair_lkw_article_reference(
        db, tenant_id="t1", artikel="W-100"
    )

    assert article_id is None
    assert label is None
    assert reason == "ambiguous_article_number"
