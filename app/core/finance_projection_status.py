from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectionStatusEntry(BaseModel):
    projection_key: str
    item_count: int = 0
    cached: bool = True
    cursor_status: str | None = None
    cursor_source: str | None = None
    cursor_updated_at: str | None = None
    last_processed_event_id: str | None = None


class ProjectionStatusReadModel(BaseModel):
    tenant_id: str
    projection_count: int = 0
    persisted_snapshot_count: int = 0
    persisted_cursor_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_rebuilt_at: str | None = None
    last_snapshot_at: str | None = None
    last_cursor_advanced_at: str | None = None
    last_processed_event_id: str | None = None
    projections: list[ProjectionStatusEntry] = Field(default_factory=list)
    schema_version: int = 1
