"""Event publishing for CRM Marketing service."""

from uuid import UUID
from typing import Optional
import httpx
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes domain events for marketing management."""
    
    def __init__(self):
        self.event_bus_url = settings.EVENT_BUS_URL
    
    async def publish_segment_created(
        self,
        segment_id: UUID,
        tenant_id: str,
        segment_name: str,
    ):
        """Publish segment.created event."""
        event = {
            "event_type": "crm.segment.created",
            "segment_id": str(segment_id),
            "tenant_id": tenant_id,
            "segment_name": segment_name,
        }
        await self._publish(event)
    
    async def publish_segment_updated(
        self,
        segment_id: UUID,
        tenant_id: str,
    ):
        """Publish segment.updated event."""
        event = {
            "event_type": "crm.segment.updated",
            "segment_id": str(segment_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_segment_deleted(
        self,
        segment_id: UUID,
        tenant_id: str,
    ):
        """Publish segment.deleted event."""
        event = {
            "event_type": "crm.segment.deleted",
            "segment_id": str(segment_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_segment_calculated(
        self,
        segment_id: UUID,
        tenant_id: str,
        member_count: int,
    ):
        """Publish segment.calculated event."""
        event = {
            "event_type": "crm.segment.calculated",
            "segment_id": str(segment_id),
            "tenant_id": tenant_id,
            "member_count": member_count,
        }
        await self._publish(event)
    
    async def publish_segment_member_added(
        self,
        segment_id: UUID,
        contact_id: UUID,
    ):
        """Publish segment.member_added event."""
        event = {
            "event_type": "crm.segment.member_added",
            "segment_id": str(segment_id),
            "contact_id": str(contact_id),
        }
        await self._publish(event)
    
    async def publish_segment_member_removed(
        self,
        segment_id: UUID,
        contact_id: UUID,
    ):
        """Publish segment.member_removed event."""
        event = {
            "event_type": "crm.segment.member_removed",
            "segment_id": str(segment_id),
            "contact_id": str(contact_id),
        }
        await self._publish(event)
    
    async def publish_campaign_created(
        self,
        campaign_id: UUID,
        tenant_id: str,
        campaign_name: str,
    ):
        """Publish campaign.created event."""
        event = {
            "event_type": "crm.campaign.created",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
            "campaign_name": campaign_name,
        }
        await self._publish(event)
    
    async def publish_campaign_updated(
        self,
        campaign_id: UUID,
        tenant_id: str,
    ):
        """Publish campaign.updated event."""
        event = {
            "event_type": "crm.campaign.updated",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_campaign_deleted(
        self,
        campaign_id: UUID,
        tenant_id: str,
    ):
        """Publish campaign.deleted event."""
        event = {
            "event_type": "crm.campaign.deleted",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_campaign_started(
        self,
        campaign_id: UUID,
        tenant_id: str,
    ):
        """Publish campaign.started event."""
        event = {
            "event_type": "crm.campaign.started",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_campaign_created(
        self,
        campaign_id: UUID,
        tenant_id: str,
        campaign_name: str,
    ):
        """Publish campaign.created event."""
        event = {
            "event_type": "crm.campaign.created",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
            "campaign_name": campaign_name,
        }
        await self._publish(event)
    
    async def publish_campaign_updated(
        self,
        campaign_id: UUID,
        tenant_id: str,
    ):
        """Publish campaign.updated event."""
        event = {
            "event_type": "crm.campaign.updated",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_campaign_deleted(
        self,
        campaign_id: UUID,
        tenant_id: str,
    ):
        """Publish campaign.deleted event."""
        event = {
            "event_type": "crm.campaign.deleted",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_campaign_started(
        self,
        campaign_id: UUID,
        tenant_id: str,
    ):
        """Publish campaign.started event."""
        event = {
            "event_type": "crm.campaign.started",
            "campaign_id": str(campaign_id),
            "tenant_id": tenant_id,
        }
        await self._publish(event)
    
    async def publish_campaign_event(
        self,
        campaign_id: UUID,
        event_type: str,
        recipient_id: UUID | None = None,
    ):
        """Publish campaign event (sent, opened, clicked, etc.)."""
        event = {
            "event_type": f"crm.campaign.{event_type}",
            "campaign_id": str(campaign_id),
            "recipient_id": str(recipient_id) if recipient_id else None,
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

