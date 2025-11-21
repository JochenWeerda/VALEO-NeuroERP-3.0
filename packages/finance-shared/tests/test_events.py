from uuid import uuid4

from finance_shared.events import BookingApprovedEvent, BookingCreatedEvent


def test_booking_created_event_contains_payload():
    event = BookingCreatedEvent.from_values(
        tenant_id="tenant-1",
        booking_id=uuid4(),
        account_id="8400",
        amount=123.45,
        currency="EUR",
        period="2025-11",
        approved=True,
    )

    data = event.serialize()
    assert data["payload"]["account_id"] == "8400"
    assert data["payload"]["approved"] is True


def test_booking_approved_event_serialization():
    event = BookingApprovedEvent.from_values(
        tenant_id="tenant-1",
        booking_id=uuid4(),
        approver_id="user-42",
        comment="OK",
    )

    data = event.serialize()
    assert data["metadata"]["event_type"] == "fibu.booking.approved"
    assert data["payload"]["approver_id"] == "user-42"


