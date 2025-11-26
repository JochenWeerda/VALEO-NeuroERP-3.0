"""Performance aggregation for segments."""

from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Segment, SegmentMember, SegmentPerformance
from app.config.settings import settings


class PerformanceAggregator:
    """Aggregates performance metrics for segments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def aggregate_daily(self, segment_id: UUID, date: datetime | None = None):
        """Aggregate daily performance metrics."""
        if date is None:
            date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        segment = await self.db.get(Segment, segment_id)
        if not segment:
            return
        
        # Count active members
        member_count = await self.db.scalar(
            select(func.count(SegmentMember.id)).where(
                and_(
                    SegmentMember.segment_id == segment_id,
                    SegmentMember.removed_at.is_(None)
                )
            )
        )
        
        # Check if performance record already exists
        existing_stmt = select(SegmentPerformance).where(
            and_(
                SegmentPerformance.segment_id == segment_id,
                SegmentPerformance.date == date,
                SegmentPerformance.period_type == "daily"
            )
        )
        existing = await self.db.scalar(existing_stmt)
        
        if existing:
            existing.member_count = member_count or 0
            existing.active_members = member_count or 0
        else:
            performance = SegmentPerformance(
                segment_id=segment_id,
                date=date,
                period_type="daily",
                member_count=member_count or 0,
                active_members=member_count or 0,
                campaign_count=0,  # TODO: Get from campaigns service
                conversion_rate=None,  # TODO: Calculate from campaign data
                revenue=None  # TODO: Calculate from revenue data
            )
            self.db.add(performance)
        
        await self.db.commit()
    
    async def aggregate_weekly(self, segment_id: UUID, week_start: datetime | None = None):
        """Aggregate weekly performance metrics."""
        if week_start is None:
            today = datetime.utcnow()
            week_start = today - timedelta(days=today.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        segment = await self.db.get(Segment, segment_id)
        if not segment:
            return
        
        # Get daily aggregations for the week
        week_end = week_start + timedelta(days=7)
        daily_stmt = select(SegmentPerformance).where(
            and_(
                SegmentPerformance.segment_id == segment_id,
                SegmentPerformance.date >= week_start,
                SegmentPerformance.date < week_end,
                SegmentPerformance.period_type == "daily"
            )
        )
        daily_result = await self.db.execute(daily_stmt)
        daily_performances = list(daily_result.scalars().all())
        
        if not daily_performances:
            return
        
        # Aggregate
        total_members = sum(p.member_count for p in daily_performances)
        avg_members = total_members / len(daily_performances) if daily_performances else 0
        total_active = sum(p.active_members for p in daily_performances)
        avg_active = total_active / len(daily_performances) if daily_performances else 0
        total_campaigns = sum(p.campaign_count for p in daily_performances)
        total_revenue = sum(p.revenue or 0 for p in daily_performances)
        
        # Calculate conversion rate (if available)
        conversion_rate = None
        if total_campaigns > 0:
            # TODO: Get actual conversions from campaigns service
            pass
        
        # Check if weekly record already exists
        existing_stmt = select(SegmentPerformance).where(
            and_(
                SegmentPerformance.segment_id == segment_id,
                SegmentPerformance.date == week_start,
                SegmentPerformance.period_type == "weekly"
            )
        )
        existing = await self.db.scalar(existing_stmt)
        
        if existing:
            existing.member_count = int(avg_members)
            existing.active_members = int(avg_active)
            existing.campaign_count = total_campaigns
            existing.conversion_rate = conversion_rate
            existing.revenue = total_revenue if total_revenue > 0 else None
        else:
            performance = SegmentPerformance(
                segment_id=segment_id,
                date=week_start,
                period_type="weekly",
                member_count=int(avg_members),
                active_members=int(avg_active),
                campaign_count=total_campaigns,
                conversion_rate=conversion_rate,
                revenue=total_revenue if total_revenue > 0 else None
            )
            self.db.add(performance)
        
        await self.db.commit()
    
    async def aggregate_monthly(self, segment_id: UUID, month_start: datetime | None = None):
        """Aggregate monthly performance metrics."""
        if month_start is None:
            today = datetime.utcnow()
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        segment = await self.db.get(Segment, segment_id)
        if not segment:
            return
        
        # Get daily aggregations for the month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        daily_stmt = select(SegmentPerformance).where(
            and_(
                SegmentPerformance.segment_id == segment_id,
                SegmentPerformance.date >= month_start,
                SegmentPerformance.date < month_end,
                SegmentPerformance.period_type == "daily"
            )
        )
        daily_result = await self.db.execute(daily_stmt)
        daily_performances = list(daily_result.scalars().all())
        
        if not daily_performances:
            return
        
        # Aggregate
        total_members = sum(p.member_count for p in daily_performances)
        avg_members = total_members / len(daily_performances) if daily_performances else 0
        total_active = sum(p.active_members for p in daily_performances)
        avg_active = total_active / len(daily_performances) if daily_performances else 0
        total_campaigns = sum(p.campaign_count for p in daily_performances)
        total_revenue = sum(p.revenue or 0 for p in daily_performances)
        
        # Calculate conversion rate (if available)
        conversion_rate = None
        if total_campaigns > 0:
            # TODO: Get actual conversions from campaigns service
            pass
        
        # Check if monthly record already exists
        existing_stmt = select(SegmentPerformance).where(
            and_(
                SegmentPerformance.segment_id == segment_id,
                SegmentPerformance.date == month_start,
                SegmentPerformance.period_type == "monthly"
            )
        )
        existing = await self.db.scalar(existing_stmt)
        
        if existing:
            existing.member_count = int(avg_members)
            existing.active_members = int(avg_active)
            existing.campaign_count = total_campaigns
            existing.conversion_rate = conversion_rate
            existing.revenue = total_revenue if total_revenue > 0 else None
        else:
            performance = SegmentPerformance(
                segment_id=segment_id,
                date=month_start,
                period_type="monthly",
                member_count=int(avg_members),
                active_members=int(avg_active),
                campaign_count=total_campaigns,
                conversion_rate=conversion_rate,
                revenue=total_revenue if total_revenue > 0 else None
            )
            self.db.add(performance)
        
        await self.db.commit()

