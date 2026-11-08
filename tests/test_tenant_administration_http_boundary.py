"""Tenant administration requires the common verified boundary before DB access."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.endpoints.tenants import router
from app.core.database import get_db


@pytest.mark.parametrize('method,path,body', [
    ('GET', '/', None), ('GET', '/target', None),
    ('POST', '/', {}), ('PUT', '/target', {}),
    ('POST', '/target/block', {'reason': 'synthetic reason'}),
    ('DELETE', '/target', {'reason': 'synthetic reason'}),
])
def test_no_unverified_administrative_request_reaches_database(method, path, body):
    app = FastAPI()
    app.include_router(router, prefix='/tenants')
    accesses = []

    def database():
        accesses.append(True)
        raise AssertionError('Unverified caller reached database')

    app.dependency_overrides[get_db] = database
    with TestClient(app) as client:
        response = client.request(method, '/tenants' + path, json=body)
    assert response.status_code in {401, 403}, response.text
    assert not accesses
