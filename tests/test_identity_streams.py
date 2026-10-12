"""No cross-tenant delivery in shared event channels."""
import asyncio
from app.core.sse import SSEHub


def test_events_are_isolated_and_cleanup_preserves_other_subscribers():
    async def exercise():
        hub = SSEHub()
        own = await hub.subscribe('workflow', tenant_id='tenant-a')
        foreign = await hub.subscribe('workflow', tenant_id='tenant-b')
        other = await hub.subscribe('audit', tenant_id='tenant-a')
        await hub.broadcast('workflow', {'number': 'private'}, tenant_id='tenant-a')
        assert own.get_nowait() == {'number': 'private'}
        assert foreign.empty() and other.empty()
        await hub.unsubscribe('workflow', own, tenant_id='tenant-a')
        assert hub.get_connection_count('workflow', tenant_id='tenant-b') == 1
        await hub.broadcast('workflow', {'number': 'other'}, tenant_id='tenant-b')
        assert foreign.get_nowait() == {'number': 'other'}
        await hub.unsubscribe('workflow', foreign, tenant_id='tenant-b')
        await hub.unsubscribe('audit', other, tenant_id='tenant-a')
        assert hub._channels == {}
    asyncio.run(exercise())
