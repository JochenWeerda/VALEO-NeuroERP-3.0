from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

articles = importlib.import_module("app.api.v1.endpoints.articles")


class _RecordingQuery:
    def __init__(self, items=None):
        self.items = list(items or [])
        self.filters: list[str] = []

    def filter(self, *clauses):
        self.filters.extend(str(clause) for clause in clauses)
        return self

    def all(self):
        return list(self.items)


class _RecordingDb:
    def __init__(self, query_map):
        self.query_map = query_map
        self.queries = []

    def query(self, model):
        query = self.query_map.setdefault(model, _RecordingQuery())
        self.queries.append((model, query))
        return query


class _FakeColumn:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return f"{self.name}={other}"


class _FakeArticleDocumentModel:
    article_id = _FakeColumn("article_id")
    tenant_id = _FakeColumn("tenant_id")


def test_resolve_article_tenant_rejects_mismatch():
    with pytest.raises(HTTPException) as exc:
        articles._resolve_article_tenant("tenant-evil", "tenant-a")

    assert exc.value.status_code == 403
    assert exc.value.detail == "Article payload belongs to a different tenant"


@pytest.mark.asyncio
async def test_get_article_documents_filters_documents_by_context_tenant(monkeypatch):
    fake_model = _FakeArticleDocumentModel
    db = _RecordingDb({fake_model: _RecordingQuery(items=[])})

    monkeypatch.setattr(
        articles,
        "_get_article_or_404",
        lambda *_args, **_kwargs: SimpleNamespace(id="art-1"),
    )
    monkeypatch.setattr(articles, "ArticleDocument", fake_model)

    result = await articles.get_article_documents(
        article_id="art-1",
        tenant_id="tenant-a",
        db=db,
    )

    assert result == {"items": []}
    _, query = db.queries[0]
    assert any("tenant_id" in clause for clause in query.filters)
