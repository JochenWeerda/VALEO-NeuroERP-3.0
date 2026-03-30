"""Tests fuer Knowledge Store (NC-06)."""

import pytest

from app.services.knowledge_store import (
    KnowledgeEntry,
    KnowledgeType,
    _IN_MEMORY_STORE,
    store_knowledge,
    get_knowledge,
    search_knowledge,
    delete_knowledge,
    get_knowledge_stats,
)


@pytest.fixture(autouse=True)
def clean_store():
    _IN_MEMORY_STORE.clear()
    yield
    _IN_MEMORY_STORE.clear()


def _make_entry(**kwargs) -> KnowledgeEntry:
    defaults = {
        "knowledge_type": KnowledgeType.BUSINESS_RULE,
        "domain": "einkauf",
        "key": "mindestbestellmenge-soja",
        "title": "Mindestbestellmenge Sojaschrot",
        "content": "Mindestens 25 MT pro Bestellung bei Sojaschrot.",
    }
    defaults.update(kwargs)
    return KnowledgeEntry(**defaults)


class TestStoreKnowledge:
    def test_store_and_retrieve(self):
        entry = _make_entry()
        result = store_knowledge(None, entry)
        assert result.entry_id == entry.entry_id
        assert result.version == 1

        retrieved = get_knowledge(None, "einkauf", "mindestbestellmenge-soja")
        assert retrieved is not None
        assert retrieved.title == "Mindestbestellmenge Sojaschrot"

    def test_store_increments_version_in_memory(self):
        store_knowledge(None, _make_entry(key="test-v"))
        entry2 = _make_entry(key="test-v", title="V2")
        store_knowledge(None, entry2)
        retrieved = get_knowledge(None, "einkauf", "test-v")
        assert retrieved is not None
        assert retrieved.title == "V2"

    def test_store_different_domains(self):
        store_knowledge(None, _make_entry(domain="einkauf", key="regel-a"))
        store_knowledge(None, _make_entry(domain="agrar", key="regel-b"))
        assert get_knowledge(None, "einkauf", "regel-a") is not None
        assert get_knowledge(None, "agrar", "regel-b") is not None
        assert get_knowledge(None, "einkauf", "regel-b") is None


class TestSearchKnowledge:
    def test_search_by_domain(self):
        store_knowledge(None, _make_entry(domain="einkauf", key="a"))
        store_knowledge(None, _make_entry(domain="agrar", key="b"))
        store_knowledge(None, _make_entry(domain="einkauf", key="c"))

        results = search_knowledge(None, domain="einkauf")
        assert len(results) == 2
        assert all(e.domain == "einkauf" for e in results)

    def test_search_by_type(self):
        store_knowledge(None, _make_entry(key="r1", knowledge_type=KnowledgeType.BUSINESS_RULE))
        store_knowledge(None, _make_entry(key="r2", knowledge_type=KnowledgeType.FAQ))
        store_knowledge(None, _make_entry(key="r3", knowledge_type=KnowledgeType.FAQ))

        results = search_knowledge(None, knowledge_type=KnowledgeType.FAQ)
        assert len(results) == 2

    def test_search_by_query(self):
        store_knowledge(None, _make_entry(key="a", title="Sojaschrot Regeln", content="Einkauf von Sojaschrot"))
        store_knowledge(None, _make_entry(key="b", title="Mais Regeln", content="Einkauf von Mais"))
        store_knowledge(None, _make_entry(key="c", title="Raps Info", content="Verkauf von Raps"))

        results = search_knowledge(None, query="soja")
        assert len(results) == 1
        assert results[0].key == "a"

    def test_search_limit(self):
        for i in range(10):
            store_knowledge(None, _make_entry(key=f"item-{i}"))
        results = search_knowledge(None, limit=3)
        assert len(results) == 3


class TestDeleteKnowledge:
    def test_delete_existing(self):
        store_knowledge(None, _make_entry(key="to-delete"))
        assert get_knowledge(None, "einkauf", "to-delete") is not None
        deleted = delete_knowledge(None, "einkauf", "to-delete")
        assert deleted is True
        assert get_knowledge(None, "einkauf", "to-delete") is None

    def test_delete_nonexistent(self):
        deleted = delete_knowledge(None, "einkauf", "does-not-exist")
        assert deleted is False


class TestKnowledgeStats:
    def test_stats_empty(self):
        stats = get_knowledge_stats(None)
        assert stats == {}

    def test_stats_counts(self):
        store_knowledge(None, _make_entry(key="a", knowledge_type=KnowledgeType.BUSINESS_RULE))
        store_knowledge(None, _make_entry(key="b", knowledge_type=KnowledgeType.BUSINESS_RULE))
        store_knowledge(None, _make_entry(key="c", knowledge_type=KnowledgeType.FAQ))
        stats = get_knowledge_stats(None)
        assert stats.get("business_rule") == 2
        assert stats.get("faq") == 1


class TestKnowledgeEntryModel:
    def test_to_dict(self):
        entry = _make_entry()
        d = entry.to_dict()
        assert d["knowledge_type"] == "business_rule"
        assert d["domain"] == "einkauf"
        assert d["key"] == "mindestbestellmenge-soja"
        assert d["version"] == 1
        assert d["active"] is True

    def test_all_types(self):
        for kt in KnowledgeType:
            entry = _make_entry(knowledge_type=kt, key=f"test-{kt.value}")
            assert entry.knowledge_type == kt
            assert entry.to_dict()["knowledge_type"] == kt.value
