from app.api.v1.endpoints.sales_orders import build_sales_order_screen_summary


def test_sales_order_screen_summary_contract() -> None:
    payload = build_sales_order_screen_summary(
        order_id="order-1",
        tenant_id="tenant-1",
        order={
            "order_number": "SO-100",
            "subject": "Weizen Lieferung",
            "status": "open",
            "total_amount": 1500.0,
        },
        item_count=3,
        customer_name="Musterkunde AG",
    )

    assert payload["schema_version"] == 1
    assert payload["screen_id"] == "sales/sales-order"
    assert payload["summary"]["item_count"] == 3
    assert payload["tab_endpoints"]["positionen"].endswith("/sales/orders/order-1/tabs/positionen")
    assert payload["performance"]["tabs_lazy"] is True


def test_sales_order_screen_summary_includes_customer_name() -> None:
    payload = build_sales_order_screen_summary(
        order_id="order-1",
        tenant_id="tenant-1",
        order={"order_number": "SO-100", "subject": "Test"},
        item_count=0,
        customer_name="Kunde X",
    )

    assert payload["customer_name"] == "Kunde X"
