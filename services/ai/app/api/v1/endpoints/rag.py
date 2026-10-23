"""
RAG (Retrieval-Augmented Generation) Endpoint
Semantic Search über ERP-Daten und Wissensbasis
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(responses={503: {"description": "RAG backend is not configured"}})


class SearchResult(BaseModel):
    """Single search result"""
    content: str
    source: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)


class RAGRequest(BaseModel):
    """RAG search request"""
    query: str = Field(..., min_length=1, description="Suchanfrage in natürlicher Sprache")
    domain: Optional[str] = Field(None, description="Domäne einschränken (sales, finance, etc.)")
    top_k: int = Field(default=5, ge=1, le=20, description="Anzahl Ergebnisse")
    include_answer: bool = Field(default=True, description="LLM-generierte Antwort inkludieren?")


class RAGResponse(BaseModel):
    """RAG search response"""
    answer: Optional[str] = None
    sources: List[SearchResult] = Field(default_factory=list)
    query: str


@router.post("/search", response_model=RAGResponse)
async def semantic_search(request: RAGRequest) -> RAGResponse:
    """Reject search until a tenant-isolated RAG backend is available."""
    raise HTTPException(status_code=503, detail={
        "code": "rag_backend_unavailable",
        "message": "Semantische Suche ist nicht eingerichtet. Es werden keine Suchergebnisse simuliert.",
    })


@router.post("/index/document")
async def index_document(
    content: str,
    source: str,
    metadata: Optional[dict] = None
) -> dict:
    """
    Dokumentindexierung ist bis zur Backend-Integration nicht verfuegbar
    """
    raise HTTPException(status_code=503, detail={
        "code": "rag_backend_unavailable", "message": "Dokumentindexierung ist nicht eingerichtet.",
    })


@router.delete("/index/{source}")
async def remove_from_index(source: str) -> dict:
    """Ablehnung ohne verfuegbaren Dokumentindex"""
    raise HTTPException(status_code=503, detail={"code": "rag_backend_unavailable", "message": "Kein Dokumentindex eingerichtet."})


