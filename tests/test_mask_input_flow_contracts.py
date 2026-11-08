"""Human input flows are explicit and cannot masquerade as executable commands."""
from copy import deepcopy

import pytest

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
from scripts.check_mask_command_endpoint_inventory import valid_input_flow


def flows():
    return [action for screen in SCREEN_DEFINITION_BUILDERS
            for action in get_screen_definition(screen).get("actions", [])
            if action.get("inputFlow")]


def test_all_current_human_flows_have_guarded_submit_contracts():
    actions = flows()
    expected = {
        ("lager/inventur-nebenlaeufe", "create_opening"),
        ("agrar/feed-readiness", "create_handoff"),
        ("agrar/feeding-actuals", "create_measure"),
        ("agrar/feeding-actuals", "configure_threshold"),
    }
    actual = {(screen, action["key"]) for screen in SCREEN_DEFINITION_BUILDERS
              for action in get_screen_definition(screen).get("actions", [])
              if action.get("inputFlow")}
    assert expected <= actual
    assert all(valid_input_flow(action) for action in actions)


@pytest.mark.parametrize("screen,key", [
    ("personal/onboarding", "speichern"),
    ("personal/qualifikationen", "speichern"),
    ("personal/schulungen", "speichern"),
    ("personal/bewerbungen", "speichern"),
    ("personal/einwilligungserklaerungen", "anlegen"),
])
def test_migrated_personal_flows_have_real_commands(screen, key):
    from app.main import app

    action = next(a for a in get_screen_definition(screen)["actions"] if a["key"] == key)
    assert action.get("commandEndpoint")
    assert not action.get("inputFlow")
    assert not action.get("stubReason")
    assert any(route.path == action["commandEndpoint"] and "POST" in route.methods
               for route in app.routes)


@pytest.mark.parametrize("field,value", [("forbiddenForAgents", False),
                                         ("commandEndpoint", "/api/v1/unsafe")])
def test_unprotected_or_ambiguous_flows_fail_inventory(field, value):
    action = deepcopy(flows()[0])
    action[field] = value
    assert not valid_input_flow(action)


def test_missing_submit_endpoint_fails_inventory():
    action = deepcopy(flows()[0])
    del action["inputFlow"]["submitEndpoint"]
    assert not valid_input_flow(action)
