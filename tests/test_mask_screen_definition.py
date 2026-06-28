from app.core.screen_definitions import get_screen_definition


def test_get_crm_customer_360_screen_definition() -> None:
    definition = get_screen_definition("crm/customer-360")

    assert definition is not None
    assert definition["schemaVersion"] == 1
    assert definition["id"] == "crm/customer-360"
    assert definition["adapter"]["temporary"] is False
    assert definition["performance"]["requiresLazyTabs"] is True
    assert definition["performance"]["lookupMinChars"] >= 2


def test_get_sales_order_screen_definition() -> None:
    definition = get_screen_definition("sales/sales-order")

    assert definition is not None
    assert definition["id"] == "sales/sales-order"
    assert definition["adapter"]["temporary"] is False
    assert definition["performance"]["requiresLazyTabs"] is True


def test_get_screen_definition_unknown_mask_returns_none() -> None:
    assert get_screen_definition("unknown/mask") is None
