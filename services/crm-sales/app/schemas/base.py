"""Shared schema utilities for CRM Sales service."""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic pagination response."""

    items: List[T] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1)
    pages: int = Field(default=1, ge=1)
    has_next: bool = False
    has_prev: bool = False

    class Config:
        arbitrary_types_allowed = True
