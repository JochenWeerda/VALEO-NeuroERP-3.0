"""
RAG Indexer Background Worker
Periodically indexes new/updated entities into vector store
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.infrastructure.rag.indexer import get_indexer

logger = logging.getLogger(__name__)


class RAGIndexerWorker:
    """Background worker to keep vector store synchronized."""
    
    def __init__(self, interval_seconds: int = 300):  # 5 minutes
        self.interval = interval_seconds
        self.running = False
        self.last_sync: Optional[datetime] = None
    
    async def start(self) -> None:
        """Start the RAG indexer worker."""
        self.running = True
        logger.info(
            f"RAG Indexer worker started (interval: {self.interval}s)"
        )
        
        while self.running:
            try:
                await self._index_batch()
            except Exception as e:
                logger.error(
                    f"RAG indexer error: {e}",
                    exc_info=True
                )
            
            await asyncio.sleep(self.interval)
        
        logger.info("RAG Indexer worker stopped")
    
    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
    
    async def _index_batch(self) -> None:
        """Index a batch of entities."""
        db: Session = SessionLocal()
        
        try:
            indexer = get_indexer()
            
            # Index all tenants (in production: only updated since last_sync)
            tenant_id = "system"  # TODO: Multi-tenant support
            
            # Index articles
            article_count = await indexer.index_articles(db, tenant_id)
            logger.info(f"Indexed {article_count} articles")
            
            # Index customers
            customer_count = await indexer.index_customers(db, tenant_id)
            logger.info(f"Indexed {customer_count} customers")
            
            self.last_sync = datetime.utcnow()
            
            logger.info(
                f"✅ RAG indexing complete: "
                f"{article_count} articles, {customer_count} customers"
            )
        
        finally:
            db.close()


# Global worker instance
_rag_worker: Optional[RAGIndexerWorker] = None


def get_rag_worker() -> RAGIndexerWorker:
    """Get the global RAG worker instance."""
    global _rag_worker
    if _rag_worker is None:
        _rag_worker = RAGIndexerWorker()
    return _rag_worker


async def start_rag_worker() -> None:
    """Start the RAG indexer worker."""
    worker = get_rag_worker()
    await worker.start()

