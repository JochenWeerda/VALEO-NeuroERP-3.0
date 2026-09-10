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
    assert len(actions) == 13
    assert all(valid_input_flow(action) for action in actions)


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
