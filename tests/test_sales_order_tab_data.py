from app.api.v1.endpoints.sales_orders import (
    _fetch_delivery_notes_for_order,
    _fetch_order_documents,
)


class _FakeSession:
    def execute(self, *_args, **_kwargs):
        raise RuntimeError("missing table")

    def rollback(self) -> None:
        return None


def test_fetch_delivery_notes_returns_empty_on_missing_table() -> None:
    items = _fetch_delivery_notes_for_order(_FakeSession(), "order-1", "tenant-1")
    assert items == []


def test_fetch_order_documents_returns_empty_on_missing_table() -> None:
    items = _fetch_order_documents(_FakeSession(), "order-1", "tenant-1")
    assert items == []
