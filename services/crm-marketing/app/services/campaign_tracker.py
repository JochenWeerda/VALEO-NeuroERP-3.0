"""Campaign tracking service."""

from uuid import UUID
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Campaign, CampaignRecipient, CampaignEvent, CampaignEventType, RecipientStatus
from app.services.events import get_event_publisher


class CampaignTracker:
    """Tracks campaign events (opens, clicks, conversions)."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def track_open(
        self,
        campaign_id: UUID,
        recipient_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ):
        """Track email open."""
        # Check if already tracked
        existing = await self.db.scalar(
            select(CampaignEvent).where(
                and_(
                    CampaignEvent.campaign_id == campaign_id,
                    CampaignEvent.recipient_id == recipient_id,
                    CampaignEvent.event_type == CampaignEventType.OPENED
                )
            )
        )
        
        if existing:
            return  # Already tracked
        
        # Create event
        event = CampaignEvent(
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            event_type=CampaignEventType.OPENED,
            details={
                "user_agent": user_agent,
            },
            ip_address=ip_address,
        )
        
        self.db.add(event)
        await self.db.commit()
        
        # Publish event
        event_publisher = get_event_publisher()
        await event_publisher.publish_campaign_event(
            campaign_id=campaign_id,
            event_type="email.opened",
            recipient_id=recipient_id,
        )
    
    async def track_click(
        self,
        campaign_id: UUID,
        recipient_id: UUID,
        link_url: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ):
        """Track link click."""
        # Create event
        event = CampaignEvent(
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            event_type=CampaignEventType.CLICKED,
            details={
                "link_url": link_url,
                "user_agent": user_agent,
            },
            ip_address=ip_address,
        )
        
        self.db.add(event)
        await self.db.commit()
        
        # Publish event
        event_publisher = get_event_publisher()
        await event_publisher.publish_campaign_event(
            campaign_id=campaign_id,
            event_type="email.clicked",
            recipient_id=recipient_id,
        )
    
    async def track_conversion(
        self,
        campaign_id: UUID,
        recipient_id: UUID,
        conversion_type: str,
        conversion_value: float | None = None,
        details: Dict[str, Any] | None = None,
    ):
        """Track conversion."""
        # Create event
        event = CampaignEvent(
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            event_type=CampaignEventType.CONVERTED,
            details={
                "conversion_type": conversion_type,
                "conversion_value": conversion_value,
                **(details or {}),
            },
        )
        
        self.db.add(event)
        await self.db.commit()
        
        # Publish event
        event_publisher = get_event_publisher()
        await event_publisher.publish_campaign_event(
            campaign_id=campaign_id,
            event_type="converted",
            recipient_id=recipient_id,
        )
    
    async def track_bounce(
        self,
        campaign_id: UUID,
        recipient_id: UUID,
        bounce_reason: str,
    ):
        """Track email bounce."""
        recipient = await self.db.get(CampaignRecipient, recipient_id)
        if recipient:
            recipient.status = RecipientStatus.BOUNCED
            recipient.bounce_reason = bounce_reason
        
        # Create event
        event = CampaignEvent(
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            event_type=CampaignEventType.BOUNCED,
            details={
                "bounce_reason": bounce_reason,
            },
        )
        
        self.db.add(event)
        await self.db.commit()
        
        # Publish event
        event_publisher = get_event_publisher()
        await event_publisher.publish_campaign_event(
            campaign_id=campaign_id,
            event_type="bounced",
            recipient_id=recipient_id,
        )
    
    async def track_unsubscribe(
        self,
        campaign_id: UUID,
        recipient_id: UUID,
    ):
        """Track unsubscribe."""
        # Create event
        event = CampaignEvent(
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            event_type=CampaignEventType.UNSUBSCRIBED,
        )
        
        self.db.add(event)
        await self.db.commit()
        
        # Publish event
        event_publisher = get_event_publisher()
        await event_publisher.publish_campaign_event(
            campaign_id=campaign_id,
            event_type="unsubscribed",
            recipient_id=recipient_id,
        )

