"""Enum-Definitionen für FiBu-Events."""

from __future__ import annotations

from enum import Enum


class FiBuEventCategory(str, Enum):
    """Grobe Einteilung der Eventströme."""

    BOOKING = "booking"
    MASTER_DATA = "master_data"
    OPEN_ITEM = "open_item"


class FiBuEventType(str, Enum):
    """Offizielle Eventnamen (NATS Subjects)."""

    BOOKING_CREATED = "fibu.booking.created"
    BOOKING_APPROVED = "fibu.booking.approved"
    MASTER_DATA_ACCOUNT_UPDATED = "fibu.master_data.account.updated"
    OPEN_ITEM_CREATED = "fibu.op.created"

    def category(self) -> FiBuEventCategory:
        if self in (FiBuEventType.BOOKING_CREATED, FiBuEventType.BOOKING_APPROVED):
            return FiBuEventCategory.BOOKING
        if self is FiBuEventType.MASTER_DATA_ACCOUNT_UPDATED:
            return FiBuEventCategory.MASTER_DATA
        return FiBuEventCategory.OPEN_ITEM


