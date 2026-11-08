"""Actual task cancellation and stream cleanup, no network or database."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from app.core import sse_manager as sse


@pytest.mark.asyncio
async def test_normal_owned_heartbeat_stop_and_restart():
    manager = sse.SSEManager(heartbeat_interval=3600)
    await manager.start_heartbeat()
    first = manager._heartbeat_task
    await asyncio.sleep(0)
    await manager.stop_heartbeat()
    assert first.cancelled()
    assert manager._heartbeat_task is None
    await manager.start_heartbeat()
    assert manager._heartbeat_task is not first
    await manager.stop_heartbeat()
    await manager.stop_heartbeat()


@pytest.mark.asyncio
async def test_loop_preserves_cancellation_signal():
    manager = sse.SSEManager(heartbeat_interval=3600)
    task = asyncio.create_task(manager._heartbeat_loop())
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert task.cancelled()


@pytest.mark.asyncio
async def test_stream_cancellation_unregisters_connection(monkeypatch):
    manager = sse.SSEManager()
    connection = sse.SSEConnection('synthetic', 'test-client')
    manager.register(connection.channel, connection)
    monkeypatch.setattr(sse, 'get_sse_manager', lambda: manager)
    request = SimpleNamespace(is_disconnected=AsyncMock(return_value=False))
    stream = sse.sse_event_generator(request, connection)
    task = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert manager.connections == {}
    await stream.aclose()


@pytest.mark.asyncio
async def test_cancellation_of_stopping_caller_is_not_absorbed():
    manager = sse.SSEManager()
    child_started, child_cleaning = asyncio.Event(), asyncio.Event()
    async def child():
        child_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            child_cleaning.set()
            await asyncio.Event().wait()
    task = asyncio.create_task(child())
    manager._heartbeat_task = task
    await child_started.wait()
    stopping = asyncio.create_task(manager.stop_heartbeat())
    await child_cleaning.wait()
    stopping.cancel()
    with pytest.raises(asyncio.CancelledError):
        await stopping
    assert stopping.cancelled()
    assert task.cancelled()
    assert manager._heartbeat_task is None


@pytest.mark.asyncio
async def test_child_failure_is_visible_and_reference_is_cleared():
    manager = sse.SSEManager()
    async def broken():
        raise RuntimeError('synthetic-task-failure')
    task = asyncio.create_task(broken())
    manager._heartbeat_task = task
    await asyncio.sleep(0)
    with pytest.raises(RuntimeError, match='synthetic-task-failure'):
        await manager.stop_heartbeat()
    assert manager._heartbeat_task is None
