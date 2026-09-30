"""Pure mapping for the CRM Object-Page field keys."""

from app.services.customer_service import attach_mask_aliases


def test_attach_mask_aliases_fills_german_object_page_keys() -> None:
    payload = attach_mask_aliases(
        {
            "id": "abc",
            "company_name": "Hof Nord",
            "customer_number": "GAP00216",
            "address": "Dorf 1",
            "postal_code": "12345",
            "city": "Uelzen",
            "country": "DE",
            "phone": "0581-1",
            "industry": "Agrar",
            "credit_limit": 25000,
            "payment_terms": 14,
            "chefanweisung": "Nur Vorkasse",
        }
    )
    assert payload["firma"] == "Hof Nord"
    assert payload["kunden_nr"] == "GAP00216"
    assert payload["strasse"] == "Dorf 1"
    assert payload["plz"] == "12345"
    assert payload["ort"] == "Uelzen"
    assert payload["telefon"] == "0581-1"
    assert payload["notizen"] == "Nur Vorkasse"
    assert payload["kreditlimit"] == 25000
    assert payload["zahlungsbedingungen"] == "14"
