from decimal import Decimal

from app.api.v1.endpoints.sales_delivery_notes import _quantity_summary
from app.core.screen_definitions_listen import build_sales_lieferungen_liste


def test_quantities_do_not_mix_units_or_hide_missing_units():
    assert _quantity_summary([
        {"menge": Decimal("2.5"), "einheit": "kg"},
        {"menge": Decimal("1.5"), "einheit": "kg"},
        {"menge": Decimal("3"), "einheit": "Stk"},
        {"menge": Decimal("1"), "einheit": None},
    ]) == "4 kg, 3 Stk, 1 ohne Einheit"
    assert _quantity_summary([]) == ""


def test_delivery_screen_uses_actual_projection_and_safe_order_navigation():
    screen = build_sales_lieferungen_liste()
    table = screen["tables"][0]
    assert table["rowRouteTemplate"] == "/sales/delivery-editor?id={id}"
    assert {c["key"] for c in table["columns"]} >= {"delivery_note_number", "quantity_summary", "sales_order_number", "is_delivered"}
    order = table["rowActions"][0]
    assert order["visibleWhen"] == {"field": "has_sales_order", "values": [True]}
    assert order["navigationRoute"] == "/sales/order-editor?id={sales_order_id}"
    assert "unterwegs" not in str(screen)
