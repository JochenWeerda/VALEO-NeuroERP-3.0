from decimal import Decimal

from app.api.v1.endpoints.sales_delivery_notes import _quantity_summary


def test_quantities_do_not_mix_units_or_hide_missing_units():
    assert _quantity_summary([
        {"menge": Decimal("2.5"), "einheit": "kg"},
        {"menge": Decimal("1.5"), "einheit": "kg"},
        {"menge": Decimal("3"), "einheit": "Stk"},
        {"menge": Decimal("1"), "einheit": None},
    ]) == "4 kg, 3 Stk, 1 ohne Einheit"
    assert _quantity_summary([]) == ""


def test_delivery_list_reads_docflow_and_opens_the_document_mask():
    """Seit BELEG-052 (08.11.2026) ist die Lieferscheinliste die Variante sales_delivery der Belegliste (DocFlow)."""
    from app.core.screen_definitions import get_screen_definition

    screen = get_screen_definition("beleg-liste/sales-delivery")
    table = screen["tables"][0]
    assert screen["dataSources"][0]["endpoint"] == "/api/v1/belege/sales_delivery"
    assert table["rowRouteTemplate"] == "/belege/sales_delivery/{id}"
    assert not {"netto", "brutto"} & {c["key"] for c in table["columns"]}  # Mengenbeleg ohne Betraege
    assert "unterwegs" not in str(screen)
