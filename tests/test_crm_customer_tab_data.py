from app.api.v1.endpoints.crm_360 import (
    _fetch_customer_tab_items,
    build_customer_screen_summary,
)


class _FakeSession:
    pass


def test_customer_screen_summary_exposes_tab_endpoints() -> None:
    payload = build_customer_screen_summary(
        customer_id="cust-1",
        tenant_id="tenant-1",
        customer={"name": "Musterkunde", "kunden_nr": "K-100"},
    )

    assert "tab_endpoints" in payload
    assert payload["tab_endpoints"]["contacts"].endswith("/crm/customers/cust-1/tabs/contacts")
    assert payload["tab_endpoints"]["kontakte"].endswith("/crm/customers/cust-1/tabs/kontakte")
    assert payload["tab_endpoints"]["auftraege"].endswith("/crm/customers/cust-1/tabs/auftraege")


def test_fetch_customer_tab_items_returns_empty_for_unmapped_tabs() -> None:
    table_key, items = _fetch_customer_tab_items(
        _FakeSession(),
        customer_id="cust-1",
        tenant_id="tenant-1",
        tab_key="angebote",
        kunden_nr="K-100",
    )

    assert table_key == "angebote"
    assert items == []
