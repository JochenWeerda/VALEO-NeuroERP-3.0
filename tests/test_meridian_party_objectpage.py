"""Vertrag: eine Object-Page-Akte fuer Kunde, Lead und Stammobjekte."""

from app.core.screen_definitions import get_screen_definition


def _layout(screen_id: str) -> dict:
    screen = get_screen_definition(screen_id)
    assert screen is not None, screen_id
    return screen["layout"]


def test_customer_360_is_object_page_with_identity_and_anchors() -> None:
    screen = get_screen_definition("crm/customer-360")
    assert screen is not None
    assert screen["identityField"] == "firma"
    assert screen["layout"]["floorplan"] == "objectPage"
    assert screen["layout"]["sectionNavigation"] == "anchors"
    assert screen["layout"]["columnNavigation"] == "single"
    assert screen["workflow"]["processKey"] == "crm-party-lifecycle"
    assert [phase["label"] for phase in screen["workflow"]["phases"]] == [
        "Interessent",
        "Qualifiziert",
        "Kunde",
    ]
    assert {item["kind"] for item in screen["summary"]} == {"identity", "status", "kpi", "contact"}
    tab_keys = [tab["key"] for tab in screen["tabs"]]
    assert "finance" in tab_keys
    assert "aufgaben" in tab_keys
    assert "kontrakte" in tab_keys
    assert "praesente" in tab_keys
    assert "postfach" in tab_keys
    finance = next(tab for tab in screen["tabs"] if tab["key"] == "finance")
    assert finance["tables"][0]["dataSourceKey"] == "dokumente"
    praesente = next(tab for tab in screen["tabs"] if tab["key"] == "praesente")
    assert praesente["tables"][0]["dataSourceKey"] == "praesente"
    postfach = next(tab for tab in screen["tabs"] if tab["key"] == "postfach")
    assert {field["key"] for field in postfach["fields"]} >= {"postfach", "postfach_plz", "postfach_ort"}


def test_lead_uses_the_same_object_page_contract() -> None:
    screen = get_screen_definition("crm/lead")
    assert screen is not None
    assert screen["identityField"] == "company_name"
    assert screen["layout"]["floorplan"] == "objectPage"
    assert screen["layout"]["sectionNavigation"] == "anchors"
    assert screen["workflow"]["processKey"] == "crm-party-lifecycle"
    assert any(item.get("kind") == "status" for item in screen["summary"])


def test_attach_mask_aliases_fill_the_object_page_keys() -> None:
    from app.services.customer_service import attach_mask_aliases

    row = attach_mask_aliases(
        {
            "company_name": "Testhof Sonnenacker",
            "customer_number": "KD-100",
            "chefanweisung": "Immer anrufen",
            "payment_terms": 14,
        }
    )
    assert row["firma"] == "Testhof Sonnenacker"
    assert row["kunden_nr"] == "KD-100"
    assert row["notizen"] == "Immer anrufen"
    assert row["zahlungsbedingungen"] == "14"


def test_tenant_as_uuid_keeps_slug_tenants_from_crashing() -> None:
    from uuid import UUID

    from app.services.customer_service import _DEFAULT_TENANT, _tenant_as_uuid

    assert _tenant_as_uuid("test-abc") == UUID(_DEFAULT_TENANT)
    assert _tenant_as_uuid(_DEFAULT_TENANT) == UUID(_DEFAULT_TENANT)


def test_stamm_object_pages_share_the_header_contract() -> None:
    expected = {
        "einkauf/supplier": "lieferantennummer",
        "lager/article-stock": "article_number",
        "agrar/kontrakte": "contract_no",
    }
    for screen_id, identity in expected.items():
        screen = get_screen_definition(screen_id)
        assert screen is not None, screen_id
        assert screen["identityField"] == identity, screen_id
        assert _layout(screen_id)["floorplan"] == "objectPage", screen_id
        assert _layout(screen_id)["sectionNavigation"] == "anchors", screen_id
        assert any(item.get("kind") for item in screen.get("summary") or []), screen_id
