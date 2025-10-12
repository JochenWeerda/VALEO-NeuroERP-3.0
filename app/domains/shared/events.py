"""
Domain Events Infrastructure
Provides abstract base classes and in-memory stub for event publishing
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Callable, Dict, Type
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    aggregate_id: str
    timestamp: datetime
    event_id: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid4())


class IEventPublisher(ABC):
    """Interface for event publishing."""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        pass


class InMemoryEventPublisher(IEventPublisher):
    """
    In-memory event publisher for Phase 1.
    Logs events and notifies registered handlers.
    Later replaced with NATS/Redis Streams.
    """
    
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
        self._event_log: List[DomainEvent] = []
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish event to in-memory handlers."""
        logger.info(
            f"Event published: {event.__class__.__name__}",
            extra={
                "event_id": event.event_id,
                "aggregate_id": event.aggregate_id,
                "timestamp": event.timestamp.isoformat()
            }
        )
        
        # Store in memory log
        self._event_log.append(event)
        
        # Notify handlers
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}", exc_info=True)
    
    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        """Subscribe to specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type.__name__}")
    
    def get_events(self, limit: int = 100) -> List[DomainEvent]:
        """Get recent events (for debugging)."""
        return self._event_log[-limit:]


# Singleton instance
_event_publisher = InMemoryEventPublisher()


def get_event_publisher() -> IEventPublisher:
    """Get the global event publisher instance."""
    return _event_publisher

