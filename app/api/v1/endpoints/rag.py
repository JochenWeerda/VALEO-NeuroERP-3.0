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
from ....infrastructure.rag.vector_store import get_vector_store
from ....infrastructure.rag.indexer import get_indexer

logger = logging.getLogger(__name__)

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
    """Indexing request."""
    tenant_id: str = "system"


class IndexResponse(BaseModel):
    """Indexing response."""
    collection: str
    documents_indexed: int
    status: str


@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
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
            where=request.filters
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


@router.post("/index/articles", response_model=IndexResponse)
async def index_articles(
    request: IndexRequest,
    db: Session = Depends(get_db)
):
    """Manually trigger article indexing."""
    logger.info(f"Manual article indexing triggered (tenant: {request.tenant_id})")
    
    try:
        indexer = get_indexer()
        count = await indexer.index_articles(db, request.tenant_id)
        
        return IndexResponse(
            collection="articles",
            documents_indexed=count,
            status="completed"
        )
    
    except Exception as e:
        logger.error(f"Article indexing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/customers", response_model=IndexResponse)
async def index_customers(
    request: IndexRequest,
    db: Session = Depends(get_db)
):
    """Manually trigger customer indexing."""
    logger.info(f"Manual customer indexing triggered (tenant: {request.tenant_id})")
    
    try:
        indexer = get_indexer()
        count = await indexer.index_customers(db, request.tenant_id)
        
        return IndexResponse(
            collection="customers",
            documents_indexed=count,
            status="completed"
        )
    
    except Exception as e:
        logger.error(f"Customer indexing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{collection}")
async def get_collection_stats(collection: str):
    """Get statistics for a collection."""
    try:
        vector_store = get_vector_store()
        stats = await vector_store.get_stats(collection)
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

