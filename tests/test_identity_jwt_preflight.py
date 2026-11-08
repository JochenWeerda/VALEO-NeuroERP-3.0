"""Malformed credentials must not trigger external key discovery or database work."""
import base64
import json
from unittest.mock import Mock
import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.auth.deps import get_current_user
from app.core import security


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """This fresh HTTP app tests production auth and needs no compatibility app."""
    yield


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """No database or tenant fixture is needed by this isolated auth contract."""
    yield


def compact_header(header):
    encoded=base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    return encoded+'.e30.c2ln'


@pytest.fixture
def provider_outage(monkeypatch):
    network=Mock(side_effect=HTTPException(503,'Identity provider unavailable'))
    monkeypatch.setattr(security,'_resolve_jwks_url',lambda:'https://identity.invalid/keys')
    monkeypatch.setattr(security,'_get_jwks',network)
    app=FastAPI()
    @app.get('/protected')
    def protected(user=Depends(get_current_user)):
        raise AssertionError('Unverified identity reached protected handler')
    return TestClient(app),network


@pytest.mark.parametrize('token',[
    'dev-token', 'not.a.jwt',
    compact_header({'alg':'none','kid':'synthetic'}),
    compact_header({'alg':'HS256','kid':'synthetic'}),
    compact_header({'alg':['RS256'],'kid':'synthetic'}),
    compact_header({'alg':'RS256','kid':['synthetic']}),
])
def test_invalid_bearer_is_rejected_without_provider_access(provider_outage,token):
    client,network=provider_outage
    response=client.get('/protected',headers={'Authorization':'Bearer '+token})
    assert response.status_code==401
    assert response.json()=={'detail':'Invalid bearer token'}
    network.assert_not_called()


def test_well_formed_supported_header_still_requires_provider(provider_outage):
    client,network=provider_outage
    response=client.get('/protected',headers={'Authorization':'Bearer '+compact_header({'alg':'RS256','kid':'synthetic'})})
    assert response.status_code==503
    network.assert_called_once_with('https://identity.invalid/keys')
