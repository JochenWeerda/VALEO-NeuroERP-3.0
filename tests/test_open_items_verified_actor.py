"""Open-item audit helper cannot derive actors from caller-controlled headers."""
import base64
import json
import time

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.v1.endpoints.open_items import _get_user_id_from_request
from app.core.identity_context import reset_current_identity, set_current_identity


@pytest.mark.parametrize('headers', [
    [],
    [(b'x-user-id', b'forged-admin')],
    [(b'authorization', b'Bearer header.' + base64.urlsafe_b64encode(
        json.dumps({'sub': 'forged-admin'}).encode()).rstrip(b'=') + b'.unsigned')],
])
def test_caller_headers_do_not_replace_verified_subject(monkeypatch, headers):
    # Session/JWT verification has separate RSA contracts. This unit contract
    # isolates the helper's selection of the already verified principal.
    monkeypatch.setattr('app.core.identity_session.validate', lambda *args, **kwargs: None)
    monkeypatch.setattr('app.core.security._resolve_issuer', lambda: 'https://identity.test/realm')
    monkeypatch.setattr('app.core.config.settings.OIDC_CLIENT_ID', 'audit-contract-api')
    token = set_current_identity({
        'iss': 'https://identity.test/realm', 'sub': 'verified-bookkeeper',
        'aud': 'audit-contract-api',
        'tenant_id': '11111111-1111-1111-1111-111111111111',
        'exp': time.time() + 60,
    }, 'verified-token')
    try:
        request = Request({'type': 'http', 'headers': headers})
        assert _get_user_id_from_request(request) == 'verified-bookkeeper'
        assert _get_user_id_from_request(None) == 'verified-bookkeeper'
    finally:
        reset_current_identity(token)


@pytest.mark.parametrize('http_request', [None, Request({
    'type': 'http', 'headers': [(b'x-user-id', b'forged-admin')],
})])
def test_missing_verified_identity_fails_closed(http_request):
    with pytest.raises(HTTPException) as error:
        _get_user_id_from_request(http_request)
    assert error.value.status_code == 401
