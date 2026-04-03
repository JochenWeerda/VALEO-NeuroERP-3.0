"""Port contract for external document lookups."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_system: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    url: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class DocumentPort(ABC):
    @abstractmethod
    def search_documents(self, *, tenant_id: str, query: str, limit: int = 10) -> list[DocumentMetadata]:
        raise NotImplementedError
