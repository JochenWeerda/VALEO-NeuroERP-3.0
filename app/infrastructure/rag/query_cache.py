"""
RAG Query Cache
Caches vector search results to improve performance
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CachedResult:
    """Cached RAG query result."""
    query: str
    results: List[Dict[str, Any]]
    timestamp: datetime
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        expiry = self.timestamp + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > expiry


class RAGQueryCache:
    """
    In-memory cache for RAG queries.
    In production: Use Redis for distributed caching.
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes
        self.cache: Dict[str, CachedResult] = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def _make_key(
        self,
        query: str,
        collection: str,
        filters: Optional[Dict] = None
    ) -> str:
        """Generate cache key from query parameters."""
        key_data = {
            "query": query,
            "collection": collection,
            "filters": filters or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def get(
        self,
        query: str,
        collection: str,
        filters: Optional[Dict] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached results if available and not expired."""
        key = self._make_key(query, collection, filters)
        
        cached = self.cache.get(key)
        if cached is None:
            self.misses += 1
            return None
        
        if cached.is_expired():
            logger.debug(f"Cache expired for key: {key}")
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        logger.debug(f"Cache hit for query: {query[:50]}...")
        return cached.results
    
    def set(
        self,
        query: str,
        collection: str,
        results: List[Dict[str, Any]],
        filters: Optional[Dict] = None,
        ttl: Optional[int] = None
    ) -> None:
        """Cache query results."""
        key = self._make_key(query, collection, filters)
        
        cached_result = CachedResult(
            query=query,
            results=results,
            timestamp=datetime.utcnow(),
            ttl_seconds=ttl or self.default_ttl
        )
        
        self.cache[key] = cached_result
        logger.debug(f"Cached results for query: {query[:50]}...")
    
    def invalidate(
        self,
        collection: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries.
        If collection is specified, only invalidate that collection.
        Returns count of invalidated entries.
        """
        if collection is None:
            # Clear all
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"Invalidated entire RAG cache ({count} entries)")
            return count
        
        # Invalidate by collection
        # (Simple implementation: clear all for now)
        count = len(self.cache)
        self.cache.clear()
        logger.info(
            f"Invalidated RAG cache for collection={collection} "
            f"({count} entries)"
        )
        return count
    
    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        before_count = len(self.cache)
        
        expired_keys = [
            key for key, cached in self.cache.items()
            if cached.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        removed = len(expired_keys)
        if removed > 0:
            logger.info(f"Cleaned up {removed} expired cache entries")
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


# Global instance
_query_cache: Optional[RAGQueryCache] = None


def get_query_cache() -> RAGQueryCache:
    """Get the global query cache instance."""
    global _query_cache
    if _query_cache is None:
        _query_cache = RAGQueryCache()
    return _query_cache

