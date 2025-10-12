"""
Outbox Publisher Background Worker
Periodically publishes pending events from outbox table
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..infrastructure.eventbus.outbox import OutboxPublisher
from ..domains.shared.events import get_event_publisher

logger = logging.getLogger(__name__)


class OutboxPublisherWorker:
    """Background worker to publish outbox events."""
    
    def __init__(self, interval_seconds: int = 5):
        self.interval = interval_seconds
        self.running = False
    
    async def start(self) -> None:
        """Start the outbox publisher worker."""
        self.running = True
        logger.info(f"Outbox publisher worker started (interval: {self.interval}s)")
        
        while self.running:
            try:
                await self._publish_batch()
            except Exception as e:
                logger.error(f"Outbox publisher error: {e}", exc_info=True)
            
            await asyncio.sleep(self.interval)
        
        logger.info("Outbox publisher worker stopped")
    
    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
    
    async def _publish_batch(self) -> None:
        """Publish a batch of pending events."""
        db: Session = SessionLocal()
        
        try:
            event_publisher = get_event_publisher()
            outbox = OutboxPublisher(db, event_publisher)
            
            count = await outbox.publish_pending_events(limit=100)
            
            if count > 0:
                logger.info(f"Published {count} events from outbox")
        
        finally:
            db.close()


# Global worker instance
_outbox_worker: Optional[OutboxPublisherWorker] = None


def get_outbox_worker() -> OutboxPublisherWorker:
    """Get the global outbox worker instance."""
    global _outbox_worker
    if _outbox_worker is None:
        _outbox_worker = OutboxPublisherWorker()
    return _outbox_worker


async def start_outbox_worker() -> None:
    """Start the global outbox worker."""
    worker = get_outbox_worker()
    await worker.start()


async def stop_outbox_worker() -> None:
    """Stop the global outbox worker."""
    worker = get_outbox_worker()
    await worker.stop()

