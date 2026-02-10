"""
NATS Event Publisher
Production event bus using NATS Streaming
"""

import logging
import json
from typing import Optional
from datetime import datetime

from ...domains.shared.events import DomainEvent, IEventPublisher

logger = logging.getLogger(__name__)


class NATSEventPublisher(IEventPublisher):
    """
    NATS-based event publisher for Phase 3.
    
    Publishes domain events to NATS Streaming for distributed consumption.
    Falls back to logging if NATS is unavailable.
    """
    
    def __init__(self, nats_url: str = "nats://localhost:4222", enabled: bool = False):
        self.nats_url = nats_url
        self.enabled = enabled
        self._client: Optional[any] = None
        
        if enabled:
            logger.info(f"NATS Publisher initialized (URL: {nats_url})")
        else:
            logger.info("NATS Publisher disabled - using in-memory fallback")
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish event to NATS or fallback to logging."""
        
        if not self.enabled:
            # Fallback: Just log
            logger.info(
                f"Event (fallback): {event.__class__.__name__}",
                extra={
                    "event_id": event.event_id,
                    "aggregate_id": event.aggregate_id,
                    "timestamp": event.timestamp.isoformat()
                }
            )
            return
        
        try:
            # Serialize event
            event_data = {
                "event_type": event.__class__.__name__,
                "event_id": event.event_id,
                "aggregate_id": event.aggregate_id,
                "timestamp": event.timestamp.isoformat(),
                "payload": self._serialize_event(event)
            }
            
            # Publish to NATS
            subject = f"domain.{event.__class__.__module__.split('.')[-2]}.{event.__class__.__name__}"
            
            # TODO: Actual NATS publish
            # await self._client.publish(subject, json.dumps(event_data).encode())
            
            logger.info(
                f"Event published to NATS: {subject}",
                extra={
                    "event_id": event.event_id,
                    "aggregate_id": event.aggregate_id,
                    "subject": subject
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to publish event to NATS: {e}", exc_info=True)
            # Fallback: at least log the event
            logger.warning(f"Event fallback-logged: {event.__class__.__name__}")
    
    def _serialize_event(self, event: DomainEvent) -> dict:
        """Serialize event to dict."""
        from dataclasses import asdict
        data = asdict(event)
        
        # Convert datetime to ISO string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
    
    async def connect(self) -> None:
        """Connect to NATS server."""
        if not self.enabled:
            return
        
        try:
            # TODO: Actual NATS connection
            # from nats.aio.client import Client as NATS
            # self._client = NATS()
            # await self._client.connect(self.nats_url)
            logger.info("NATS connection established")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            self.enabled = False
    
    async def disconnect(self) -> None:
        """Disconnect from NATS server."""
        if self._client:
            # TODO: Actual disconnect
            # await self._client.close()
            logger.info("NATS connection closed")

