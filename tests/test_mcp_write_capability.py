"""Generic MCP writes require exact explicit action-level release."""
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from app.core import identity_context
from app.services import mcp_mask_actions as mm
from app.services.mcp_tool_registry_service import mcp_tool_registry_service

SCREEN = 'test/screen'
ENDPOINT = '/api/v1/test/{entity_id}/actions/delete'
CAPABILITY = {'domain_command': 'test.delete.v1', 'endpoint': ENDPOINT, 'screen_id': SCREEN,
              'action': 'delete', 'command_version': 1, 'agent_write_enabled': True,
              'agent_roles': ['PERSONAL_BEARBEITEN']}
ACTION = {'key': 'delete', 'commandEndpoint': ENDPOINT, 'domainCommand': 'test.delete.v1', 'method': 'POST'}


def principal(roles=('PERSONAL_BEARBEITEN',), scopes=('masks:write',)):
    return SimpleNamespace(roles=frozenset(roles), scopes=frozenset(scopes), claims={'identity_type': 'human'})


def execute(monkeypatch, entries, action=ACTION, user=None):
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', lambda _: {'write_capabilities': entries})
    monkeypatch.setattr(mm, '_definition', lambda _screen, _tenant: {'id': SCREEN, 'actions': [action]})
    monkeypatch.setattr(identity_context, 'current_identity', lambda: user or principal())
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={'success': True})
    req = SimpleNamespace(parameters={'screen_id': SCREEN, 'action': 'delete', 'entity_id': 'a/1'},
                          mode='execute', idempotency_key='key')
    def run():
        return mm.execute(req, 't1', 'Bearer token', transport=httpx.MockTransport(handler))
    return run, calls


def test_approved_exact_command_forwarded_with_caller_token(monkeypatch):
    run, calls = execute(monkeypatch, [CAPABILITY])
    assert run()['success']
    [request] = calls
    assert request.method == 'POST' and request.url.raw_path == b'/api/v1/test/a%2F1/actions/delete'
    assert request.headers['authorization'] == 'Bearer token' and 'x-tenant-id' not in request.headers


@pytest.mark.parametrize('entries', [[], [{**CAPABILITY, 'agent_write_enabled': False}],
    [{**CAPABILITY, 'command_version': 2}], [CAPABILITY, CAPABILITY],
    [{**CAPABILITY, 'screen_id': 'other'}], [{**CAPABILITY, 'action': 'other'}],
    [{**CAPABILITY, 'endpoint': '/api/v1/other'}], [{**CAPABILITY, 'domain_command': 'wrong'}],
    [CAPABILITY, {**CAPABILITY, 'domain_command': 'other', 'endpoint': '/api/v1/other'}],
    'invalid', [None]])
def test_unknown_disabled_malformed_or_ambiguous_write_blocked_before_forward(monkeypatch, entries):
    run, calls = execute(monkeypatch, entries)
    with pytest.raises(HTTPException) as error:
        run()
    assert error.value.status_code == 403 and not calls


@pytest.mark.parametrize('user', [principal(roles=['OTHER']), principal(scopes=[]), principal(roles=[], scopes=['masks:write'])])
def test_even_human_bearer_needs_capability_role_and_scope_before_forward(monkeypatch, user):
    run, calls = execute(monkeypatch, [CAPABILITY], user=user)
    with pytest.raises(HTTPException) as error:
        run()
    assert error.value.status_code == 403 and not calls


def test_read_and_write_contract_cannot_be_combined():
    conflicting = {**ACTION, 'localEffect': 'view', 'readView': {'endpoint': '/api/v1/test'}}
    assert mm.agent_block(conflicting, SCREEN) == 'leseansicht_ungueltig'
