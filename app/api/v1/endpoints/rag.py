"""
RAG API Endpoints
Semantic search and document indexing
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from ....core.database import get_db
from app.core.tenant import get_tenant_id
from pydantic import Field

logger = logging.getLogger(__name__)


def get_vector_store():
    """Erst beim Aufruf laden: chromadb/sentence-transformers sind schwer und optional."""
    from ....infrastructure.rag.vector_store import get_vector_store as _get_vector_store

    return _get_vector_store()


def get_indexer():
    from ....infrastructure.rag.indexer import get_indexer as _get_indexer

    return _get_indexer()

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.rag_schemas import RagOut


router = APIRouter()


class SearchRequest(BaseModel):
    """RAG search request."""
    query: str
    collection: str = "articles"
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """RAG search result."""
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float


class SearchResponse(BaseModel):
    """RAG search response."""
    query: str
    results: List[SearchResult]
    total: int


class IndexRequest(BaseModel):
    """Indexing request; der Mandant kommt aus dem Token (bis 27.10.2026 Feld mit Vorgabe "system")."""


class IndexResponse(BaseModel):
    """Indexing response."""
    collection: str
    documents_indexed: int
    status: str


def tenant_where(tenant_id: str, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Suchfilter, der immer an den Mandanten gebunden ist.

    Die Collections enthalten Dokumente aller Mandanten (Mandant in den Metadaten). Bis 27.10.2026
    kamen die Filter allein vom Aufrufer: ohne Filter fand die Suche Kunden und Artikel aller
    Mandanten. Filter des Aufrufers schraenken weiter ein, ersetzen den Mandanten aber nie.
    """
    if not filters:
        return {"tenant_id": tenant_id}
    return {"$and": [{"tenant_id": tenant_id}, filters]}


@router.post("/search", response_model=SearchResponse, summary="Search semantic")
async def semantic_search(request: SearchRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    Perform semantic search across indexed documents.
    
    Supports collections: articles, customers, policies
    """
    logger.info(f"RAG search: {request.query} in {request.collection}")
    
    try:
        vector_store = get_vector_store()
        
        results = await vector_store.search(
            collection_name=request.collection,
            query=request.query,
            n_results=request.limit,
            where=tenant_where(tenant_id, request.filters)
        )
        
        # Format response
        search_results = []
        for i, doc_id in enumerate(results["ids"]):
            search_results.append(SearchResult(
                id=doc_id,
                text=results["documents"][i],
                metadata=results["metadatas"][i],
                distance=results["distances"][i]
            ))
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )
    
    except Exception as e:
        logger.error(f"RAG search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/articles", response_model=IndexResponse, summary="Articles index")
async def index_articles(
    request: IndexRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Manually trigger article indexing."""
    logger.info(f"Manual article indexing triggered (tenant: {tenant_id})")
    
    try:
        indexer = get_indexer()
        count = await indexer.index_articles(db, tenant_id)
        
        return IndexResponse(
            collection="articles",
            documents_indexed=count,
            status="completed"
        )
    
    except Exception as e:
        logger.error(f"Article indexing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/customers", response_model=IndexResponse, summary="Customers index")
async def index_customers(
    request: IndexRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Manually trigger customer indexing."""
    logger.info(f"Manual customer indexing triggered (tenant: {tenant_id})")
    
    try:
        indexer = get_indexer()
        count = await indexer.index_customers(db, tenant_id)
        
        return IndexResponse(
            collection="customers",
            documents_indexed=count,
            status="completed"
        )
    
    except Exception as e:
        logger.error(f"Customer indexing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{collection}", summary="Collection stats abrufen",
    response_model=RagOut
)
async def get_collection_stats(collection: str):
    """Get statistics for a collection."""
    try:
        vector_store = get_vector_store()
        stats = await vector_store.get_stats(collection)
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

