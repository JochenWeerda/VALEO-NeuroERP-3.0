"""Pydantic-Modelle für FiBu-Events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator

from .enums import FiBuEventType


class EventMetadata(BaseModel):
    """Standard-Metadaten für FiBu-Events."""

    model_config = ConfigDict(populate_by_name=True)

    event_type: FiBuEventType
    version: str = "1.0"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    tenant_id: str
    correlation_id: str | None = None
    causation_id: str | None = None
    source: str = "fibu-gateway"

    @field_validator("tenant_id", "version", "source")
    @classmethod
    def _ensure_non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Feld darf nicht leer sein.")
        return value


class FiBuEventPayload(BaseModel):
    """Basisklasse für Payloads."""

    tenant_id: str

    @field_validator("tenant_id")
    @classmethod
    def _tenant_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("tenant_id darf nicht leer sein.")
        return value


class BookingCreatedPayload(FiBuEventPayload):
    booking_id: UUID
    account_id: str
    amount: Decimal
    currency: str = "EUR"
    period: str
    document_id: UUID | None = None
    approved: bool = False


class BookingApprovedPayload(FiBuEventPayload):
    booking_id: UUID
    approver_id: str
    approved_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    comment: str | None = None


class AccountUpdatedPayload(FiBuEventPayload):
    account_id: str
    account_number: str
    account_name: str
    status: str = "active"


class OpenItemCreatedPayload(FiBuEventPayload):
    op_id: UUID
    customer_id: str
    amount: Decimal
    currency: str = "EUR"
    due_date: datetime


PayloadT = TypeVar("PayloadT", bound=FiBuEventPayload)


class FiBuEventEnvelope(BaseModel, Generic[PayloadT]):
    """Einhüllung eines Events inkl. Metadaten."""

    id: UUID = Field(default_factory=uuid4)
    metadata: EventMetadata
    payload: PayloadT

    def serialize(self) -> Dict[str, Any]:
        return json.loads(self.model_dump_json())


class BookingCreatedEvent(FiBuEventEnvelope[BookingCreatedPayload]):
    @classmethod
    def from_values(
        cls,
        *,
        tenant_id: str,
        booking_id: str | UUID,
        account_id: str,
        amount: Decimal,
        currency: str,
        period: str,
        document_id: str | UUID | None = None,
        approved: bool = False,
        correlation_id: str | None = None,
        source: str = "fibu-gateway",
    ) -> "BookingCreatedEvent":
        payload = BookingCreatedPayload(
            tenant_id=tenant_id,
            booking_id=UUID(str(booking_id)),
            account_id=account_id,
            amount=amount,
            currency=currency,
            period=period,
            document_id=UUID(str(document_id)) if document_id else None,
            approved=approved,
        )
        metadata = EventMetadata(
            event_type=FiBuEventType.BOOKING_CREATED,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            source=source,
        )
        return cls(metadata=metadata, payload=payload)


class BookingApprovedEvent(FiBuEventEnvelope[BookingApprovedPayload]):
    @classmethod
    def from_values(
        cls,
        *,
        tenant_id: str,
        booking_id: str | UUID,
        approver_id: str,
        comment: str | None = None,
        source: str = "fibu-gateway",
    ) -> "BookingApprovedEvent":
        payload = BookingApprovedPayload(
            tenant_id=tenant_id,
            booking_id=UUID(str(booking_id)),
            approver_id=approver_id,
            comment=comment,
        )
        metadata = EventMetadata(
            event_type=FiBuEventType.BOOKING_APPROVED,
            tenant_id=tenant_id,
            source=source,
        )
        return cls(metadata=metadata, payload=payload)


class AccountUpdatedEvent(FiBuEventEnvelope[AccountUpdatedPayload]):
    @classmethod
    def from_values(
        cls,
        *,
        tenant_id: str,
        account_id: str,
        account_number: str,
        account_name: str,
        status: str = "active",
        source: str = "fibu-master-data",
    ) -> "AccountUpdatedEvent":
        payload = AccountUpdatedPayload(
            tenant_id=tenant_id,
            account_id=account_id,
            account_number=account_number,
            account_name=account_name,
            status=status,
        )
        metadata = EventMetadata(
            event_type=FiBuEventType.MASTER_DATA_ACCOUNT_UPDATED,
            tenant_id=tenant_id,
            source=source,
        )
        return cls(metadata=metadata, payload=payload)


class OpenItemCreatedEvent(FiBuEventEnvelope[OpenItemCreatedPayload]):
    @classmethod
    def from_values(
        cls,
        *,
        tenant_id: str,
        op_id: str | UUID,
        customer_id: str,
        amount: Decimal,
        currency: str = "EUR",
        due_date: datetime,
        source: str = "fibu-op",
    ) -> "OpenItemCreatedEvent":
        payload = OpenItemCreatedPayload(
            tenant_id=tenant_id,
            op_id=UUID(str(op_id)),
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            due_date=due_date,
        )
        metadata = EventMetadata(
            event_type=FiBuEventType.OPEN_ITEM_CREATED,
            tenant_id=tenant_id,
            source=source,
        )
        return cls(metadata=metadata, payload=payload)


