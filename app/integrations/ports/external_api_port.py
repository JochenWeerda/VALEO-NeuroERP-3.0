"""Generic read-only external API port contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ExternalApiResult(BaseModel):
    """Normalized payload returned from an external API preview or lookup."""

    resource_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: str = Field(default="ok", min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)


class ExternalApiPort(ABC):
    @abstractmethod
    def preview_resource(self, *, tenant_id: str, resource_id: str) -> ExternalApiResult:
        raise NotImplementedError
