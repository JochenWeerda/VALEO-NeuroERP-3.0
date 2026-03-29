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
            from sqlalchemy import text

            indexer = get_indexer()

            tenant_rows = db.execute(
                text("SELECT DISTINCT tenant_id FROM domain_shared.tenants WHERE active = true LIMIT 50")
            ).fetchall()
            tenant_ids = [r.tenant_id for r in tenant_rows] if tenant_rows else ["system"]

            total_articles = 0
            total_customers = 0
            for tenant_id in tenant_ids:
                article_count = await indexer.index_articles(db, tenant_id)
                customer_count = await indexer.index_customers(db, tenant_id)
                total_articles += article_count
                total_customers += customer_count
                logger.debug("Tenant %s: %d articles, %d customers", tenant_id, article_count, customer_count)

            self.last_sync = datetime.utcnow()

            logger.info(
                "RAG indexing complete: %d tenants, %d articles, %d customers",
                len(tenant_ids), total_articles, total_customers,
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

