from fastapi.testclient import TestClient

from app.core.config import settings
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
