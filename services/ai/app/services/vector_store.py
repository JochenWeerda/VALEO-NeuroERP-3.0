"""
Vector Store Service
ChromaDB integration for semantic search
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Lazy imports to avoid startup failures
_vector_store = None


async def initialize_vector_store():
    """Initialize ChromaDB vector store"""
    global _vector_store
    
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        from app.config import settings
        
        client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        _vector_store = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "VALEO ERP Knowledge Base"}
        )
        
        logger.info(f"Vector store initialized: {_vector_store.count()} documents")
        return _vector_store
        
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        _vector_store = None
        raise


async def get_vector_store():
    """Get or initialize vector store"""
    global _vector_store
    if _vector_store is None:
        await initialize_vector_store()
    return _vector_store


async def search_similar(
    query: str,
    top_k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Search for similar documents"""
    try:
        store = await get_vector_store()
        if store is None:
            return []
        
        results = store.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_metadata
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "score": 1.0 - distance  # Convert distance to similarity score
            }
            for doc, meta, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []


async def add_document(
    content: str,
    metadata: Dict[str, Any],
    doc_id: Optional[str] = None
) -> str:
    """Add document to vector store"""
    try:
        store = await get_vector_store()
        if store is None:
            raise Exception("Vector store not initialized")
        
        import uuid
        doc_id = doc_id or str(uuid.uuid4())
        
        store.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        logger.info(f"Document added: {doc_id}")
        return doc_id
        
    except Exception as e:
        logger.error(f"Failed to add document: {e}")
        raise

