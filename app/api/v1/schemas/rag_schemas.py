"""Auto-generated domain schemas for rag.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class RagOut(BaseSchema):
    """Response schema for rag endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class SearchRequest(BaseModel):
    """RAG search request."""
    query: str
    collection: str = "articles"
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """RAG search response."""
    query: str
    results: List[SearchResult]
    total: int


class IndexRequest(BaseModel):
    """Indexing request."""
    tenant_id: str = "system"


class IndexResponse(BaseModel):
    """Indexing response."""
    collection: str
    documents_indexed: int
    status: str

