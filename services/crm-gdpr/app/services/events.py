"""Event publishing for CRM GDPR service."""

from uuid import UUID
from typing import Optional
import httpx
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes domain events for GDPR management."""
    
    def __init__(self):
        self.event_bus_url = settings.EVENT_BUS_URL
    
    async def publish_gdpr_request_created(
        self,
        request_id: UUID,
        tenant_id: str,
        contact_id: UUID,
        request_type: str,
    ):
        """Publish gdpr.request.created event."""
        event = {
            "event_type": "crm.gdpr.request.created",
            "request_id": str(request_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
            "request_type": request_type,
        }
        await self._publish(event)
    
    async def publish_gdpr_request_verified(
        self,
        request_id: UUID,
        tenant_id: str,
        contact_id: UUID,
    ):
        """Publish gdpr.request.verified event."""
        event = {
            "event_type": "crm.gdpr.request.verified",
            "request_id": str(request_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
        }
        await self._publish(event)
    
    async def publish_gdpr_request_exported(
        self,
        request_id: UUID,
        tenant_id: str,
        contact_id: UUID,
    ):
        """Publish gdpr.request.exported event."""
        event = {
            "event_type": "crm.gdpr.request.exported",
            "request_id": str(request_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
        }
        await self._publish(event)
    
    async def publish_gdpr_request_deleted(
        self,
        request_id: UUID,
        tenant_id: str,
        contact_id: UUID,
    ):
        """Publish gdpr.request.deleted event."""
        event = {
            "event_type": "crm.gdpr.request.deleted",
            "request_id": str(request_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
        }
        await self._publish(event)
    
    async def publish_gdpr_request_rejected(
        self,
        request_id: UUID,
        tenant_id: str,
        contact_id: UUID,
        reason: str,
    ):
        """Publish gdpr.request.rejected event."""
        event = {
            "event_type": "crm.gdpr.request.rejected",
            "request_id": str(request_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
            "reason": reason,
        }
        await self._publish(event)
    
    async def _publish(self, event: dict):
        """Publish event to event bus."""
        if not self.event_bus_url:
            logger.debug(f"Event bus not configured, skipping event: {event['event_type']}")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.event_bus_url}/events",
                    json=event,
                    timeout=5.0,
                )
            logger.info(f"Published event: {event['event_type']}")
        except Exception as e:
            logger.error(f"Failed to publish event {event['event_type']}: {e}")


def get_event_publisher() -> EventPublisher:
    """Get event publisher instance."""
    return EventPublisher()

