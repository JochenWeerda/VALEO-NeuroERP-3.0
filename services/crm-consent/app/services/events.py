"""Event publishing for CRM Consent service."""

from uuid import UUID
from typing import Optional
import httpx
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes domain events for consent management."""
    
    def __init__(self):
        self.event_bus_url = settings.EVENT_BUS_URL
    
    async def publish_consent_created(
        self,
        consent_id: UUID,
        tenant_id: str,
        contact_id: UUID,
        channel: str,
        consent_type: str,
    ):
        """Publish consent.created event."""
        event = {
            "event_type": "crm.consent.created",
            "consent_id": str(consent_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
            "channel": channel,
            "consent_type": consent_type,
        }
        await self._publish(event)
    
    async def publish_consent_confirmed(
        self,
        consent_id: UUID,
        tenant_id: str,
        contact_id: UUID,
        channel: str,
    ):
        """Publish consent.confirmed event (double opt-in)."""
        event = {
            "event_type": "crm.consent.confirmed",
            "consent_id": str(consent_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
            "channel": channel,
        }
        await self._publish(event)
    
    async def publish_consent_revoked(
        self,
        consent_id: UUID,
        tenant_id: str,
        contact_id: UUID,
        channel: str,
        reason: Optional[str] = None,
    ):
        """Publish consent.revoked event."""
        event = {
            "event_type": "crm.consent.revoked",
            "consent_id": str(consent_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
            "channel": channel,
            "reason": reason,
        }
        await self._publish(event)
    
    async def publish_consent_updated(
        self,
        consent_id: UUID,
        tenant_id: str,
        contact_id: UUID,
        old_status: str,
        new_status: str,
    ):
        """Publish consent.updated event."""
        event = {
            "event_type": "crm.consent.updated",
            "consent_id": str(consent_id),
            "tenant_id": tenant_id,
            "contact_id": str(contact_id),
            "old_status": old_status,
            "new_status": new_status,
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

