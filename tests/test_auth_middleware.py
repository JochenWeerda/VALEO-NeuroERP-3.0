import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core import security
from main import app


client = TestClient(app)


def test_api_requires_bearer_token() -> None:
    response = client.get('/api/v1/status')
    assert response.status_code == 401
    assert response.json()['detail'] == 'Missing bearer token'


def test_api_accepts_valid_dev_token() -> None:
    token = settings.API_DEV_TOKEN or 'dev-token'
    response = client.get('/api/v1/status', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_api_accepts_valid_oidc_token(monkeypatch: pytest.MonkeyPatch) -> None:
    original = settings.API_DEV_TOKEN
    settings.API_DEV_TOKEN = None

    monkeypatch.setattr(security, '_validate_jwt', lambda token: {'sub': 'user-123'})

    try:
        response = client.get('/api/v1/status', headers={'Authorization': 'Bearer jwt-token'})
        assert response.status_code == 200
        assert response.json()['status'] == 'ok'
    finally:
        settings.API_DEV_TOKEN = original
        monkeypatch.undo()


def test_api_rejects_invalid_oidc_token(monkeypatch: pytest.MonkeyPatch) -> None:
    original = settings.API_DEV_TOKEN
    settings.API_DEV_TOKEN = None

    def _raise(_: str) -> dict[str, str]:
        raise HTTPException(status_code=401, detail='Invalid bearer token')

    monkeypatch.setattr(security, '_validate_jwt', _raise)

    try:
        response = client.get('/api/v1/status', headers={'Authorization': 'Bearer bad-token'})
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid bearer token'
    finally:
        settings.API_DEV_TOKEN = original
        monkeypatch.undo()
