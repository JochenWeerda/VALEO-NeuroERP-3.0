"""A/B-Testing service for campaigns."""

from uuid import UUID
from typing import List
import random
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Campaign, CampaignABTest, CampaignRecipient, CampaignEvent, CampaignEventType


class ABTesting:
    """A/B-Testing logic for campaigns."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def assign_variant(
        self,
        campaign: Campaign,
        recipient_id: UUID,
    ) -> str:
        """Assign A/B-Test variant to a recipient."""
        if not campaign.settings or not campaign.settings.get("ab_test_enabled"):
            return "A"  # Default variant
        
        # Get variants
        variants_stmt = select(CampaignABTest).where(
            CampaignABTest.campaign_id == campaign.id
        )
        variants_result = await self.db.execute(variants_stmt)
        variants = list(variants_result.scalars().all())
        
        if not variants:
            return "A"  # Default variant
        
        # Calculate distribution (equal split by default)
        variant_names = [v.variant_name for v in variants]
        
        # Random assignment
        assigned_variant = random.choice(variant_names)
        
        # Update recipient
        recipient = await self.db.get(CampaignRecipient, recipient_id)
        if recipient:
            recipient.variant = assigned_variant
            await self.db.commit()
        
        return assigned_variant
    
    async def calculate_variant_performance(
        self,
        campaign_id: UUID,
    ) -> List[Dict]:
        """Calculate performance metrics for each variant."""
        # Get variants
        variants_stmt = select(CampaignABTest).where(
            CampaignABTest.campaign_id == campaign_id
        )
        variants_result = await self.db.execute(variants_stmt)
        variants = list(variants_result.scalars().all())
        
        results = []
        
        for variant in variants:
            # Count recipients
            recipient_count = await self.db.scalar(
                select(func.count(CampaignRecipient.id)).where(
                    and_(
                        CampaignRecipient.campaign_id == campaign_id,
                        CampaignRecipient.variant == variant.variant_name
                    )
                )
            ) or 0
            
            # Count opens
            opened = await self.db.scalar(
                select(func.count(CampaignEvent.id)).where(
                    and_(
                        CampaignEvent.campaign_id == campaign_id,
                        CampaignEvent.event_type == CampaignEventType.OPENED,
                        CampaignEvent.recipient_id.in_(
                            select(CampaignRecipient.id).where(
                                and_(
                                    CampaignRecipient.campaign_id == campaign_id,
                                    CampaignRecipient.variant == variant.variant_name
                                )
                            )
                        )
                    )
                )
            ) or 0
            
            # Count clicks
            clicked = await self.db.scalar(
                select(func.count(CampaignEvent.id)).where(
                    and_(
                        CampaignEvent.campaign_id == campaign_id,
                        CampaignEvent.event_type == CampaignEventType.CLICKED,
                        CampaignEvent.recipient_id.in_(
                            select(CampaignRecipient.id).where(
                                and_(
                                    CampaignRecipient.campaign_id == campaign_id,
                                    CampaignRecipient.variant == variant.variant_name
                                )
                            )
                        )
                    )
                )
            ) or 0
            
            # Count conversions
            converted = await self.db.scalar(
                select(func.count(CampaignEvent.id)).where(
                    and_(
                        CampaignEvent.campaign_id == campaign_id,
                        CampaignEvent.event_type == CampaignEventType.CONVERTED,
                        CampaignEvent.recipient_id.in_(
                            select(CampaignRecipient.id).where(
                                and_(
                                    CampaignRecipient.campaign_id == campaign_id,
                                    CampaignRecipient.variant == variant.variant_name
                                )
                            )
                        )
                    )
                )
            ) or 0
            
            # Calculate rates
            open_rate = (opened / recipient_count * 100) if recipient_count > 0 else 0.0
            click_rate = (clicked / recipient_count * 100) if recipient_count > 0 else 0.0
            conversion_rate = (converted / recipient_count * 100) if recipient_count > 0 else 0.0
            
            # Update variant
            variant.recipient_count = recipient_count
            variant.open_rate = round(open_rate, 2)
            variant.click_rate = round(click_rate, 2)
            variant.conversion_rate = round(conversion_rate, 2)
            
            results.append({
                "variant_name": variant.variant_name,
                "recipient_count": recipient_count,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "conversion_rate": round(conversion_rate, 2),
            })
        
        await self.db.commit()
        
        return results
    
    async def get_winner(
        self,
        campaign_id: UUID,
        metric: str = "conversion_rate",  # conversion_rate, click_rate, open_rate
    ) -> str | None:
        """Get the winning variant based on metric."""
        performance = await self.calculate_variant_performance(campaign_id)
        
        if not performance:
            return None
        
        # Sort by metric
        sorted_performance = sorted(
            performance,
            key=lambda x: x.get(metric, 0),
            reverse=True
        )
        
        winner = sorted_performance[0]
        return winner.get("variant_name")

