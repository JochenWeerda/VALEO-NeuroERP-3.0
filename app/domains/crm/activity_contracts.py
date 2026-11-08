"""Versioned CRM activity command and read contracts.

Tenant and actor identity are deliberately supplied by the execution context.
"""
from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

ActivityType = Literal["meeting", "call", "email", "note", "visit", "task"]
ActivityStatus = Literal["planned", "completed", "cancelled"]
ShortText = Annotated[str, Field(max_length=100)]
ListItem = Annotated[str, Field(max_length=200)]
Items = Annotated[list[ListItem], Field(max_length=100)]
Identifier = Annotated[str, Field(min_length=1, max_length=64)]


class _Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("date",check_fields=False)
    @classmethod
    def canonical_timestamp(cls,value):
        if value is None:return None
        return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value).astimezone(timezone.utc)


class ActivityBase(_Contract):
    type: ActivityType
    title: str = Field(min_length=1, max_length=200)
    customer: ShortText = ""
    contact_person: ShortText = ""
    date: datetime | None = None
    status: ActivityStatus = "planned"
    assigned_to: ShortText = ""
    description: str | None = Field(default=None, max_length=10000)
    customer_id: Identifier | None = None
    contact_id: Identifier | None = None
    opportunity_id: str | None = Field(default=None, max_length=36)
    main_topics: Items = Field(default_factory=list)
    orders_placed: Items = Field(default_factory=list)
    follow_up_actions: Items = Field(default_factory=list)


class ActivityCreateCommand(ActivityBase):
    idempotency_key: str = Field(min_length=1, max_length=200, validation_alias=AliasChoices("idempotency_key", "_idempotencyKey"))
    audit_reason: str | None = Field(default=None, max_length=2000, validation_alias=AliasChoices("audit_reason", "_auditReason"))
    correlation_id: str | None = Field(default=None, max_length=200)


class ActivityUpdateCommand(_Contract):
    type: ActivityType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    customer: ShortText | None = None
    contact_person: ShortText | None = None
    date: datetime | None = None
    status: ActivityStatus | None = None
    assigned_to: ShortText | None = None
    description: str | None = Field(default=None, max_length=10000)
    customer_id: Identifier | None = None
    contact_id: Identifier | None = None
    opportunity_id: str | None = Field(default=None, max_length=36)
    main_topics: Items | None = None
    orders_placed: Items | None = None
    follow_up_actions: Items | None = None
    expected_version: int = Field(ge=1, strict=True)
    idempotency_key: str = Field(min_length=1, max_length=200, validation_alias=AliasChoices("idempotency_key", "_idempotencyKey"))
    audit_reason: str | None = Field(default=None, max_length=2000, validation_alias=AliasChoices("audit_reason", "_auditReason"))
    correlation_id: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def reject_non_nullable_nulls(self):
        for name in ("type", "title", "customer", "contact_person", "status", "assigned_to",
                     "main_topics", "orders_placed", "follow_up_actions"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class ActivityDeleteCommand(_Contract):
    expected_version: int = Field(ge=1, strict=True)
    idempotency_key: str = Field(min_length=1, max_length=200, validation_alias=AliasChoices("idempotency_key", "_idempotencyKey"))
    audit_reason: str | None = Field(default=None, max_length=2000, validation_alias=AliasChoices("audit_reason", "_auditReason"))
    correlation_id: str | None = Field(default=None, max_length=200)


class ActivityRead(ActivityBase):
    # Read responses may be revalidated after serialization; computed fields are always recomputed.
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    id: str
    version: int = Field(ge=1, strict=True)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    @computed_field
    @property
    def overdue(self) -> bool:
        from app.services.list_presets import is_business_overdue
        return is_business_overdue(self.date, self.status)


def normalize_legacy_activity_type(value: str) -> ActivityType:
    values = {"anruf": "call", "besuch": "visit", "e-mail": "email",
              "aufgabe": "task", "meeting": "meeting", "sonstiges": "note",
              "call": "call", "visit": "visit", "email": "email", "task": "task", "note": "note"}
    try:
        return values[value.strip().casefold()]
    except (KeyError, AttributeError) as exc:
        raise ValueError("Unknown legacy activity type") from exc


def normalize_legacy_activity_status(value: str) -> ActivityStatus:
    values = {"overdue": "planned", "offen": "planned", "planned": "planned",
              "completed": "completed", "erledigt": "completed", "cancelled": "cancelled",
              "abgesagt": "cancelled", "storniert": "cancelled"}
    try:
        return values[value.strip().casefold()]
    except (KeyError, AttributeError) as exc:
        raise ValueError("Unknown legacy activity status") from exc
