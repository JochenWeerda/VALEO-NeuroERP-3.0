"""Email sender service for campaigns."""

from uuid import UUID
from typing import Dict, Any
import httpx
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Campaign, CampaignTemplate, CampaignRecipient, CampaignEvent, CampaignType, CampaignEventType, RecipientStatus
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailSender:
    """Sends emails for campaigns."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.smtp_host = "localhost"  # TODO: Get from config
        self.smtp_port = 587
        self.smtp_user = None  # TODO: Get from config
        self.smtp_password = None  # TODO: Get from config
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str,
        from_name: str | None = None,
    ) -> bool:
        """Send email via SMTP or email service."""
        # TODO: Implement actual email sending
        # For now, just log
        logger.info(f"Sending email to {to_email}: {subject}")
        return True
    
    async def send_campaign_email(
        self,
        campaign: Campaign,
        recipient: CampaignRecipient,
        template: CampaignTemplate | None = None,
        variant: str | None = None,
    ) -> bool:
        """Send email for a campaign recipient."""
        # Get template
        if not template:
            if campaign.template_id:
                template = await self.db.get(CampaignTemplate, campaign.template_id)
            else:
                logger.error(f"No template for campaign {campaign.id}")
                return False
        
        # Get subject and body
        subject = campaign.subject or template.subject_template or ""
        body = template.body_template
        
        # Render template with variables
        variables = {
            "contact_name": "Contact",  # TODO: Get from contact
            "campaign_name": campaign.name,
            "unsubscribe_url": f"https://example.com/unsubscribe?token={recipient.id}",  # TODO: Generate token
        }
        
        # If A/B-Test variant, use variant content
        if variant and campaign.settings and campaign.settings.get("ab_test_enabled"):
            # TODO: Get variant content from CampaignABTest
            pass
        
        subject = self._render_template(subject, variables)
        body = self._render_template(body, variables)
        
        # Add tracking pixel for opens
        tracking_pixel = f'<img src="https://example.com/track/open?campaign_id={campaign.id}&recipient_id={recipient.id}" width="1" height="1" style="display:none;" />'
        body = body.replace("</body>", f"{tracking_pixel}</body>")
        
        # Wrap links for click tracking
        # TODO: Implement link wrapping
        
        # Send email
        success = await self._send_email(
            to_email=recipient.email or "",
            subject=subject,
            body=body,
            from_email=campaign.sender_email or "noreply@example.com",
            from_name=campaign.sender_name,
        )
        
        if success:
            # Update recipient status
            recipient.status = RecipientStatus.SENT
            recipient.sent_at = datetime.utcnow()
            
            # Create sent event
            event = CampaignEvent(
                campaign_id=campaign.id,
                recipient_id=recipient.id,
                event_type=CampaignEventType.SENT,
            )
            self.db.add(event)
            
            await self.db.commit()
        
        return success
    
    async def send_batch(
        self,
        campaign_id: UUID,
        batch_size: int = 100,
    ):
        """Send emails in batches for a campaign."""
        campaign = await self.db.get(Campaign, campaign_id)
        if not campaign or campaign.type != CampaignType.EMAIL:
            return
        
        # Get pending recipients
        from sqlalchemy import select, and_
        stmt = select(CampaignRecipient).where(
            and_(
                CampaignRecipient.campaign_id == campaign_id,
                CampaignRecipient.status == RecipientStatus.PENDING
            )
        ).limit(batch_size)
        
        result = await self.db.execute(stmt)
        recipients = list(result.scalars().all())
        
        # Get template
        template = None
        if campaign.template_id:
            template = await self.db.get(CampaignTemplate, campaign.template_id)
        
        # Send to each recipient
        for recipient in recipients:
            await self.send_campaign_email(
                campaign=campaign,
                recipient=recipient,
                template=template,
            )

