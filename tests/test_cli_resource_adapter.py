import io
import json

import httpx
import pytest

from app.core.screen_definitions_sorte import build_agrar_sorte_stamm
from app.core.screen_definitions_stamm import build_crm_segment_stamm, build_crm_gdpr_request_stamm
from app.api.v1.endpoints.crm_segments import MemberInput, Mutation, SegmentUpdate
from app.services.gdpr_request_processor import ProcessPayload
from valeo_cli import cli, resource, support
from test_valeo_cli import HUMAN, AGENT


def test_resource_dry_run_never_sends_put(monkeypatch):
    monkeypatch.setenv('VALEO_ACCESS_TOKEN', HUMAN)
    calls = []
    definition = build_agrar_sorte_stamm()
    action = next(a for a in definition['actions'] if a.get('responseAdapter') == 'resource.v1')

    def handle(request):
        if request.url.path.endswith('/screen-definition'):
            return httpx.Response(200, json=definition)
        calls.append(request)
        return httpx.Response(200, json={'id': 's1'})

    with httpx.Client(transport=httpx.MockTransport(handle)) as http:
        result = cli.main(['ausfuehren', 'agrar/saatgut/sorte', action['key'], '--id', 's1',
                           '--modus', 'dryRun'], http=http, out=lambda _: None, stdin=io.StringIO())
    assert result != 0
    assert calls == []


def invoke(monkeypatch, definition, argv, response, token=HUMAN, data=''):
    monkeypatch.setenv('VALEO_ACCESS_TOKEN', token)
    calls, lines = [], []
    def handle(request):
        if request.url.path.endswith('/screen-definition'):
            return httpx.Response(200, json=definition)
        calls.append(request)
        return response
    with httpx.Client(transport=httpx.MockTransport(handle)) as http:
        code = cli.main(argv, http=http, out=lines.append, stdin=io.StringIO(data), ask=lambda _: 'ja')
    return code, calls, lines


def test_sorte_execute_sends_only_declared_raw_fields_once(monkeypatch):
    definition = build_agrar_sorte_stamm()
    action = next(a for a in definition['actions'] if a.get('responseAdapter') == 'resource.v1')
    argv = ['ausfuehren', definition['id'], action['key'], '--id', 's1', '--feld', 'name=Roggen',
            '--feld', 'variety_number=42', '--feld', 'tenant_id=foreign', '--json']
    code, calls, lines = invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 's1'}))
    assert code == 0 and len(calls) == 1
    assert calls[0].method == 'PUT' and calls[0].url.path == '/api/v1/agrar/varieties/s1'
    assert json.loads(calls[0].content) == {'name': 'Roggen', 'variety_number': '42'}
    assert json.loads(lines[-1])['resourceId'] == 's1'
    assert invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 's1'}), AGENT)[1] == []


@pytest.mark.parametrize('identifier', ['', '.', '..', 'a/b', 'a b', 'x?y', 'x#y', 'a\\b', 'x' * 129])
def test_unsafe_resource_ids_are_blocked(identifier):
    action = next(a for a in build_agrar_sorte_stamm()['actions'] if a.get('responseAdapter') == 'resource.v1')
    with pytest.raises(ValueError):
        resource.prepare(action, 'agrar/saatgut/sorte', identifier, {}, 'execute', False)


def test_allowlist_control_fields_and_nonresource_preview():
    action = next(a for a in build_agrar_sorte_stamm()['actions'] if a.get('responseAdapter') == 'resource.v1')
    assert support.support(action, screen_id='agrar/saatgut/sorte').supported
    assert not support.support(action).supported
    assert not support.support(action, screen_id='crm/campaign').supported
    assert not support.support({**action, 'method': 'POST'}, screen_id='agrar/saatgut/sorte').supported
    assert not support.support({**action, 'responseAdapter': 'unknown'}, screen_id='agrar/saatgut/sorte').supported
    with pytest.raises(ValueError):
        resource.prepare(action, 'agrar/saatgut/sorte', 's1', {'_mode': 'dryRun'}, 'execute', False)
    for mode in ('dryRun', 'execute'):
        with pytest.raises(ValueError, match='Ressourcenadapter'):
            support.build_request(action, screen_id='agrar/saatgut/sorte', entity_id='s1', payload={},
                                  mode=mode, audit_reason=None, idempotency_key=None)
    generic = {'key': 'x', 'commandEndpoint': '/api/v1/studio/entities/studio_test/actions/create'}
    assert support.build_request(generic, screen_id='s', entity_id=None, payload={}, mode='dryRun',
                                 audit_reason=None, idempotency_key=None)[2] == {'_mode': 'dryRun'}


def test_response_identity_delete_and_child_relationship():
    edit = next(a for a in build_agrar_sorte_stamm()['actions'] if a.get('responseAdapter') == 'resource.v1')
    assert resource.result(edit, 's1', {'id': 's1'}, 200)['affectedIds'] == ['s1']
    for bad in (None, {}, {'id': 'other'}, {'id': '..'}):
        with pytest.raises(ValueError):
            resource.result(edit, 's1', bad, 200)
    delete = {'method': 'DELETE', 'commandEndpoint': '/api/v1/crm/campaigns/{entity_id}'}
    assert resource.result(delete, 'c1', None, 204)['resourceId'] == 'c1'
    with pytest.raises(ValueError):
        resource.result(delete, 'c1', {}, 200)
    child = {'method': 'POST', 'commandEndpoint': '/api/v1/crm/campaigns/{entity_id}/recipients'}
    assert resource.result(child, 'c1', {'id': 'r1', 'campaign_id': 'c1'}, 200)['affectedIds'] == ['c1', 'r1']
    for bad in ({'id': 'c1', 'campaign_id': 'c1'}, {'id': 'r1', 'campaign_id': 'other'}):
        with pytest.raises(ValueError):
            resource.result(child, 'c1', bad, 200)


def test_duplicate_does_not_retry_and_rejects_uncertain_or_wrong_result(monkeypatch):
    action = {'key': 'duplicate', 'method': 'POST', 'commandEndpoint': '/api/v1/crm/campaigns/templates/{entity_id}/duplicate',
              'responseAdapter': 'resource.v1', 'forbiddenForAgents': True}
    definition = {'id': 'crm/campaign-template', 'actions': [action]}
    argv = ['ausfuehren', definition['id'], 'duplicate', '--id', 't1']
    code, calls, _ = invoke(monkeypatch, definition, argv, httpx.Response(500, json={'detail': 'uncertain'}))
    assert code == 4 and len(calls) == 1
    code, calls, _ = invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 't1'}))
    assert code != 0 and len(calls) == 1
    code, calls, _ = invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 't2'}))
    assert code == 0 and len(calls) == 1 and json.loads(calls[0].content) == {}
    code, calls, _ = invoke(monkeypatch, definition, argv + ['--idempotenz', 'x'], httpx.Response(200, json={'id': 't2'}))
    assert code != 0 and not calls


def test_delete_requires_exact_no_content_confirmation(monkeypatch):
    action = {'key': 'delete', 'method': 'DELETE', 'commandEndpoint': '/api/v1/crm/campaigns/{entity_id}',
              'responseAdapter': 'resource.v1', 'forbiddenForAgents': True}
    definition = {'id': 'crm/campaign', 'actions': [action]}
    argv = ['ausfuehren', definition['id'], 'delete', '--id', 'c1']
    assert invoke(monkeypatch, definition, argv, httpx.Response(204))[0] == 0
    assert invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 'c1'}))[0] != 0


@pytest.mark.parametrize('mode', ['dryRun', 'validate', 'propose'])
def test_all_resource_previews_are_blocked_before_send(monkeypatch, mode):
    definition = build_agrar_sorte_stamm()
    action = next(a for a in definition['actions'] if a.get('responseAdapter') == 'resource.v1')
    code, calls, _ = invoke(monkeypatch, definition, ['ausfuehren', definition['id'], action['key'], '--id', 's1', '--modus', mode], httpx.Response(200, json={'id': 's1'}))
    assert code != 0 and not calls


@pytest.mark.parametrize('key,payload,model', [
    ('edit', {'name': 'Test', 'segment_type': 'static'}, SegmentUpdate),
    ('rules', {'criteria_rules': []}, SegmentUpdate),
    ('calculate', {}, Mutation), ('delete', {}, Mutation),
    ('add_member', {'partner_id': 'p1'}, MemberInput),
    ('remove_member', {'partner_id': 'p1'}, MemberInput),
])
def test_versioned_segment_cli_matches_server_model(monkeypatch, key, payload, model):
    definition = build_crm_segment_stamm()
    argv = ['ausfuehren', definition['id'], key, '--id', 's1', '--version', '3', '--idempotenz', 'k1',
            '--daten', '-', '--ja', '--json']
    if key in {'rules', 'delete'}:
        argv += ['--grund', 'Nachweis']
    code, calls, _ = invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 's1'}), data=json.dumps(payload))
    assert code == 0 and len(calls) == 1
    body = json.loads(calls[0].content)
    parsed = model.model_validate(body)
    assert parsed.idempotency_key == 'k1' and parsed.expected_version == 3
    assert parsed.audit_reason == ('Nachweis' if key in {'rules', 'delete'} else None)
    assert invoke(monkeypatch, definition, [x for x in argv if x not in ('--version', '3')],
                  httpx.Response(200, json={'id': 's1'}), data=json.dumps(payload))[1] == []
    if key in {'rules', 'delete'}:
        without_reason = argv[:-2]
        assert invoke(monkeypatch, definition, without_reason, httpx.Response(200, json={'id': 's1'}), data=json.dumps(payload))[1] == []


@pytest.mark.parametrize('key', ['export', 'delete'])
def test_gdpr_cli_body_matches_process_payload(monkeypatch, key):
    definition = build_crm_gdpr_request_stamm()
    payload = {'subject_type': 'CUSTOMER', 'data_scope': 'LOCAL_CRM_SUBJECT', 'reason': 'Anfrage'}
    argv = ['ausfuehren', definition['id'], key, '--id', 'g1', '--version', '2', '--idempotenz', 'g-key',
            '--daten', '-', '--ja']
    code, calls, _ = invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 'g1'}), data=json.dumps(payload))
    assert code == 0 and len(calls) == 1
    parsed = ProcessPayload.model_validate(json.loads(calls[0].content))
    assert parsed.expected_version == 2 and parsed.idempotency_key == 'g-key' and parsed.reason == 'Anfrage'
    assert invoke(monkeypatch, definition, [x for x in argv if x not in ('--version', '2')],
                  httpx.Response(200, json={'id': 'g1'}), data=json.dumps(payload))[1] == []
    assert invoke(monkeypatch, definition, argv, httpx.Response(200, json={'id': 'g1'}),
                  data=json.dumps({k: v for k, v in payload.items() if k != 'reason'}))[1] == []


def test_versioned_recovery_key_and_untrusted_controls(monkeypatch):
    definition = build_crm_segment_stamm()
    argv = ['ausfuehren', definition['id'], 'calculate', '--id', 's1', '--version', '1', '--idempotenz', 'wieder-1']
    code, calls, lines = invoke(monkeypatch, definition, argv, httpx.Response(500, json={'detail': 'uncertain'}))
    assert code == 4 and len(calls) == 1 and any('--idempotenz wieder-1' in line for line in lines)
    generated_argv = ['ausfuehren', definition['id'], 'calculate', '--id', 's1', '--version', '1']
    code, calls, lines = invoke(monkeypatch, definition, generated_argv, httpx.Response(500, json={'detail': 'uncertain'}))
    sent_key = json.loads(calls[0].content)['_idempotencyKey']
    assert code == 4 and any(f'--idempotenz {sent_key}' in line for line in lines)
    assert invoke(monkeypatch, definition, ['ausfuehren', definition['id'], 'calculate', '--id', 's1', '--version', '0'],
                  httpx.Response(200, json={'id': 's1'}))[1] == []
    for field in ('expected_version', 'idempotency_key', 'audit_reason', '_idempotencyKey'):
        code, calls, _ = invoke(monkeypatch, definition, argv + ['--daten', '-'], httpx.Response(200, json={'id': 's1'}),
                                data=json.dumps({field: 'foreign'}))
        assert code != 0 and not calls
