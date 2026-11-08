"""Identity worklists use the native compiler contract and real typed commands."""
import pytest
from app.core.screen_definitions import get_screen_definition,get_screen_list_route
from app.api.v1.endpoints.mask_screen_definition import _check_readiness


@pytest.mark.parametrize('screen_id',['admin/identity-budgets','admin/token-consumption'])
def test_identity_mask_is_native_and_passes_all_readiness_gates(screen_id):
    screen=get_screen_definition(screen_id)
    assert screen['adapter']=={'type':'native','sourceId':screen_id,'temporary':False}
    result=_check_readiness(screen)
    assert result['generatorReady'] and result['advisoryScore']==1,result
    assert get_screen_list_route(screen_id)=='/'+screen_id
    assert screen['layout']['tableProfile']=='audit'
    assert all(source['endpoint'].startswith('/api/v1/identity/') for source in screen['dataSources'])


def test_budget_mutations_require_human_confirmation_reason_and_classification():
    screen=get_screen_definition('admin/identity-budgets')
    mutations=[action for action in screen['actions'] if action.get('commandEndpoint')]
    assert {action['key'] for action in mutations}=={'root','allocate'}
    for action in mutations:
        assert action['requiresConfirmation'] and action['auditReasonRequired']
        assert action['forbiddenForAgents'] and action['humanApprovalRequired']
        assert action['commandEndpoint'].endswith('/actions/'+action['key'])
        assert {'tokens','max_children'}<= {field['key'] for field in action['inputFields']}
