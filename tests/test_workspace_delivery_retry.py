"""Delivery identity must survive failures and remain tenant scoped."""
import asyncio
import pytest
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("workspace_delivery_under_test", Path(__file__).parents[1] / "app/workspace/events.py")
events = importlib.util.module_from_spec(spec)
spec.loader.exec_module(events)
publish_workspace_sse = events.publish_workspace_sse
reset_workspace_sse_dedup = events.reset_workspace_sse_dedup

@pytest.fixture(autouse=True)
def reset():
    reset_workspace_sse_dedup()

class Hub:
    def __init__(self):
        self.calls = []
        self.fail = False
    async def broadcast(self, channel, envelope, *, tenant_id):
        self.calls.append(tenant_id)
        if self.fail:
            raise RuntimeError("synthetic delivery failure")

async def send(hub, tenant="tenant-a", kind="LOADING_STARTED"):
    return await publish_workspace_sse(kind, tenant_id=tenant, event_id="same-id", hub=hub)

def test_failed_delivery_can_retry_and_success_is_deduplicated():
    async def run():
        hub = Hub()
        hub.fail = True
        assert await send(hub) is None
        hub.fail = False
        assert await send(hub) is not None
        assert await send(hub) is None
        assert len(hub.calls) == 2
    asyncio.run(run())

def test_same_id_in_other_tenant_is_independent():
    async def run():
        hub = Hub()
        assert await send(hub) is not None
        assert await send(hub, "tenant-b") is not None
        assert hub.calls == ["tenant-a", "tenant-b"]
    asyncio.run(run())

def test_unmapped_type_does_not_consume_identity():
    async def run():
        hub = Hub()
        assert await send(hub, kind="unknown.event") is None
        assert await send(hub) is not None
        assert len(hub.calls) == 1
    asyncio.run(run())

def test_concurrent_duplicate_is_broadcast_once():
    async def run():
        started, release = asyncio.Event(), asyncio.Event()
        class SlowHub(Hub):
            async def broadcast(self, *args, **kwargs):
                started.set()
                await release.wait()
                await super().broadcast(*args, **kwargs)
        hub = SlowHub()
        first = asyncio.create_task(send(hub))
        await started.wait()
        second = asyncio.create_task(send(hub))
        await asyncio.sleep(0)
        release.set()
        results = await asyncio.gather(first, second)
        assert sum(result is not None for result in results) == 1
        assert len(hub.calls) == 1
    asyncio.run(run())

def test_cancelled_delivery_can_retry():
    async def run():
        started = asyncio.Event()
        class WaitingHub(Hub):
            async def broadcast(self, *args, **kwargs):
                started.set()
                await asyncio.Event().wait()
        first = asyncio.create_task(send(WaitingHub()))
        await started.wait()
        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first
        assert await send(Hub()) is not None
    asyncio.run(run())
