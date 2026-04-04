"""Port contract for read-only partner/legacy preview adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class PartnerPreview(BaseModel):
    partner_key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    mapped_steps: list[str] = Field(default_factory=list)
    notices: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class PartnerAdapterPort(ABC):
    @abstractmethod
    def preview_partner_mapping(
        self,
        *,
        tenant_id: str,
        partner_key: str,
        sample_payload: dict[str, str] | None = None,
    ) -> PartnerPreview:
        raise NotImplementedError
