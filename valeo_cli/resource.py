"""Enger, menschlicher REST-Ressourcentransport wie resource-response-adapter.ts."""
from __future__ import annotations

import re
from urllib.parse import quote

ROUTES = {
    'agrar/saatgut/sorte': {'PUT /api/v1/agrar/varieties/{entity_id}'},
    'crm/campaign-template': {f'{m} /api/v1/crm/campaigns/templates/{{entity_id}}{suffix}' for m, suffix in [('DELETE', ''), ('PUT', ''), ('POST', '/duplicate')]},
    'crm/campaign': {f'{m} /api/v1/crm/campaigns/{{entity_id}}{suffix}' for m, suffix in [('DELETE', ''), ('PUT', ''), *[('POST', '/' + k) for k in ('activate', 'pause', 'resume', 'complete', 'archive', 'recipients')]]},
    'crm/consent': {f'{m} /api/v1/crm/consents/{{entity_id}}{suffix}' for m, suffix in [('PUT', ''), ('POST', '/revoke'), ('POST', '/resend-confirmation')]},
    'crm/gdpr-request': {f'POST /api/v1/gdpr/requests/{{entity_id}}/{k}' for k in ('verify', 'reject', 'export', 'delete')},
    'crm/segment': {f'{m} /api/v1/crm/segments/{{entity_id}}{suffix}' for m, suffix in [('PUT', ''), ('DELETE', ''), *[('POST', '/' + k) for k in ('calculate', 'members', 'members/remove')]]},
}
DELETE_ROUTES = {'DELETE /api/v1/crm/campaigns/{entity_id}', 'DELETE /api/v1/crm/campaigns/templates/{entity_id}'}
VERSIONED_ROUTES = {
    ('crm/segment', value) for value in ROUTES['crm/segment']
} | {
    ('crm/gdpr-request', f'POST /api/v1/gdpr/requests/{{entity_id}}/{action}')
    for action in ('export', 'delete')
}
CONTROL_KEYS = {'expected_version', 'idempotency_key', 'audit_reason'}


def route(action):
    return f"{action.get('method', 'POST')} {action.get('commandEndpoint', '')}"


def supported(action, screen_id):
    versioned = (screen_id, route(action)) in VERSIONED_ROUTES
    flags = (action.get('requiresExpectedVersion') is True and action.get('requiresIdempotencyKey') is True
             if versioned else not any(action.get(k) for k in ('requiresIdempotencyKey', 'requiresExpectedVersion', 'auditReasonRequired')))
    return (action.get('responseAdapter') == 'resource.v1' and action.get('forbiddenForAgents') is True
            and route(action) in ROUTES.get(screen_id, set())
            and flags and not any(action.get(k) for k in ('inputFlow', 'commandBinding')))


def safe_id(value):
    return isinstance(value, str) and bool(value.strip()) and value not in {'.', '..'} and len(value) <= 128 and not re.search(r'[\s/\\?#]', value)


def prepare(action, screen_id, entity_id, payload, mode, is_agent, *, version=None, audit_reason=None, idempotency_key=None):
    if not supported(action, screen_id) or is_agent or mode != 'execute' or not safe_id(entity_id):
        raise ValueError('REST-Ressourcenaktion ist fuer diesen Aufruf gesperrt.')
    declared = {field['key'] for field in action.get('inputFields', []) if isinstance(field, dict) and isinstance(field.get('key'), str)}
    # Steuerfelder duerfen niemals durch untrusted --daten als Fachfelder durchrutschen.
    if any(key.startswith('_') or key in CONTROL_KEYS for key in payload):
        raise ValueError('Interne Steuerfelder sind fuer Ressourcenaktionen nicht erlaubt.')
    body = {key: value for key, value in payload.items() if key in declared}
    if (screen_id, route(action)) in VERSIONED_ROUTES:
        if type(version) is not int or version < 1:
            raise ValueError('Diese Aktion braucht die gelesene Version (--version).')
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 128:
            raise ValueError('Ein gueltiger Wiederholungsschluessel ist erforderlich.')
        if action.get('auditReasonRequired') and not (audit_reason or '').strip():
            raise ValueError('Diese Aktion verlangt eine Begruendung (--grund).')
        body.update(expected_version=version, _idempotencyKey=idempotency_key)
        if audit_reason:
            body['_auditReason'] = audit_reason
    elif version is not None or audit_reason or idempotency_key:
        raise ValueError('Dieser Ressourcenvertrag akzeptiert keine Steueroptionen.')
    return action.get('method', 'POST'), action['commandEndpoint'].replace('{entity_id}', quote(entity_id, safe='')), body


def result(action, entity_id, body, status):
    route_key = route(action)
    if route_key in DELETE_ROUTES:
        if status == 204 and body is None:
            return {'success': True, 'resourceId': entity_id, 'affectedIds': [entity_id]}
        raise ValueError('Die Loeschung wurde nicht eindeutig bestaetigt.')
    item = body if isinstance(body, dict) else {}
    identifier = item.get('id')
    creates_child = action.get('method') == 'POST' and (action['commandEndpoint'].endswith('/duplicate') or action['commandEndpoint'] == '/api/v1/crm/campaigns/{entity_id}/recipients')
    if (not safe_id(identifier) or (identifier == entity_id if creates_child else identifier != entity_id)
            or action['commandEndpoint'] == '/api/v1/crm/campaigns/{entity_id}/recipients' and item.get('campaign_id') != entity_id):
        raise ValueError('Die Serverantwort bestaetigt die betroffene Ressource nicht.')
    return {'success': True, 'resourceId': identifier, 'affectedIds': [entity_id, identifier] if creates_child else [identifier]}
