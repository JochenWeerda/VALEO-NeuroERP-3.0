"""
Outbox Pattern Implementation
Ensures reliable event publishing using transactional outbox
"""

import logging
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

from ...domains.shared.events import DomainEvent

logger = logging.getLogger(__name__)

Base = declarative_base()


class OutboxEvent(Base):
    """
    Outbox table for storing events before publishing.
    Ensures events are persisted transactionally with domain changes.
    """
    __tablename__ = "outbox_events"
    
    id = Column(String, primary_key=True)
    event_type = Column(String(200), nullable=False)
    aggregate_id = Column(String(50), nullable=False)
    payload = Column(Text, nullable=False)  # JSON
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    tenant_id = Column(String(50), nullable=True)


class OutboxPublisher:
    """
    Outbox-based event publisher.
    Stores events in DB first, then publishes asynchronously.
    """
    
    def __init__(self, db_session: Session, event_publisher):
        self.db = db_session
        self.event_publisher = event_publisher
    
    async def store_event(self, event: DomainEvent, tenant_id: Optional[str] = None) -> None:
        """Store event in outbox table (transactional)."""
        from dataclasses import asdict
        
        outbox_event = OutboxEvent(
            id=event.event_id,
            event_type=event.__class__.__name__,
            aggregate_id=event.aggregate_id,
            payload=json.dumps(asdict(event), default=str),
            timestamp=event.timestamp,
            published=False,
            tenant_id=tenant_id
        )
        
        self.db.add(outbox_event)
        # Committed with main transaction
        
        logger.debug(f"Event stored in outbox: {event.__class__.__name__}")
    
    async def publish_pending_events(self, limit: int = 100) -> int:
        """
        Publish pending events from outbox.
        Called by background worker.
        """
        pending = (
            self.db.query(OutboxEvent)
            .filter(OutboxEvent.published == False)  # noqa: E712
            .order_by(OutboxEvent.timestamp)
            .limit(limit)
            .all()
        )
        
        published_count = 0
        
        for outbox_event in pending:
            try:
                # Deserialize and publish
                payload = json.loads(outbox_event.payload)
                
                # Recreate event object (simplified - just log for now)
                await self.event_publisher.publish(
                    type(outbox_event.event_type, (DomainEvent,), payload)
                )
                
                # Mark as published
                outbox_event.published = True
                outbox_event.published_at = datetime.utcnow()
                published_count += 1
                
            except Exception as e:
                logger.error(
                    f"Failed to publish event {outbox_event.id}: {e}",
                    exc_info=True
                )
                outbox_event.retry_count += 1
                
                # Give up after 3 retries
                if outbox_event.retry_count >= 3:
                    outbox_event.published = True
                    logger.error(f"Gave up on event {outbox_event.id} after 3 retries")
        
        self.db.commit()
        
        logger.info(f"Published {published_count} events from outbox")
        return published_count
    
    async def cleanup_old_events(self, days: int = 30) -> int:
        """Delete published events older than X days."""
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        deleted = (
            self.db.query(OutboxEvent)
            .filter(
                OutboxEvent.published == True,  # noqa: E712
                OutboxEvent.published_at < cutoff
            )
            .delete()
        )
        
        self.db.commit()
        
        logger.info(f"Cleaned up {deleted} old outbox events")
        return deleted

