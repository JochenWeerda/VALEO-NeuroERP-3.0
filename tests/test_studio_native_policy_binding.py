"""Native Studio imports inherit only the current source's exact policies."""
from copy import deepcopy
import pytest
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
from app.core.stamm_object_page_parent import ensure_stamm_screen_registry
from app.core.studio_release import definition_hash
from app.services.studio_validation import validate_studio_draft

import json
from pathlib import Path

# Probe einer nativen Maske mit Datei-Import (Wiederholungsschluessel, Agentensperre, Dateigrenze). Bis 08.11.2026
# war das die Verkaufsangebotsliste; seit DocFlow einziger Belegspeicher ist (BELEG-052), liest die Liste
# /belege/sales_offer und hat keinen Import mehr. Die Richtlinie gilt fuer jede solche Aktion; geprueft wird sie an
# der festgehaltenen Fassung.
PROBE = "test/native-import-probe"
_PROBE_DEFINITION = json.loads((Path(__file__).parent / "fixtures/native_policy_import_probe.json")
                               .read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _probe(monkeypatch):
    monkeypatch.setitem(SCREEN_DEFINITION_BUILDERS, PROBE, lambda: deepcopy(_PROBE_DEFINITION))


def draft(screen_id):
    ensure_stamm_screen_registry()
    canonical = get_screen_definition(screen_id)
    return {**deepcopy(canonical), "id": "tenant/policy-probe", "baseScreenId": screen_id,
            "nativeBaseline": {"sourceId": screen_id, "sourceHash": definition_hash(canonical)},
            "adapter": {"type": "native", "sourceId": "tenant/policy-probe", "temporary": True}}


def violations(value):
    return validate_studio_draft(value, native_screen_ids=set(SCREEN_DEFINITION_BUILDERS))


@pytest.mark.parametrize("screen_id", [PROBE, "waage/neu", "crm/customer-360", "finance/datev-export", "lager/article-stock"])
def test_current_native_source_preserves_functional_policy_without_global_key_collision(screen_id):
    value = draft(screen_id)
    assert violations(value) == []
    value["title"] = "Eigene Arbeitsansicht"
    assert violations(value) == []


@pytest.mark.parametrize("change", ["endpoint", "permission", "agent", "replay", "file", "source", "adapter"])
def test_pinned_native_origin_cannot_authorize_a_weakened_or_new_transport(change):
    value = draft(PROBE)
    action = next(action for action in value["actions"] if action["key"] == "import_csv")
    if change == "endpoint": action["commandEndpoint"] = "/api/v1/other-command"
    elif change == "permission": action.pop("permission")
    elif change == "agent": action["forbiddenForAgents"] = False
    elif change == "replay": action["requiresIdempotencyKey"] = False
    elif change == "file": action["inputFields"][0]["fileContent"]["maxBytes"] = 2**30
    elif change == "source": value["nativeBaseline"]["sourceHash"] = "0" * 64
    elif change == "adapter": action["responseAdapter"] = "arbitrary"
    assert violations(value)


def test_foreign_read_source_and_extra_action_stay_forbidden():
    value = draft(PROBE)
    value["dataSources"].append({"key": "foreign", "endpoint": "/api/v1/other-tenant"})
    value["actions"].append({"key": "extra", "dangerLevel": "safe", "localEffect": "print"})
    assert violations(value)


def test_local_classification_cannot_hide_mutation_without_permission():
    from app.core.screen_governance import is_local_view_action
    action = {"key": "print", "dangerLevel": "safe", "localEffect": "print"}
    assert is_local_view_action(action)
    for key in ("commandEndpoint", "inputFlow", "command", "commandBinding", "kommando", "download"):
        assert not is_local_view_action({**action, key: {"method": "POST"}})


@pytest.mark.parametrize("change", ["omit", "foreign", "unversioned"])
def test_native_domain_command_is_immutable(monkeypatch, change):
    screen = PROBE
    builder = SCREEN_DEFINITION_BUILDERS[screen]
    def with_command():
        definition = builder()
        action = next(a for a in definition["actions"] if a["key"] == "import_csv")
        action["domainCommand"] = "test.import.v1"
        return definition
    monkeypatch.setitem(SCREEN_DEFINITION_BUILDERS, screen, with_command)
    value = draft(screen)
    action = next(a for a in value["actions"] if a["key"] == "import_csv")
    assert action["domainCommand"] == "test.import.v1"
    assert violations(value) == []
    if change == "omit":
        del action["domainCommand"]
    elif change == "foreign":
        action["domainCommand"] = "test.other.v1"
    else:
        action["domainCommand"] = "test.import"
    assert violations(value)
