from decimal import Decimal

import pytest

from app.integration.event_publisher import FiBuEventPublisher


class _DummyNATS:
    def __init__(self) -> None:
        self.connected = False
        self.published: list[tuple[str, bytes]] = []

    async def connect(self, *, servers, name):  # noqa: D401
        self.connected = True

    async def publish(self, subject, payload):
        self.published.append((subject, payload))

    async def drain(self):
        self.connected = False

    async def close(self):
        pass

    @property
    def is_connected(self):
        return self.connected


@pytest.mark.asyncio
async def test_event_publisher_writes_to_nats():
    dummy = _DummyNATS()
    publisher = FiBuEventPublisher(
        enabled=True,
        url="nats://stub",
        subject_booking_created="fibu.booking.created",
        client_factory=lambda: dummy,
    )

    await publisher.publish_booking_created(
        tenant_id="tenant-1",
        booking_id="123e4567-e89b-12d3-a456-426614174000",
        account_id="8400",
        amount=Decimal("10.00"),
        currency="EUR",
        period="2025-11",
    )

    assert dummy.published
    await publisher.close()
    assert dummy.connected is False


@pytest.mark.asyncio
async def test_event_publisher_skips_when_disabled():
    dummy = _DummyNATS()
    publisher = FiBuEventPublisher(
        enabled=False,
        url="nats://stub",
        subject_booking_created="fibu.booking.created",
        client_factory=lambda: dummy,
    )

    await publisher.publish_booking_created(
        tenant_id="tenant-1",
        booking_id="123e4567-e89b-12d3-a456-426614174000",
        account_id="8400",
        amount=Decimal("10.00"),
        currency="EUR",
        period="2025-11",
    )

    assert dummy.published == []

