"""
Outbox Pattern Implementation
Ensures reliable event publishing using transactional outbox.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session

from app.core.database import Base
from ...domains.shared.events import DomainEvent, IntegrationEvent

logger = logging.getLogger(__name__)


class OutboxEvent(Base):
    """Outbox table for storing events before asynchronous publishing."""

    __tablename__ = "outbox_events"

    id = Column(String, primary_key=True)
    event_type = Column(String(200), nullable=False)
    aggregate_id = Column(String(100), nullable=False)
    payload = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    tenant_id = Column(String(50), nullable=True)


class OutboxPublisher:
    """Outbox-based event publisher utility."""

    def __init__(self, db_session: Session, event_publisher):
        self.db = db_session
        self.event_publisher = event_publisher

    async def store_event(self, event: DomainEvent, tenant_id: Optional[str] = None) -> None:
        """Store event in outbox table (same DB transaction as caller)."""
        from dataclasses import asdict

        event_dict = asdict(event)
        outbox_event = OutboxEvent(
            id=event.event_id,
            event_type=getattr(event, "event_type", event.__class__.__name__),
            aggregate_id=event.aggregate_id,
            payload=json.dumps(event_dict, default=str),
            timestamp=event.timestamp,
            published=False,
            tenant_id=tenant_id,
        )
        self.db.add(outbox_event)
        logger.debug("Event stored in outbox: %s", outbox_event.event_type)

    async def publish_pending_events(self, limit: int = 100) -> int:
        """Publish pending outbox events and mark successful entries as published."""
        pending = (
            self.db.query(OutboxEvent)
            .filter(OutboxEvent.published == False)  # noqa: E712
            .order_by(OutboxEvent.timestamp)
            .limit(limit)
            .all()
        )

        published_count = 0
        for entry in pending:
            try:
                payload = json.loads(entry.payload)
                event = IntegrationEvent(
                    aggregate_id=payload.get("aggregate_id") or entry.aggregate_id,
                    timestamp=datetime.fromisoformat(payload["timestamp"]) if isinstance(payload.get("timestamp"), str) else entry.timestamp,
                    event_id=payload.get("event_id") or entry.id,
                    event_type=entry.event_type,
                    payload=payload.get("payload") if isinstance(payload.get("payload"), dict) else payload,
                )

                await self.event_publisher.publish(event)
                entry.published = True
                entry.published_at = datetime.utcnow()
                published_count += 1
            except Exception as exc:
                logger.error("Failed to publish outbox event %s: %s", entry.id, exc, exc_info=True)
                entry.retry_count += 1
                if entry.retry_count >= 3:
                    entry.published = True
                    entry.published_at = datetime.utcnow()
                    logger.error("Marked outbox event %s as failed after 3 retries", entry.id)

        self.db.commit()
        if published_count:
            logger.info("Published %s event(s) from outbox", published_count)
        return published_count

    async def cleanup_old_events(self, days: int = 30) -> int:
        """Delete published events older than the retention window."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = (
            self.db.query(OutboxEvent)
            .filter(OutboxEvent.published == True, OutboxEvent.published_at < cutoff)  # noqa: E712
            .delete()
        )
        self.db.commit()
        logger.info("Cleaned up %s old outbox event(s)", deleted)
        return deleted
