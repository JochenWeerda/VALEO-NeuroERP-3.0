import json
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services import studio_validation
from app.services.mcp_write_capability import capability_enabled, authorize_agent
from app.services.studio_entity_compiler import compile_entity
from test_studio_entity_generation import specification


def test_studio_capability_requires_deployment_switch_and_roles(tmp_path, monkeypatch):
    spec = specification()
    bundle = compile_entity(spec)
    definition = json.loads(bundle['files']['screen.json'])
    action = definition['actions'][0]
    assert action['disabled'] and action['forbiddenForAgents'] and not bundle['enabled']
    args = (action['domainCommand'], action['commandEndpoint'], definition['id'], action['key'])
    config = tmp_path / 'deployment.json'
    monkeypatch.setattr(studio_validation, '_CONFIG_PATH', config)
    def deploy(writes, roles):
        config.write_text(json.dumps({'generated_entities': [{'spec': spec.model_dump(),
            'writes_enabled': writes, 'agent_roles': roles}]}), encoding='utf-8')
    deploy(False, ['CRM_BEARBEITEN'])
    assert not capability_enabled(*args)
    deploy(True, [])
    assert not capability_enabled(*args)
    deploy(True, ['CRM_BEARBEITEN'])
    assert capability_enabled(*args)
    assert not capability_enabled(args[0], args[1], 'tenant/other', args[3])
    assert not capability_enabled('unknown.write.v1', *args[1:])
    authorize_agent(SimpleNamespace(scopes={'masks:write'}, roles={'CRM_BEARBEITEN'}), *args)
    for scopes, roles in [ (set(), {'CRM_BEARBEITEN'}), ({'masks:write'}, {'OTHER'}) ]:
        with pytest.raises(HTTPException):
            authorize_agent(SimpleNamespace(scopes=scopes, roles=roles), *args)
    deploy(True, ['OTHER'])
    assert not capability_enabled(*args)
