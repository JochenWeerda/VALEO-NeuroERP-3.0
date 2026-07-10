from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.seeds import inventory_seed


class _Result:
    def __init__(self, value: Any = None) -> None:
        self.value = value

    def scalar(self) -> Any:
        return self.value


class _FakeConnection:
    def __init__(self, existing_articles: set[str] | None = None) -> None:
        self.existing_articles = existing_articles or set()
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _Result:
        sql = str(statement)
        payload = params or {}
        self.calls.append((sql, payload))

        if "SELECT id FROM domain_shared.tenants" in sql:
            return _Result(settings.DEFAULT_TENANT_ID)
        if "SELECT 1 FROM domain_inventory.warehouses" in sql:
            return _Result(None)
        if "SELECT 1 FROM domain_inventory.articles" in sql:
            return _Result(1 if payload.get("number") in self.existing_articles else None)
        return _Result(None)


def test_seed_articles_are_bookable_default_tenant_data() -> None:
    numbers = {str(article["article_number"]) for article in inventory_seed.ARTICLES}

    assert inventory_seed.TENANT_ID == settings.DEFAULT_TENANT_ID
    assert {"GET-WEI-B", "SEED-00123", "FERT-2007", "DUE-KAS-27", "PSM-HERB-GET", "FUT-MILCH-18"}.issubset(numbers)
    for article in inventory_seed.ARTICLES:
        assert article["unit"]
        assert article["purchase_price"] > 0
        assert article["sales_price"] > 0
        assert article["current_stock"] > 0
        assert article["category"]


def test_ensure_articles_inserts_missing_seed_articles() -> None:
    conn = _FakeConnection()

    inventory_seed.ensure_articles(conn, settings.DEFAULT_TENANT_ID)

    inserts = [call for call in conn.calls if "INSERT INTO domain_inventory.articles" in call[0]]
    assert len(inserts) == len(inventory_seed.ARTICLES)
    assert all(call[1]["tenant_id"] == settings.DEFAULT_TENANT_ID for call in inserts)
    assert any(call[1]["article_number"] == "GET-WEI-B" for call in inserts)
    for _, payload in inserts:
        assert isinstance(payload["current_stock"], int)
        assert isinstance(payload["min_stock"], int)
        assert isinstance(payload["max_stock"], int)


def test_ensure_articles_updates_existing_seed_articles_without_duplicate_insert() -> None:
    conn = _FakeConnection(existing_articles={"GET-WEI-B"})

    inventory_seed.ensure_articles(conn, settings.DEFAULT_TENANT_ID)

    updates = [call for call in conn.calls if "UPDATE domain_inventory.articles" in call[0]]
    inserts = [call for call in conn.calls if "INSERT INTO domain_inventory.articles" in call[0]]

    assert any(call[1]["article_number"] == "GET-WEI-B" for call in updates)
    assert not any(call[1]["article_number"] == "GET-WEI-B" for call in inserts)
