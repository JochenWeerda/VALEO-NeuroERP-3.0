"""Read-only customer profile preview port."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field


class CustomerProfilePreview(BaseModel):
    customer_id: str
    display_name: str
    status: str = "active"
    email: str | None = None
    city: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class CustomerProfilePort(Protocol):
    def preview_customer_profile(self, *, tenant_id: str, customer_id: str) -> CustomerProfilePreview:
        """Return a read-only customer profile preview from an external connector."""
