"""
RAG (Retrieval-Augmented Generation) Endpoint
Semantic Search über ERP-Daten und Wissensbasis
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


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
    """
    Semantische Suche über ERP-Wissensbasis
    
    Findet relevante:
    - Dokumentation
    - Policies
    - Ähnliche Vorgänge
    - Best Practices
    """
    
    # Mock implementation - später mit ChromaDB + OpenAI
    mock_sources = [
        SearchResult(
            content="SKR03 ist der Standard-Kontenrahmen für kleine und mittlere Unternehmen in Deutschland. Er wird besonders in der Landwirtschaft eingesetzt.",
            source="docs/fibu/kontenrahmen.md",
            score=0.92,
            metadata={"domain": "finance", "type": "documentation"}
        ),
        SearchResult(
            content="Bei Cross-Compliance müssen alle Feldmaßnahmen im Feldbuch dokumentiert werden. Verstöße führen zu Kürzungen der EU-Förderung.",
            source="docs/agrar/compliance.md",
            score=0.87,
            metadata={"domain": "agrar", "type": "policy"}
        )
    ]
    
    # Filter by domain if specified
    if request.domain:
        mock_sources = [s for s in mock_sources if s.metadata.get("domain") == request.domain]
    
    # Generate answer (mock)
    answer = None
    if request.include_answer and mock_sources:
        answer = f"Basierend auf {len(mock_sources)} Quellen: {mock_sources[0].content[:100]}..."
    
    return RAGResponse(
        answer=answer,
        sources=mock_sources[:request.top_k],
        query=request.query
    )


@router.post("/index/document")
async def index_document(
    content: str,
    source: str,
    metadata: Optional[dict] = None
) -> dict:
    """
    Indexiert Dokument in Vector Store für spätere Suche
    """
    # Mock - später mit ChromaDB
    return {
        "status": "indexed",
        "source": source,
        "chunks": 3,
        "vector_count": 12
    }


@router.delete("/index/{source}")
async def remove_from_index(source: str) -> dict:
    """Entfernt Dokument aus Vector Store"""
    return {"status": "removed", "source": source}

