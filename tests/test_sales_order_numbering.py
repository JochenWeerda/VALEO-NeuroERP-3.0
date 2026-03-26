from app.api.v1.endpoints import sales_orders


def test_resolve_order_number_uses_backend_number_series_when_missing(monkeypatch):
    class _DummyNumbering:
        def next_number(self, domain: str) -> str:
            assert domain == "sales_order"
            return "SO-00991"

    monkeypatch.setattr(sales_orders, "get_numbering", lambda: _DummyNumbering())

    assert sales_orders._resolve_order_number(None) == "SO-00991"
    assert sales_orders._resolve_order_number("   ") == "SO-00991"


def test_resolve_order_number_keeps_explicit_number():
    assert sales_orders._resolve_order_number("SO-00421") == "SO-00421"
