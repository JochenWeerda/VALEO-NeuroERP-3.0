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
    [{**CAPABILITY, 'command_version': 2}], [{**CAPABILITY, 'domain_command': 'test.delete.v2'}], [CAPABILITY, CAPABILITY],
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


def test_command_name_version_must_match_registry_version(monkeypatch):
    from app.services.mcp_write_capability import capability_enabled
    altered = {**CAPABILITY, 'domain_command': 'test.delete.v2'}
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', lambda _: {'write_capabilities': [altered]})
    assert not capability_enabled('test.delete.v2', ENDPOINT, SCREEN, 'delete')


def test_explicit_screen_alias_may_share_command_and_endpoint(monkeypatch):
    alias = {**CAPABILITY, 'screen_id': 'test/alias'}
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', lambda _: {'write_capabilities': [CAPABILITY, alias]})
    from app.services.mcp_write_capability import capability_enabled
    assert capability_enabled('test.delete.v1', ENDPOINT, SCREEN, 'delete')
    assert capability_enabled('test.delete.v1', ENDPOINT, 'test/alias', 'delete')


@pytest.mark.parametrize('confirmation', [None, False, 'true'])
def test_confirmation_required_before_write_forward(monkeypatch, confirmation):
    action = {**ACTION, 'requiresConfirmation': True}
    run, calls = execute(monkeypatch, [CAPABILITY], action=action)
    # Recreate the call so its parameters include the candidate confirmation.
    original = mm.execute
    def call_with_confirmation(req, tenant, auth, *, transport):
        req.parameters['confirm'] = confirmation
        return original(req, tenant, auth, transport=transport)
    monkeypatch.setattr(mm, 'execute', call_with_confirmation)
    with pytest.raises(HTTPException) as error:
        run()
    assert error.value.status_code == 422 and not calls


def test_invalid_endpoint_type_and_unreadable_registry_fail_closed(monkeypatch):
    from app.services.mcp_write_capability import capability_enabled
    assert mm.agent_block({**ACTION, 'commandEndpoint': ['not', 'a', 'path']}, SCREEN) == 'ungueltiger_endpunkt'
    def broken(_):
        raise OSError('synthetic unavailable')
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', broken)
    assert not capability_enabled('test.delete.v1', ENDPOINT, SCREEN, 'delete')


# --- Entwicklungsphase (Nutzerentscheidung 08.11.2026: alle MCP-/CLI-Schreibzugriffe frei) -----------------


def test_entwicklungsphase_gibt_jeden_deklarierten_kommandoweg_frei(monkeypatch):
    run, calls = execute(monkeypatch, [])
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool',
                        lambda _: {'agent_write_phase': 'entwicklung', 'write_capabilities': []})
    assert run()['success'] and len(calls) == 1
    assert mm.agent_block({**ACTION, 'domainCommand': None}, SCREEN) is None


def test_entwicklungsphase_laesst_fachregeln_der_maske_stehen(monkeypatch):
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', lambda _: {'agent_write_phase': 'entwicklung'})
    assert mm.agent_block({**ACTION, 'forbiddenForAgents': True}, SCREEN) == 'fuer_agenten_gesperrt'
    assert mm.agent_block({**ACTION, 'humanApprovalRequired': True}, SCREEN) == 'menschliche_genehmigung'
    assert mm.agent_block({**ACTION, 'commandBinding': {'adapter': 'docflow.v1'}}, SCREEN) == 'adapter_nur_mensch'


def test_entwicklungsphase_braucht_weiter_masks_write(monkeypatch):
    from app.services.mcp_write_capability import authorize_agent
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', lambda _: {'agent_write_phase': 'entwicklung'})
    authorize_agent(principal(roles=[]), '', ENDPOINT, SCREEN, 'delete')
    with pytest.raises(HTTPException) as error:
        authorize_agent(principal(scopes=[]), '', ENDPOINT, SCREEN, 'delete')
    assert error.value.status_code == 403


@pytest.mark.parametrize('phase', [None, 'Entwicklung', 'produktiv', True])
def test_ohne_genau_entwicklung_bleibt_es_geschlossen(monkeypatch, phase):
    from app.services.mcp_write_capability import capability_enabled
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', lambda _: {'agent_write_phase': phase})
    assert not capability_enabled('test.delete.v1', ENDPOINT, SCREEN, 'delete')


def test_registry_schaltet_die_entwicklungsphase_sichtbar():
    from app.services.mcp_write_capability import development_release
    assert development_release(), 'config/mcp_erp_tools.yaml: agent_write_phase: entwicklung (vor Go-Live entfernen)'
