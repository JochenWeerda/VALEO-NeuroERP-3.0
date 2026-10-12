"""Production app rejects legacy credentials and accepts actual provider JWTs."""
from fastapi.testclient import TestClient
from test_system_tenant_binding import keys, probe
from main import app


def test_api_requires_bearer_token():
    response = TestClient(app).get('/api/v1/status')
    assert response.status_code == 401


def test_api_rejects_unscoped_dev_token(probe):
    response = TestClient(app).get('/api/v1/status', headers={'Authorization': 'Bearer opaque-own-dev-token'})
    assert response.status_code == 401


def test_api_accepts_valid_oidc_token(probe):
    response = TestClient(app).get('/api/v1/status', headers=probe.headers())
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_api_rejects_invalid_signature(probe):
    response = TestClient(app).get('/api/v1/status', headers={'Authorization': 'Bearer ' + probe.token(key=1)})
    assert response.status_code == 401
