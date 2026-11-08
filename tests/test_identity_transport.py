"""Actual signed provider tokens at HTTP and WebSocket transport boundaries."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from test_system_tenant_binding import keys, probe
from main import BearerAuthMiddleware
from app.api.v1.endpoints import websocket, copilot_ws
from app.policy.router import router as policy_router


@pytest.fixture
def transport(probe):
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(websocket.router, prefix='/api/v1')
    app.include_router(copilot_ws.router, prefix='/api/v1')
    app.include_router(policy_router)

    @app.get('/policy/probe')
    @app.get('/api/events')
    def protected():
        return {'ok': True}

    return TestClient(app), probe


def test_non_api_routes_require_the_same_provider_identity(transport):
    client, probe = transport
    assert client.get('/policy/probe').status_code == 401
    assert client.get('/policy/probe', headers=probe.headers()).status_code == 200


def test_query_credentials_are_limited_to_browser_streams(transport):
    client, probe = transport
    token = probe.token()
    assert client.get('/policy/probe', params={'token': token}).status_code == 401
    assert client.get('/api/events', params={'token': token}).status_code == 200
    assert client.get('/api/events', params=[('token', token), ('token', 'foreign')]).status_code == 401


@pytest.mark.parametrize('suffix', ['', '?token=opaque-own-dev-token', '?token=not-a-jwt'])
@pytest.mark.parametrize('path', ['/api/v1/ws/pos/T-1', '/api/v1/ws/workflow/W-1', '/api/v1/copilot/chat'])
def test_websockets_reject_unverified_credentials(transport, path, suffix):
    client, _ = transport
    with pytest.raises(WebSocketDisconnect) as error:
        with client.websocket_connect(path + suffix):
            pytest.fail('Unverified connection accepted')
    assert error.value.code == 1008


@pytest.mark.parametrize('selector', ['tenant_id=tenant-b', 'tenant_id=tenant-a&tenant_id=tenant-b', 'tenant_id='])
def test_websocket_query_cannot_change_provider_tenant(transport, selector):
    client, probe = transport
    with pytest.raises(WebSocketDisconnect) as error:
        with client.websocket_connect('/api/v1/ws/pos/T-1?token=' + probe.token() + '&' + selector):
            pytest.fail('Foreign tenant accepted')
    assert error.value.code == 1008
    assert websocket.active_terminals == {}


def test_two_provider_tenants_use_separate_terminal_registries(transport):
    client, probe = transport
    with client.websocket_connect('/api/v1/ws/pos/T-1?token=' + probe.token('tenant-a')):
        with client.websocket_connect('/api/v1/ws/pos/T-1?token=' + probe.token('tenant-b')):
            assert set(websocket.active_terminals) == {'tenant-a:T-1', 'tenant-b:T-1'}
    assert websocket.active_terminals == {}


def test_workflow_status_uses_verified_tenant(transport, monkeypatch):
    client, probe = transport
    seen = []
    monkeypatch.setattr('app.core.cache.cache_get_json', lambda key: seen.append(key) or {'step': 'done'})
    with client.websocket_connect('/api/v1/ws/workflow/W-1?token=' + probe.token('tenant-b')) as ws:
        ws.send_json({'action': 'status'})
        result = ws.receive_json()
    assert seen == ['workflow:tenant-b:W-1:status']
    assert result['tenant_id'] == 'tenant-b'


def test_copilot_cannot_replace_authenticated_context(transport, monkeypatch):
    client, probe = transport
    seen = []
    monkeypatch.setattr(copilot_ws, '_run_pipeline_sync', lambda text, context: seen.append(dict(context)) or {})
    with client.websocket_connect('/api/v1/copilot/chat?token=' + probe.token('tenant-b')) as ws:
        assert ws.receive_json()['tenant_id'] == 'tenant-b'
        ws.send_json({'text': 'query', 'context': {'tenant_id': 'tenant-a', 'roles': ['admin'], 'user_id': 'mallory'}})
        ws.receive_json()
        ws.receive_json()
    assert seen[0]['tenant_id'] == 'tenant-b'
    assert seen[0]['user_id'] == 'human-a'
    assert seen[0]['roles'] == ['FINANCE_BEARBEITEN']
    assert copilot_ws._SESSIONS == {}


def test_duplicate_json_selectors_fail_before_business(probe):
    response = probe.client.post('/api/probe', content='{"tenant_id":"tenant-b","tenant_id":"tenant-a"}',
                                 headers={**probe.headers(), 'Content-Type': 'application/json'})
    assert response.status_code == 400
    assert probe.calls == []


def test_expired_connection_closes_before_workflow_access(transport, monkeypatch):
    import time
    client, probe = transport
    original = time.time
    clock = [original()]
    monkeypatch.setattr('main.time.time', lambda: clock[0])
    seen = []
    monkeypatch.setattr('app.core.cache.cache_get_json', lambda key: seen.append(key))
    with client.websocket_connect('/api/v1/ws/workflow/W-1?token=' + probe.token()) as ws:
        clock[0] += 600
        ws.send_json({'action': 'status'})
        with pytest.raises(WebSocketDisconnect) as error:
            ws.receive_json()
        assert error.value.code == 1008
    assert seen == []


def test_parallel_requests_keep_distinct_verified_contexts(probe):
    from concurrent.futures import ThreadPoolExecutor
    from app.core.tenant_context import current_tenant_or_none
    before = current_tenant_or_none()
    def exercise(tenant):
        result = probe.client.get('/api/probe', headers=probe.headers(tenant))
        assert result.status_code == 200
        assert result.json()['tenant'] == result.json()['header'] == tenant
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(exercise, ['tenant-a', 'tenant-b'] * 8))
    assert current_tenant_or_none() == before


def test_production_inventory_covers_all_registered_protected_http_routes():
    from fastapi.routing import APIRoute
    from main import app
    public = BearerAuthMiddleware.PUBLIC_PATHS
    expected = [route for route in app.routes if isinstance(route, APIRoute) and route.path not in public]
    assert len(expected) > 100
    assert all(getattr(route, 'tenant_bound', False) for route in expected)
    assert len(app.state.tenant_binding_inventory) == len(expected)
