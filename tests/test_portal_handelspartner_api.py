"""HTTP adapter contract; dependency overrides do not prove JWT cryptography."""
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.api.v1.endpoints import portal_handelspartner as endpoint
from app.auth.deps import get_current_user


def test_uses_verified_subject_not_query_selectors(monkeypatch):
    app = FastAPI()
    app.include_router(endpoint.router)
    user = {"sub": "verified-subject", "raw": {"sub": "verified-subject", "tenant_id": "a"}}
    app.dependency_overrides[get_current_user] = lambda: user
    seen = []
    def own(actual):
        seen.append(actual)
        return [{"id": "b", "name": "Own partner", "customer_count": 1, "active": False}]
    monkeypatch.setattr(endpoint, "eigene_handelspartner", own)
    with TestClient(app) as client:
        response = client.get('/portal/handelspartner?subject=other&customer_id=other')
    assert response.status_code == 200
    assert seen == [user]
    assert response.json() == {"items": [{"id": "b", "name": "Own partner", "customer_count": 1, "active": False}],
                               "stage": "discovery_only", "context_switch_available": False}


def test_auth_failure_prevents_directory_read(monkeypatch):
    app = FastAPI()
    app.include_router(endpoint.router)
    def denied():
        raise HTTPException(401, 'Authentication required')
    app.dependency_overrides[get_current_user] = denied
    def forbidden(*_args):
        raise AssertionError('Directory reached without identity')
    monkeypatch.setattr(endpoint, 'eigene_handelspartner', forbidden)
    with TestClient(app) as client:
        assert client.get('/portal/handelspartner').status_code == 401
        assert client.post('/portal/handelspartner', json={"tenant_id": "b"}).status_code == 405
