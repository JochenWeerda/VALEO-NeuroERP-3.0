"""RAG-Suche und Wissensbasis: Mandantenbindung ohne Datenbank pruefen (RLS-DOMAIN-KI-20261027)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from app.core.tenant_context import tenant_scope

pytestmark = pytest.mark.unit


def test_suchfilter_bindet_immer_den_mandanten():
    from app.api.v1.endpoints.rag import tenant_where

    assert tenant_where("m-a", None) == {"tenant_id": "m-a"}
    assert tenant_where("m-a", {}) == {"tenant_id": "m-a"}
    # Filter des Aufrufers schraenken ein, ersetzen den Mandanten aber nie.
    assert tenant_where("m-a", {"tenant_id": "m-b"}) == {"$and": [{"tenant_id": "m-a"}, {"tenant_id": "m-b"}]}
    assert tenant_where("m-a", {"kategorie": "duenger"}) == {"$and": [{"tenant_id": "m-a"}, {"kategorie": "duenger"}]}


def test_suche_fragt_den_vektorspeicher_nur_im_eigenen_mandanten(monkeypatch):
    from app.api.v1.endpoints import rag

    gesehen = {}

    class _Store:
        async def search(self, collection_name, query, n_results, where):
            gesehen.update(collection=collection_name, where=where)
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}

    monkeypatch.setattr(rag, "get_vector_store", lambda: _Store())
    antwort = asyncio.run(rag.semantic_search(rag.SearchRequest(query="Weizen", collection="customers"), tenant_id="m-a"))
    assert antwort.total == 0
    assert gesehen == {"collection": "customers", "where": {"tenant_id": "m-a"}}


def test_wissensbasis_aendert_nur_eigene_objekte():
    from app.repositories.knowledge_repository import SharedKnowledgeReadOnly, _ensure_writable

    eigenes = SimpleNamespace(knowledge_id="K-1", tenant_id="m-a")
    gemeinsames = SimpleNamespace(knowledge_id="K-2", tenant_id="system")
    with tenant_scope("m-a", "test"):
        _ensure_writable(eigenes)
        with pytest.raises(SharedKnowledgeReadOnly):
            _ensure_writable(gemeinsames)
    with tenant_scope("m-b", "test"):
        with pytest.raises(SharedKnowledgeReadOnly):
            _ensure_writable(eigenes)
    _ensure_writable(gemeinsames)  # zentrale Pflege ohne Mandantenkontext (valeo_system)


def test_wissensversion_traegt_den_mandanten():
    from app.models.knowledge import KnowledgeVersionRecord

    column = KnowledgeVersionRecord.__table__.c.tenant_id
    assert column.nullable is False
