from app.api.v1.endpoints.crm_360 import build_customer_screen_summary


def test_customer_screen_summary_is_compact_generator_contract() -> None:
    payload = build_customer_screen_summary(
        customer_id="cust-1",
        tenant_id="tenant-1",
        customer={"name": "Musterkunde", "kunden_nr": "K-100"},
        sales_ytd=12_500.0,
        open_items_total=0.0,
        recent_activity_count=3,
    )

    assert payload["schema_version"] == 1
    assert payload["screen_id"] == "crm/customer-360"
    assert payload["title"] == "Musterkunde"
    assert payload["summary"]["sales_ytd"] == 12_500.0
    assert payload["summary"]["credit_status"] == "ok"
    assert "dokumente" in payload["available_tabs"]
    assert payload["performance"]["tabs_lazy"] is True
    assert payload["performance"]["lookup_min_chars"] == 2
    assert "tab_endpoints" in payload
    assert "contacts" in payload["tab_endpoints"]


def test_customer_screen_summary_warns_on_open_items() -> None:
    payload = build_customer_screen_summary(
        customer_id="cust-1",
        tenant_id=None,
        customer={"name": "Musterkunde"},
        open_items_total=250.0,
    )

    assert payload["summary"]["credit_status"] == "warning"
    assert payload["badges"][0] == {"key": "credit", "label": "Kredit", "tone": "warning"}
