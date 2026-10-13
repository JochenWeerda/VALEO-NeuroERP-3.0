"""UIX-090: SD-Studio Draft-Validierung — harte Sicherheitsregeln.

Reine Unit-Tests (kein DB): fuehre mit
`pytest tests/test_uix090_studio_validation.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""`.
"""
from __future__ import annotations

import pytest

from app.services.studio_validation import load_studio_catalog, validate_studio_draft

pytestmark = pytest.mark.unit

NATIVE = {"crm/customer-360", "finance/ar-open-item", "sales/sales-order"}


def _draft(**overrides):
    base = {
        "schemaVersion": 1,
        "id": "tenant/lieferanten-bewertung",
        "domain": "einkauf",
        "mode": "list",
        "title": "Lieferanten-Bewertung",
        "adapter": {"type": "native", "sourceId": "tenant/lieferanten-bewertung", "temporary": True},
        "actions": [],
    }
    base.update(overrides)
    return base


def _v(draft):
    return validate_studio_draft(draft, native_screen_ids=NATIVE)


def test_catalog_loads():
    load_studio_catalog.cache_clear()
    cat = load_studio_catalog()
    assert cat["version"] == "2026-07"
    assert "create_activity" in cat["actions"]
    assert cat["actions"]["stornieren"]["forbiddenForAgents"] is True
    keys = {ds["key"] for ds in cat["data_sources"]}
    assert {"duenger", "saatgut", "debtors", "consents", "purchase_offers"} <= keys


def test_valider_draft_ohne_verletzung():
    draft = _draft(actions=[{"key": "create_activity", "dangerLevel": "safe"}])
    assert _v(draft) == []


def test_namensraum_ohne_tenant_prefix_verboten():
    assert any(x.startswith("namensraum:") for x in _v(_draft(id="lieferanten-bewertung")))


def test_native_kollision_verboten():
    assert any("kollision" in x for x in _v(_draft(id="crm/customer-360")))


def test_temporary_false_verboten():
    draft = _draft(adapter={"type": "native", "temporary": False})
    assert "adapter_temporary_false_verboten" in _v(draft)


def test_action_nicht_im_katalog_verboten():
    draft = _draft(actions=[{"key": "eigene_gefahr", "dangerLevel": "safe"}])
    assert any(x.startswith("action_nicht_im_katalog") for x in _v(draft))


def test_fremder_command_endpoint_verboten():
    draft = _draft(actions=[{"key": "mahnen", "commandEndpoint": "/api/v1/evil/backdoor"}])
    assert any(x.startswith("action_fremder_commandEndpoint") for x in _v(draft))


def test_danger_level_senken_verboten():
    # stornieren ist im Katalog high — auf safe senken ist verboten
    draft = _draft(actions=[{"key": "stornieren", "dangerLevel": "safe", "forbiddenForAgents": True}])
    assert any(x.startswith("action_dangerLevel_gesenkt") for x in _v(draft))


def test_danger_level_erhoehen_erlaubt():
    # create_activity safe -> moderate erhoehen ist ok
    draft = _draft(actions=[{"key": "create_activity", "dangerLevel": "moderate"}])
    assert not any(x.startswith("action_dangerLevel") for x in _v(draft))


def test_forbidden_for_agents_aufheben_verboten():
    draft = _draft(actions=[{"key": "stornieren", "dangerLevel": "high", "forbiddenForAgents": False, "requiresConfirmation": True}])
    assert any(x.startswith("action_forbiddenForAgents_aufgehoben") for x in _v(draft))


def test_high_ohne_confirmation_verboten():
    draft = _draft(actions=[{"key": "stornieren", "dangerLevel": "high", "forbiddenForAgents": True}])
    assert any(x.startswith("action_confirmation_fehlt") for x in _v(draft))


def test_high_mit_confirmation_erlaubt():
    draft = _draft(actions=[{"key": "stornieren", "dangerLevel": "high", "forbiddenForAgents": True, "requiresConfirmation": True}])
    assert not any(x.startswith("action_confirmation_fehlt") for x in _v(draft))


def test_pflichtfeld_fehlt_verboten():
    draft = _draft()
    del draft["title"]
    assert any(x == "pflichtfeld_fehlt:title" for x in _v(draft))


def test_ungueltiger_danger_level_gemeldet():
    draft = _draft(actions=[{"key": "create_activity", "dangerLevel": "apokalyptisch"}])
    assert any(x.startswith("action_ungueltiger_dangerLevel") for x in _v(draft))


def test_mehrere_verletzungen_werden_alle_gemeldet():
    draft = _draft(
        id="crm/customer-360",  # namensraum + kollision
        adapter={"temporary": False},  # temporary
        actions=[{"key": "stornieren", "dangerLevel": "safe", "forbiddenForAgents": False}],  # danger + forbidden
    )
    violations = _v(draft)
    assert len(violations) >= 4


@pytest.mark.parametrize("placement", ["root", "table", "tab", "nested-section", "agent-contract"])
def test_every_action_location_rejects_unknown_commands(placement):
    action = {"key": "unregistered_payment", "dangerLevel": "safe"}
    locations = {
        "root": {"actions": [action]},
        "table": {"tables": [{"rowActions": [action]}]},
        "tab": {"tabs": [{"tables": [{"rowActions": [action]}]}]},
        "nested-section": {"sections": [{"groups": [{"actions": [action]}]}]},
        "agent-contract": {"agentContract": {"availableActions": [action]}},
    }
    assert "action_nicht_im_katalog:unregistered_payment" in _v(_draft(**locations[placement]))


@pytest.mark.parametrize("flag", [None, False, "true", 1])
def test_omitting_or_coercing_an_agent_prohibition_is_rejected(flag):
    action = {"key": "stornieren", "dangerLevel": "high", "requiresConfirmation": True}
    if flag is not None:
        action["forbiddenForAgents"] = flag
    assert "action_forbiddenForAgents_aufgehoben:stornieren" in _v(_draft(tabs=[{"tables": [{"rowActions": [action]}]}]))


def test_omitted_danger_level_cannot_downgrade_the_runtime_default():
    assert "action_dangerLevel_gesenkt:mahnen" in _v(_draft(actions=[{"key": "mahnen"}]))


@pytest.mark.parametrize("override", [
    {"method": "DELETE"}, {"permission": "admin:all"}, {"command": "finance.payment.execute"},
    {"commandBinding": {"adapter": "docflow.v1", "command": "post"}},
    {"inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/backdoor"}},
])
def test_known_action_cannot_change_transport_or_permission(override):
    violations = _v(_draft(actions=[{"key": "create_activity", "dangerLevel": "safe", **override}]))
    assert any(item.startswith("action_fremd") for item in violations)


@pytest.mark.parametrize("patch", [
    {"id": ["tenant/mask"]}, {"adapter": "native"}, {"actions": "bad"}, {"actions": [None]},
    {"actions": [{"key": []}]}, {"actions": [{"key": "mahnen", "dangerLevel": []}]},
    {"dataSources": [None]}, {"dataSources": [{"endpoint": []}]},
])
def test_malformed_metadata_returns_violations_instead_of_crashing(patch):
    assert _v(_draft(**patch))


def test_nested_field_options_cannot_fetch_a_foreign_endpoint():
    draft = _draft(tabs=[{"fields": [{"key": "selection", "optionsSource": {"endpoint": "https://foreign.example/data"}}]}])
    assert any(item.startswith("datenquelle_nicht_im_katalog") for item in _v(draft))


def test_catalogued_proposals_remain_valid():
    from app.services.studio_propose import propose_studio_draft
    for intent in ("Kunden", "Lieferanten", "offene Posten", "Artikel"):
        assert _v(propose_studio_draft(intent)) == []


@pytest.mark.parametrize("adapter", [
    {"type": "legacy", "sourceId": "tenant/lieferanten-bewertung", "temporary": True},
    {"type": "native", "sourceId": "finance/posting", "temporary": True},
    {"type": "native", "sourceId": "tenant/lieferanten-bewertung"},
    {"type": "native", "sourceId": "tenant/lieferanten-bewertung", "temporary": "true"},
])
def test_studio_cannot_select_a_native_or_legacy_adapter_bypass(adapter):
    assert _v(_draft(adapter=adapter))


def test_boolean_is_not_a_schema_version():
    assert "schemaVersion_muss_1_sein" in _v(_draft(schemaVersion=True))


@pytest.mark.parametrize("policy,agent_patch", [
    ({"dangerLevel": "moderate"}, {"dangerLevel": "safe"}),
    ({"humanApprovalRequired": True}, {"requiresHumanApproval": False}),
    ({"requiresConfirmation": True}, {"requiresConfirmation": False}),
    ({"forbiddenForAgents": True}, {"forbiddenForAgents": False}),
    ({"permission": "studio.draft.execute"}, {"permission": None}),
])
def test_explicit_agent_contract_cannot_weaken_a_stricter_mask_policy(policy, agent_patch):
    action = {"key": "create_activity", "dangerLevel": "safe", **policy}
    advertised = {**action, **agent_patch}
    violations = _v(_draft(actions=[action], agentContract={"availableActions": [advertised]}))
    assert any(item.startswith("agent_action_") for item in violations)


def test_agent_contract_cannot_advertise_an_undeclared_mask_action():
    assert "agent_action_ohne_maskenaktion:create_activity" in _v(_draft(
        agentContract={"availableActions": [{"key": "create_activity", "dangerLevel": "safe"}]}))
