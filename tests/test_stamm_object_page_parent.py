"""Vertrag: StammObjectPageParent-Shell fuer alle 12 Stamm-Children (UIX-STAMM-OBJECTPAGE-ALL)."""

from __future__ import annotations

import pytest

from app.api.v1.endpoints.mask_screen_definition import _check_readiness, _generate_agent_contract
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
from app.core.screen_definitions_stamm import STAMM_SCREEN_BUILDERS, build_artikel_stamm
from app.core.stamm_object_page_parent import build_stamm_object_page, stamm_entity_source, stamm_kopf_tab
from app.core.studio_release import definition_hash
from app.services import studio_native_import

STAMM_REGISTERED_SCREENS = (
    "agrar/duenger",
    "agrar/saatgut",
    "einkauf/supplier",
    "finance/debitor",
    "finance/kreditor",
    "finance/bankkonto",
    "lager/article-stock",
    "crm/opportunity",
    "crm/lead",
    "futtermittel/einzelfuttermittel",
    "futtermittel/mischfuttermittel",
)

ALL_STAMM_SCREENS = (*STAMM_REGISTERED_SCREENS, "artikel/stamm")

SHARED_LAYOUT_KEYS = {
    "floorplan": "objectPage",
    "sectionNavigation": "anchors",
    "columnNavigation": "single",
    "summaryPlacement": "header",
    "stickyHeader": True,
    "stickyFooter": True,
    "preferredMode": "desktopDense",
    "mobileMode": "mobileStack",
    "touchTargetPx": 44,
}

IDENTITY_BY_SCREEN = {
    "agrar/duenger": "artikelnummer",
    "agrar/saatgut": "artikelnummer",
    "einkauf/supplier": "lieferantennummer",
    "finance/debitor": "debitoren_nr",
    "finance/kreditor": "kreditoren_nr",
    "finance/bankkonto": "iban",
    "lager/article-stock": "article_number",
    "crm/opportunity": "name",
    "crm/lead": "company_name",
    "futtermittel/einzelfuttermittel": "artikel_nummer",
    "futtermittel/mischfuttermittel": "produkt_code",
    "artikel/stamm": "article_number",
}


def _load_stamm_screen(screen_id: str) -> dict:
    if screen_id == "artikel/stamm":
        return build_artikel_stamm()
    screen = get_screen_definition(screen_id)
    assert screen is not None, screen_id
    return screen


@pytest.mark.parametrize("screen_id", ALL_STAMM_SCREENS)
def test_all_stamm_children_share_stamm_object_page_shell(screen_id: str) -> None:
    screen = _load_stamm_screen(screen_id)
    assert screen["mode"] == "detail"
    assert screen["adapter"]["type"] == "native"
    assert screen["adapter"]["temporary"] is False
    assert screen.get("identityField") == IDENTITY_BY_SCREEN[screen_id]
    assert screen["tabs"][0]["key"] == "kopf"
    assert screen["tabs"][0]["lazy"] is False
    assert any(ds["key"] == "entity" for ds in screen["dataSources"])
    primary_actions = [action for action in screen["actions"] if action.get("kind") == "primary"]
    assert len(primary_actions) == 1
    primary_key = primary_actions[0]["key"]
    edit = next(action for action in screen["actions"] if action["key"] == primary_key)
    assert edit["kind"] == "primary"
    if screen_id in {"finance/debitor", "finance/kreditor", "finance/bankkonto"}:
        assert edit["dangerLevel"] == "moderate"
        assert edit["auditReasonRequired"] is True
        assert edit.get("commandEndpoint")
    else:
        assert edit["dangerLevel"] == "safe"
    assert "permission" in edit
    layout = screen["layout"]
    for key, value in SHARED_LAYOUT_KEYS.items():
        assert layout[key] == value, f"{screen_id}.layout.{key}"
    assert layout["density"] in {"compact", "expertDense"}
    assert layout["contextRail"] in {"audit", "combined", "copilot", "workflow"}
    assert layout["tableProfile"] in {"standard", "financial", "inventory", "audit"}
    assert any(item.get("kind") == "identity" for item in screen.get("summary") or [])
    assert (
        screen["agentContract"]["testSelectors"]["primaryAction"]
        == f"[data-testid='action-{primary_key}']"
    )
    assert screen.get("noWorkflowReason") or screen.get("workflow")


@pytest.mark.parametrize("screen_id", ALL_STAMM_SCREENS)
def test_all_stamm_children_pass_studio_gate_a_readiness_and_agent_contract(screen_id: str) -> None:
    screen = _load_stamm_screen(screen_id)
    readiness = _check_readiness(screen)
    assert readiness["generatorReady"] is True, f"{screen_id}: {readiness['errors']}"
    assert readiness["resolvedLayout"] == {
        "floorplan": "objectPage",
        "sectionNavigation": "anchors",
        "identityField": IDENTITY_BY_SCREEN[screen_id],
    }
    contract = _generate_agent_contract(screen)
    assert contract["screenId"] == screen_id
    assert contract["businessPurpose"]
    assert contract["readableFields"]
    assert contract["availableActions"]


def test_registered_stamm_children_are_discoverable_as_studio_native_sources() -> None:
    sources = studio_native_import.list_sources("default", limit=2000)
    by_id = {item["screen_id"]: item for item in sources["items"]}
    for screen_id in STAMM_REGISTERED_SCREENS:
        assert screen_id in SCREEN_DEFINITION_BUILDERS
        assert screen_id in by_id, f"{screen_id} fehlt in Studio native-sources"
        expected_hash = definition_hash(get_screen_definition(screen_id, tenant_id="default"))
        assert by_id[screen_id]["source_hash"] == expected_hash


def test_supplier_keeps_secondary_bestellung_action() -> None:
    screen = get_screen_definition("einkauf/supplier")
    assert screen is not None
    keys = [action["key"] for action in screen["actions"]]
    assert keys[0] == "bearbeiten"
    assert "neue_bestellung" in keys
    assert screen["layout"]["density"] == "expertDense"
    assert screen["layout"]["contextRail"] == "combined"
    assert screen["summaryEndpoint"].endswith("/screen-summary")


def test_finance_children_use_audit_rail_and_financial_profile() -> None:
    for screen_id in ("finance/debitor", "finance/kreditor", "finance/bankkonto"):
        screen = get_screen_definition(screen_id)
        assert screen is not None
        assert screen["layout"]["density"] == "expertDense"
        assert screen["layout"]["contextRail"] == "audit"
        assert screen["layout"]["tableProfile"] == "financial"
        assert screen["performance"]["requiresVirtualTables"] is True


def test_article_stock_and_crm_children_keep_domain_contracts() -> None:
    stock = get_screen_definition("lager/article-stock")
    opp = get_screen_definition("crm/opportunity")
    lead = get_screen_definition("crm/lead")
    assert stock is not None and opp is not None and lead is not None
    assert stock["interaction"]["enterMovesFocus"] is True
    assert stock["actions"][0]["zone"] == "commit"
    bewegungen = next(tab["tables"][0] for tab in stock["tabs"] if tab["key"] == "bewegungen")
    assert bewegungen["rowRouteTemplate"] == "/lager/stock-movement/{movement_id}"
    assert [tab["key"] for tab in opp["tabs"]] == ["kopf", "zuordnung", "aktivitaeten", "angebote"]
    assert any(action["key"] == "create_activity" for action in opp["actions"])
    assert lead["workflow"]["processKey"] == "crm-party-lifecycle"
    assert any(action["key"] == "qualifizieren" for action in lead["actions"])
    assert lead["creation"]["detailRoute"] == "/crm/lead/{entity_id}"


def test_agrar_saatgut_and_duenger_have_native_creation() -> None:
    """Create-Paritaet: keine Legacy-ObjectPage mehr fuer Neuanlage (STUDIO-MADE-OPEN-ROUTES)."""
    for screen_id, endpoint, detail in (
        ("agrar/saatgut", "/api/v1/agrar/saatgut/", "/agrar/saatgut/{entity_id}"),
        ("agrar/duenger", "/api/v1/agrar/duenger/", "/agrar/duenger/{entity_id}"),
    ):
        screen = get_screen_definition(screen_id)
        assert screen is not None
        creation = screen["creation"]
        assert creation["endpoint"] == endpoint
        assert creation["detailRoute"] == detail
        assert creation["permission"].endswith(".create")
        assert any(field["required"] for field in creation["fields"])


def test_bankkonto_kreditor_opportunity_have_native_creation() -> None:
    """Batch 2 Create-Paritaet: Bankkonto/Kreditor/Opportunity ohne Legacy-Anlage."""
    for screen_id, endpoint, detail, required_keys in (
        (
            "finance/bankkonto",
            "/api/v1/banken/konten",
            "/finance/bankkonto/{entity_id}",
            {"iban", "bic", "bank_name", "kontoart"},
        ),
        (
            "finance/kreditor",
            "/api/v1/finance/creditors",
            "/finance/kreditor/{entity_id}",
            {"creditor_number", "company_name"},
        ),
        (
            "crm/opportunity",
            "/api/v1/crm/opportunities/",
            "/crm/opportunity/{entity_id}",
            {"name"},
        ),
    ):
        screen = get_screen_definition(screen_id)
        assert screen is not None
        creation = screen["creation"]
        assert creation["endpoint"] == endpoint
        assert creation["detailRoute"] == detail
        assert creation["permission"].endswith(".create")
        keys = {field["key"] for field in creation["fields"]}
        assert required_keys <= keys
        assert "tenant_id" not in keys


def test_einkauf_anfrage_has_native_creation() -> None:
    """Batch 3: Einkaufsanfrage Create ohne Legacy-ObjectPage."""
    screen = get_screen_definition("einkauf/anfrage")
    assert screen is not None
    creation = screen["creation"]
    assert creation["endpoint"] == "/api/v1/einkauf/anfragen"
    assert creation["detailRoute"] == "/einkauf/anfrage/{entity_id}"
    assert creation["permission"] == "einkauf.anfrage.create"
    keys = {field["key"] for field in creation["fields"]}
    assert {"typ", "anforderer"} <= keys
    assert any(field.get("required") and field["key"] == "anforderer" for field in creation["fields"])


def test_qualitaet_reklamation_has_native_creation() -> None:
    """Batch 3: Reklamation Create mit responseIdKey reklamation_id."""
    screen = get_screen_definition("qualitaet/reklamation")
    assert screen is not None
    creation = screen["creation"]
    assert creation["endpoint"] == "/api/v1/reklamationen"
    assert creation["detailRoute"] == "/qualitaet/reklamation/{entity_id}"
    assert creation["responseIdKey"] == "reklamation_id"
    keys = {field["key"] for field in creation["fields"]}
    assert {"lieferant_id", "typ", "zustaendiger", "frist_datum", "positionen"} <= keys


def test_crm_kontakt_has_native_creation() -> None:
    """Batch 3: Kontakt Create (nested data.id in der API-Antwort)."""
    screen = get_screen_definition("crm/kontakt")
    assert screen is not None
    creation = screen["creation"]
    assert creation["endpoint"] == "/api/v1/crm/contacts/"
    assert creation["detailRoute"] == "/crm/kontakt/{entity_id}"
    keys = {field["key"] for field in creation["fields"]}
    assert {"customer_id", "first_name", "last_name", "email"} <= keys


def test_qualitaet_labor_has_native_creation() -> None:
    """Batch 3: Laborauftrag Create an Detail-SD (nicht Listen-ID)."""
    screen = get_screen_definition("qualitaet/labor-detail")
    assert screen is not None
    creation = screen["creation"]
    assert creation["endpoint"] == "/api/v1/qualitaet/labor-auftraege"
    assert creation["detailRoute"] == "/qualitaet/labor/{entity_id}"
    keys = {field["key"] for field in creation["fields"]}
    assert {"chargenId", "labor"} <= keys


def test_service_anfrage_has_native_creation() -> None:
    """Batch 3: Service-Anfrage Create (neu + detail)."""
    for screen_id in ("service/anfrage/neu", "service/anfrage-detail"):
        screen = get_screen_definition(screen_id)
        assert screen is not None
        creation = screen["creation"]
        assert creation["endpoint"] == "/api/v1/service/anfragen"
        assert creation["detailRoute"] == "/service/anfrage/{entity_id}"
        keys = {field["key"] for field in creation["fields"]}
        assert {"kunde", "betreff"} <= keys


def test_futtermittel_and_artikel_stamm_keep_domain_tabs() -> None:
    efm = get_screen_definition("futtermittel/einzelfuttermittel")
    mfm = get_screen_definition("futtermittel/mischfuttermittel")
    artikel = build_artikel_stamm()
    assert efm is not None and mfm is not None
    assert [tab["key"] for tab in efm["tabs"]] == ["kopf", "naehrstoffe", "preise", "history"]
    history_table = next(tab["tables"][0] for tab in efm["tabs"] if tab["key"] == "history")
    assert history_table["serverPagination"] is False
    assert [tab["key"] for tab in mfm["tabs"]] == ["kopf", "rezeptur", "naehrstoffe"]
    assert [tab["key"] for tab in artikel["tabs"]] == [
        "kopf",
        "preise_steuer",
        "lager",
        "qualitaet",
        "lieferanten",
        "preise",
        "dokumente",
    ]
    assert artikel["actions"][0]["commandEndpoint"] == "/api/v1/articles/{entity_id}/actions/bearbeiten"


def test_parent_rejects_missing_kopf_tab() -> None:
    with pytest.raises(ValueError, match="kopf"):
        build_stamm_object_page(
            screen_id="x/y",
            domain="x",
            title="X",
            subtitle="Y",
            identity_field="id",
            data_sources=[stamm_entity_source("/api/v1/x/{entity_id}")],
            tabs=[{"key": "other", "label": "X", "fields": []}],
            edit_permission="x.update",
            no_workflow_reason="test",
            business_purpose="test",
            example_prompts=["a"],
            test_id="x-y",
        )


def test_parent_rejects_missing_entity_source() -> None:
    with pytest.raises(ValueError, match="entity"):
        build_stamm_object_page(
            screen_id="x/y",
            domain="x",
            title="X",
            subtitle="Y",
            identity_field="id",
            data_sources=[{"key": "list", "endpoint": "/api/v1/x"}],
            tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}])],
            edit_permission="x.update",
            no_workflow_reason="test",
            business_purpose="test",
            example_prompts=["a"],
            test_id="x-y",
        )


def test_parent_rejects_missing_workflow_and_no_workflow_reason() -> None:
    with pytest.raises(ValueError, match="no_workflow_reason oder workflow"):
        build_stamm_object_page(
            screen_id="x/y",
            domain="x",
            title="X",
            subtitle="Y",
            identity_field="id",
            data_sources=[stamm_entity_source("/api/v1/x/{entity_id}")],
            tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}])],
            edit_permission="x.update",
            business_purpose="test",
            example_prompts=["a"],
            test_id="x-y",
        )


@pytest.mark.parametrize("screen_id", sorted(STAMM_SCREEN_BUILDERS.keys()))
def test_batch9_stamm_builders_pass_gate_a(screen_id: str) -> None:
    builder = STAMM_SCREEN_BUILDERS[screen_id]
    screen = builder()
    readiness = _check_readiness(screen)
    assert readiness["generatorReady"] is True, f"{screen_id}: {readiness['errors']}"
    if screen["layout"].get("floorplan") == "wizard":
        # Annahme-Wizards (LKW-Registrierung, Qualitaetspruefung) stehen in der Registry, sind aber
        # gefuehrte Formulare ohne Objektquelle; fuer sie gelten nur Bereitschaft und Aktionsrechte.
        assert screen.get("mode") == "wizard", screen_id
    elif screen["layout"].get("floorplan") == "worklist":
        assert screen["mode"] == "list", screen_id
        sources = {source["key"]: source["endpoint"] for source in screen["dataSources"]}
        assert screen["tables"], screen_id
        for table in screen["tables"]:
            endpoint = sources[table["dataSourceKey"]]
            assert endpoint.startswith("/api/") and "{" not in endpoint, screen_id
    else:
        entity = next(ds for ds in screen["dataSources"] if ds["key"] == "entity")
        assert "{entity_id}" in entity["endpoint"] or "{id}" in entity["endpoint"]
        identity = screen.get("identityField")
        if identity:
            kopf = next(tab for tab in screen["tabs"] if tab["key"] == "kopf")
            keys = {f["key"] for f in kopf.get("fields") or []}
            assert identity in keys, f"{screen_id}: identityField {identity} fehlt im Kopf-Tab"
    for action in screen.get("actions", []):
        # Lokale Navigation und CSV aus der bereits autorisierten Liste haben keinen Schreibendpunkt.
        local_effect = action.get("localEffect")
        local_csv = local_effect == "download" and action.get("command") == "list.exportCsv"
        rein_lokal = ((local_effect in {"navigation", "view"} or local_csv)
                      and not action.get("commandEndpoint") and not action.get("inputFlow"))
        if not rein_lokal:
            assert action.get("permission"), f"{screen_id}: action {action['key']} ohne permission"


def test_duenger_and_saatgut_keep_domain_tabs() -> None:
    duenger = get_screen_definition("agrar/duenger")
    saatgut = get_screen_definition("agrar/saatgut")
    assert duenger is not None and saatgut is not None
    assert [tab["key"] for tab in duenger["tabs"]] == ["kopf", "verwendung", "preise"]
    assert [tab["key"] for tab in saatgut["tabs"]] == ["kopf", "lagerbestaende", "vertraege"]
    assert duenger["layout"]["density"] == "compact"
    assert duenger["layout"]["contextRail"] == "combined"
