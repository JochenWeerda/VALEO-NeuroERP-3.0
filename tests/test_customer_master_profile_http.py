"""HTTP boundary keeps the existing role policy and verified actor contract."""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.api.v1.endpoints import customer_master_profile as api
from app.auth.deps import get_current_user


@pytest.fixture
def harness(monkeypatch):
    app = FastAPI()
    app.include_router(api.router)
    state = {'roles': ['CRM_BEARBEITEN'], 'sub': 'synthetic-verified-actor'}

    def user(request: Request):
        request.state.token_claims = dict(state)
        return dict(state)

    app.dependency_overrides[get_current_user] = user
    app.dependency_overrides[api.get_tenant_id] = lambda: 'synthetic-tenant'
    app.dependency_overrides[api.get_db] = lambda: object()
    calls = []

    async def execute(db, **kwargs):
        calls.append(kwargs)
        return api.MaskActionResult(actionKey=kwargs['action_key'], mode='execute', success=True)

    monkeypatch.setattr(api, 'run_delegated_mask_action', execute)
    return TestClient(app), state, calls


PATH = '/crm/customers/synthetic-customer/master-profile/actions/bearbeiten'
BODY = {'partner_iban': 'DE123', 'expected_version': 123,
        '_idempotencyKey': 'synthetic-key', '_auditReason': 'Synthetic regression'}


@pytest.mark.parametrize('roles', [[], ['CRM_LESEN'], ['FINANCE_BEARBEITEN'], ['portal_customer']])
def test_write_denies_roles_outside_existing_crm_policy(harness, roles):
    client, state, calls = harness
    state['roles'] = roles
    assert client.post(PATH, json=BODY).status_code == 403
    assert not calls


def test_actor_is_verified_and_fingerprint_binds_request(harness):
    client, state, calls = harness
    assert client.post(PATH, json=BODY).status_code == 200
    assert calls[0]['performed_by'] == state['sub']
    assert calls[0]['action_key'] == 'stammdaten_pflegen'
    fingerprint = calls[0]['request_fingerprint']
    assert client.post(PATH, json={**BODY, 'partner_iban': 'DE456'}).status_code == 200
    assert calls[1]['request_fingerprint'] != fingerprint
    assert client.post(PATH, json={**BODY, 'performed_by': 'spoofed'}).status_code == 422
    assert len(calls) == 2


@pytest.mark.parametrize('missing', ['_idempotencyKey', '_auditReason', 'expected_version'])
def test_required_execution_contract_rejected_before_mutation(harness, missing):
    client, _, calls = harness
    assert client.post(PATH, json={k: v for k, v in BODY.items() if k != missing}).status_code == 422
    assert not calls


def test_preview_precedes_audit_reason_dialog_and_does_not_require_write_key(harness):
    client, _, calls = harness
    preview = {'partner_iban': 'DE123', 'expected_version': 123, '_mode': 'dryRun'}
    assert client.post(PATH, json=preview).status_code == 200
    assert calls[0]['body']['_mode'] == 'dryRun'


def test_openapi_declares_same_partial_fields_as_domain_validator(harness):
    client, _, _ = harness
    spec = client.get('/openapi.json').json()
    body = spec['paths'][PATH.replace('synthetic-customer', '{customer_id}')]['post']['requestBody']['content']['application/json']['schema']
    assert body['additionalProperties'] is False
    assert set(body['properties']) == {'partner_' + key for key in api.field_specs()} | {
        'expected_version', '_mode', '_auditReason', '_idempotencyKey'}
    assert body['required'] == ['expected_version']
