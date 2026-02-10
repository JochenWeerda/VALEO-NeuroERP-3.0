"""
Vector Store Service
Manages embeddings and similarity search using ChromaDB
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector embeddings and similarity search."""
    
    def __init__(
        self, 
        persist_directory: str = "data/chromadb",
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Where to store ChromaDB data
            model_name: Sentence-Transformers model for embeddings
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Initialize embedding model (German-optimized)
        self.embedding_model = SentenceTransformer(model_name)
        
        logger.info(f"Vector store initialized (model: {model_name})")
    
    def get_or_create_collection(self, name: str) -> chromadb.Collection:
        """Get or create a collection."""
        return self.client.get_or_create_collection(name=name)
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to collection.
        
        Args:
            collection_name: Name of collection
            documents: List of text documents
            metadatas: List of metadata dicts
            ids: List of document IDs
        """
        collection = self.get_or_create_collection(collection_name)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to {collection_name}")
    
    async def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Semantic search in collection.
        
        Args:
            collection_name: Name of collection
            query: Search query
            n_results: Number of results to return
            where: Metadata filter
        
        Returns:
            Search results with documents, distances, metadatas
        """
        collection = self.get_or_create_collection(collection_name)
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        logger.info(f"Search in {collection_name}: {n_results} results")
        
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }
    
    async def delete_document(self, collection_name: str, document_id: str) -> None:
        """Delete a document from collection."""
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=[document_id])
        logger.info(f"Deleted document {document_id} from {collection_name}")
    
    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""
        collection = self.get_or_create_collection(collection_name)
        count = collection.count()
        
        return {
            "collection": collection_name,
            "document_count": count,
            "model": self.embedding_model.get_sentence_embedding_dimension()
        }
    
    async def reset_collection(self, collection_name: str) -> None:
        """Delete and recreate a collection."""
        try:
            self.client.delete_collection(name=collection_name)
        except:
            pass
        self.client.create_collection(name=collection_name)
        logger.info(f"Reset collection {collection_name}")


# Global instance
_vector_store: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """Get the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store

