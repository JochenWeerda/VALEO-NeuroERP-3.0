"""Studio-Objektmaske fuer das bestehende mandantengebundene Sortenregister."""
from app.core.stamm_object_page_parent import build_stamm_object_page, stamm_entity_source, stamm_kopf_tab


def build_agrar_sorte_stamm() -> dict:
    fields = [
        {"key": "variety_number", "label": "Sortennummer", "type": "text", "required": True},
        {"key": "name", "label": "Sorte", "type": "text", "required": True},
        {"key": "description", "label": "Beschreibung", "type": "text"},
        {"key": "crop_type", "label": "Kultur", "type": "text"},
        {"key": "zuechter", "label": "Züchter", "type": "text"},
        {"key": "zulassungsjahr", "label": "Zulassungsjahr", "type": "number"},
        {"key": "reifezahl", "label": "Reifezahl", "type": "text"},
        {"key": "qualitaetsgruppe", "label": "Qualitätsgruppe", "type": "text"},
    ]
    endpoint = "/api/v1/agrar/varieties/{entity_id}"
    return build_stamm_object_page(
        screen_id="agrar/saatgut/sorte", domain="agrar", title="Sorte", subtitle="Sortenregister",
        identity_field="name", data_sources=[stamm_entity_source(endpoint)],
        tabs=[stamm_kopf_tab([*fields, {"key": "aktiv", "label": "Aktiv", "type": "boolean", "readOnly": True}])],
        edit_permission="agrar.sorte.update", no_workflow_reason="Sortenstamm ohne eigenen Ablauf.",
        business_purpose="Sortenstammdaten anzeigen und bearbeiten.", example_prompts=["Welche Kultur hat Sorte {entity_id}?"],
        test_id="agrar-sorte-stamm", bundle_group="agrar",
        edit_action_overrides={"commandEndpoint": endpoint, "method": "PUT", "forbiddenForAgents": True,
                               "responseAdapter": "resource.v1", "inputPrefill": "entity", "inputFields": fields},
    )
