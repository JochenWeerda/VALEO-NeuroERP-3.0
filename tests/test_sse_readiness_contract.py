"""Readiness probes hub responsiveness without tenant data or false health."""
import asyncio
import pytest
from app.core import health
from app.core.sse import SSEHub


@pytest.fixture
def hub(monkeypatch):
    instance = SSEHub()
    monkeypatch.setattr(health, 'sse_hub', instance)
    return instance


@pytest.mark.asyncio
async def test_healthy_hub_does_not_read_tenant_connection_counts(hub, monkeypatch):
    first = await hub.subscribe('workflow', tenant_id='synthetic-tenant-a')
    second = await hub.subscribe('workflow', tenant_id='synthetic-tenant-b')
    def forbidden(*args, **kwargs):
        raise AssertionError('Tenant counters must not be used by readiness')
    monkeypatch.setattr(hub, 'get_connection_count', forbidden)
    assert await health.check_sse_hub() == (True, 'SSE hub responsive')
    await hub.broadcast('workflow', {'synthetic': True}, tenant_id='synthetic-tenant-a')
    assert first.get_nowait() == {'synthetic': True}
    assert second.empty()


@pytest.mark.asyncio
async def test_blocked_hub_fails_with_a_bounded_probe_and_recovers(hub):
    async with hub._lock:
        ready, message = await asyncio.wait_for(health.check_sse_hub(), timeout=2)
        assert ready is False
        assert 'timed out' in message
    assert await health.check_sse_hub() == (True, 'SSE hub responsive')


@pytest.mark.asyncio
async def test_probe_failure_is_not_reported_as_ready(hub, monkeypatch):
    async def fail():
        raise RuntimeError('synthetic-internal-detail')
    monkeypatch.setattr(hub, 'ping', fail)
    assert await health.check_sse_hub() == (False, 'SSE hub probe failed')


@pytest.mark.asyncio
async def test_cancelled_probe_propagates_without_holding_the_lock(hub):
    async with hub._lock:
        task = asyncio.create_task(health.check_sse_hub())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert not hub._lock.locked()
    assert await health.check_sse_hub() == (True, 'SSE hub responsive')


@pytest.mark.asyncio
async def test_database_failure_keeps_overall_readiness_red(hub, monkeypatch):
    async def unavailable():
        return False, 'synthetic database unavailable'
    monkeypatch.setattr(health, 'check_postgresql', unavailable)
    result = await health.readiness_check()
    assert result['ready'] is False
    assert result['checks']['postgresql']['healthy'] is False
    assert result['checks']['sse_hub']['healthy'] is True
