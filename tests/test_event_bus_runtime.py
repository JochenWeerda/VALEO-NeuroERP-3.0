from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.domains.shared import events


@pytest.fixture(autouse=True)
def _reset_event_publisher_cache():
    events._event_publisher = None
    yield
    events._event_publisher = None


def test_get_event_publisher_returns_memory_when_disabled(monkeypatch):
    fake_settings = SimpleNamespace(
        EVENT_BUS_PROVIDER="memory",
        EVENT_BUS_ENABLED=False,
        EVENT_BUS_NATS_URL="nats://localhost:4222",
    )
    monkeypatch.setattr(events, "settings", fake_settings)

    publisher = events.get_event_publisher()

    assert isinstance(publisher, events.InMemoryEventPublisher)


def test_get_event_publisher_returns_nats_when_enabled(monkeypatch):
    fake_settings = SimpleNamespace(
        EVENT_BUS_PROVIDER="nats",
        EVENT_BUS_ENABLED=True,
        EVENT_BUS_NATS_URL="nats://nats:4222",
    )
    monkeypatch.setattr(events, "settings", fake_settings)

    class FakePublisher:
        enabled = False
        nats_url = "nats://localhost:4222"

    fake_publisher = FakePublisher()

    import app.infrastructure.eventbus.nats_publisher as publisher_module

    monkeypatch.setattr(publisher_module, "nats_publisher", fake_publisher)

    publisher = events.get_event_publisher()

    assert publisher is fake_publisher
    assert publisher.enabled is True
    assert publisher.nats_url == "nats://nats:4222"


@pytest.mark.asyncio
async def test_startup_event_consumer_skips_when_disabled(monkeypatch):
    fake_settings = SimpleNamespace(EVENT_BUS_PROVIDER="memory", EVENT_BUS_ENABLED=False)
    monkeypatch.setattr(events, "settings", fake_settings)

    calls: list[str] = []

    async def fake_start():
        calls.append("start")

    import app.infrastructure.eventbus.nats_consumer as consumer_module

    monkeypatch.setattr(consumer_module.nats_consumer, "start", fake_start)

    await events.startup_event_consumer()

    assert calls == []
