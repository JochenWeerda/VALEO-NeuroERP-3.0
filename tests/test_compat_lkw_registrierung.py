from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from app.api.v1.endpoints.compat import LKWRegistrierungIn, _lkw_db_to_item, create_lkw_registrierung
from app.infrastructure.models import Article as ArticleModel
from app.infrastructure.models import LkwAnnahmeQueue


class _FakeArticleQuery:
    def __init__(self, article: "_ArticleStub | None"):
        self.article = article

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self.article


class _FakeDb:
    def __init__(self, article: "_ArticleStub | None"):
        self.article = article
        self.added: list[object] = []

    def query(self, model):
        if model is ArticleModel:
            return _FakeArticleQuery(self.article)
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
