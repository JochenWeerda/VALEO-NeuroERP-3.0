from types import SimpleNamespace
import pytest
from app.core.akteur import gepruefte_email


def request(claims):
    return SimpleNamespace(state=SimpleNamespace(token_claims=claims), headers={'X-User-Email': 'owner@example.invalid'})


@pytest.mark.parametrize('verified', [None, False, 0, 1, 'true', 'false', {}, []])
def test_signed_email_without_verified_ownership_is_not_an_access_identity(verified):
    assert gepruefte_email(request({'sub': 'subject-a', 'email': 'owner@example.invalid', 'email_verified': verified})) is None


def test_verified_email_is_read_from_claims_and_trimmed():
    assert gepruefte_email(request({'sub': 'subject-a', 'email': ' reader@example.invalid ', 'email_verified': True})) == 'reader@example.invalid'


@pytest.mark.parametrize('claims', [None, {}, {'email_verified': True}, {'email_verified': True, 'email': '   '}])
def test_missing_claims_do_not_fall_back_to_client_headers(claims):
    assert gepruefte_email(request(claims)) is None
