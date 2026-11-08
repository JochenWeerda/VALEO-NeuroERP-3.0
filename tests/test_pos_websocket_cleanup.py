"""Deterministic transport cleanup; verified-token integration remains separate."""
import asyncio
import json
import pytest
from starlette.websockets import WebSocketDisconnect
from app.api.v1.endpoints import websocket as endpoint

pytestmark = pytest.mark.asyncio


class Socket:
    def __init__(self, failure=None):
        self.entered = asyncio.Event()
        self.failure = failure

    async def accept(self):
        pass

    async def receive_text(self):
        self.entered.set()
        if self.failure is not None:
            raise self.failure
        await asyncio.Future()


@pytest.fixture
def registry(monkeypatch):
    values = {}
    monkeypatch.setattr(endpoint, 'active_terminals', values)
    monkeypatch.setattr(endpoint, '_resolve_authenticated_context', lambda *_args: {'tenant_id': 'synthetic-own'})
    return values


async def test_cancelled_connection_leaves_no_terminal_entry(registry):
    socket = Socket()
    task = asyncio.create_task(endpoint.pos_websocket(socket, 'T-1', None, None))
    await asyncio.wait_for(socket.entered.wait(), 1)
    assert registry == {'synthetic-own:T-1': {socket}}
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert registry == {}


@pytest.mark.parametrize('failure', [WebSocketDisconnect(), RuntimeError('synthetic transport failure'), json.JSONDecodeError('invalid', '', 0)])
async def test_disconnect_and_receive_errors_remove_empty_registry(registry, failure):
    await endpoint.pos_websocket(Socket(failure), 'T-1', None, None)
    assert registry == {}


async def test_cancellation_preserves_other_terminal_connections_and_other_tenants(registry):
    same_terminal, foreign = object(), object()
    registry.update({'synthetic-own:T-1': {same_terminal}, 'synthetic-other:T-1': {foreign}})
    socket = Socket()
    task = asyncio.create_task(endpoint.pos_websocket(socket, 'T-1', None, None))
    await asyncio.wait_for(socket.entered.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert registry == {'synthetic-own:T-1': {same_terminal}, 'synthetic-other:T-1': {foreign}}
