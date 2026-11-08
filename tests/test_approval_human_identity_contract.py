"""The same non-human classification protects AP and central approval decisions."""
import pytest
from app.services.freigabe_engine import technisches_konto


@pytest.mark.parametrize('user', [None, {}, {'sub':'human','name':'Synthetic person'},
    {'sub':'human','raw':{'preferred_username':'synthetic-person','actor_type':'human'}}])
def test_plain_person_is_not_reclassified_by_role_or_missing_optional_profile(user):
    assert technisches_konto(user) is (user is None)


@pytest.mark.parametrize('user', [
    {'raw':{'preferred_username':'service-account-synthetic'}},
    {'raw':{'client_id':'synthetic-service'}},
    {'agent_id':'synthetic-agent'}, {'raw':{'agent_id':'synthetic-agent'}},
    {'raw':{'act':{'sub':'synthetic-delegate'}}}, {'raw':{'act':{}}},
    {'raw':{'actor_type':'ai_agent'}}, {'raw':{'actor_type':'SYSTEM'}}, {'raw':'invalid'},
])
def test_service_delegation_and_agent_markers_cannot_supply_independent_human_approval(user):
    assert technisches_konto(user) is True
