"""
CRM Weekly Report Service
Generates automated weekly reports for sales performance and trends
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, extract

logger = logging.getLogger(__name__)


class WeeklyReportService:
    """Service for generating automated weekly reports"""

    def __init__(self, db: Session):
        self.db = db

    def generate_weekly_reports(self, week_start: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate weekly reports for all sales reps

        Args:
            week_start: Start date of the week (default: last Monday)

        Returns:
            Dictionary with weekly report data
        """
        if week_start is None:
            # Get last Monday
            today = datetime.now()
            days_since_monday = today.weekday()  # 0 = Monday, 6 = Sunday
            week_start = today - timedelta(days=days_since_monday + 7)  # Last Monday

        week_end = week_start + timedelta(days=6)

        # Get all active sales reps
        sales_reps = self.db.query(self.db.query().filter(
            and_(
                self.db.query().c.is_active == True,
                self.db.query().c.role.in_(['sales', 'field_sales', 'manager'])
            )
        )).all()

        reports = {}
        for rep in sales_reps:
            try:
                report = self._generate_rep_weekly_report(rep.id, week_start, week_end)
                if report:
                    reports[rep.id] = {
                        'sales_rep': rep,
                        'week_start': week_start.date(),
                        'week_end': week_end.date(),
                        'data': report
                    }
            except Exception as e:
                logger.error(f"Error generating weekly report for {rep.username}: {e}")
                continue

        return reports

    def _generate_rep_weekly_report(self, sales_rep_id: str, week_start: datetime, week_end: datetime) -> Optional[Dict[str, Any]]:
        """Generate weekly report for a specific sales rep"""

        # Get activities for the week
        activities = self.db.query(self.db.query().filter(
            and_(
                self.db.query().c.assigned_to == sales_rep_id,
                self.db.query().c.activity_date >= week_start,
                self.db.query().c.activity_date <= week_end,
                self.db.query().c.status == 'completed'
            )
        )).order_by(self.db.query().c.activity_date).all()

        # Get visit reports for the week
        visits = self.db.query(self.db.query().filter(
            and_(
                self.db.query().c.sales_rep == sales_rep_id,
                self.db.query().c.visit_date >= week_start,
                self.db.query().c.visit_date <= week_end
            )
        )).order_by(self.db.query().c.visit_date).all()

        if not activities and not visits:
            return None

        # Calculate metrics
        metrics = self._calculate_weekly_metrics(activities, visits, week_start, week_end)

        # Analyze trends
        trends = self._analyze_weekly_trends(activities, visits, sales_rep_id)

        # Generate insights
        insights = self._generate_weekly_insights(metrics, trends)

        return {
            'metrics': metrics,
            'trends': trends,
            'insights': insights,
            'daily_breakdown': self._daily_breakdown(activities, visits, week_start, week_end),
            'top_performers': self._top_performers(activities, visits),
            'challenges': self._identify_challenges(activities, visits)
        }

    def _calculate_weekly_metrics(self, activities: List[Any], visits: List[Any], week_start: datetime, week_end: datetime) -> Dict[str, Any]:
        """Calculate key weekly metrics"""

        # Basic counts
        total_activities = len(activities)
        total_visits = len(visits)

        # Time and distance
        total_minutes = sum(activity.duration_minutes or 0 for activity in activities)
        total_kilometers = sum(float(visit.kilometers_driven or 0) for visit in visits)

        # Activity types
        activity_types = {}
        for activity in activities:
            activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1

        # Visit metrics
        unique_customers = len(set(visit.customer_id for visit in visits))

        # Orders and quotes
        total_orders = sum(len(visit.orders_placed or []) for visit in visits)
        total_quotes = sum(len(visit.quotes_created or []) for visit in visits)

        # Conversion rates
        conversion_rate = (total_orders / max(1, total_quotes)) * 100 if total_quotes > 0 else 0

        # Customer feedback (simplified)
        positive_feedback = sum(1 for visit in visits if visit.customer_feedback and
                               any(word in visit.customer_feedback.lower()
                                   for word in ['gut', 'zufrieden', 'super', 'exzellent']))

        return {
            'total_activities': total_activities,
            'total_visits': total_visits,
            'total_time_minutes': total_minutes,
            'total_kilometers': total_kilometers,
            'unique_customers': unique_customers,
            'activity_types': activity_types,
            'orders_placed': total_orders,
            'quotes_created': total_quotes,
            'conversion_rate': conversion_rate,
            'positive_feedback_count': positive_feedback,
            'avg_activities_per_day': total_activities / 5,  # Business days
            'avg_visits_per_day': total_visits / 5
        }

    def _analyze_weekly_trends(self, activities: List[Any], visits: List[Any], sales_rep_id: str) -> Dict[str, Any]:
        """Analyze trends compared to previous weeks"""

        # Get previous week data for comparison
        prev_week_start = datetime.now() - timedelta(days=14)
        prev_week_end = datetime.now() - timedelta(days=8)

        prev_activities = self.db.query(self.db.query().filter(
            and_(
                self.db.query().c.assigned_to == sales_rep_id,
                self.db.query().c.activity_date >= prev_week_start,
                self.db.query().c.activity_date <= prev_week_end,
                self.db.query().c.status == 'completed'
            )
        )).count()

        prev_visits = self.db.query(self.db.query().filter(
            and_(
                self.db.query().c.sales_rep == sales_rep_id,
                self.db.query().c.visit_date >= prev_week_start,
                self.db.query().c.visit_date <= prev_week_end
            )
        )).count()

        current_activities = len(activities)
        current_visits = len(visits)

        return {
            'activities_change': ((current_activities - prev_activities) / max(1, prev_activities)) * 100,
            'visits_change': ((current_visits - prev_visits) / max(1, prev_visits)) * 100,
            'productivity_trend': 'increasing' if current_activities > prev_activities else 'decreasing',
            'customer_engagement_trend': 'increasing' if current_visits > prev_visits else 'decreasing'
        }

    def _generate_weekly_insights(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights from weekly data"""

        insights = []

        # Activity volume insights
        if metrics['avg_activities_per_day'] > 15:
            insights.append({
                'type': 'high_activity',
                'priority': 'medium',
                'message': f'Starke Aktivität mit {metrics["avg_activities_per_day"]:.1f} Aktivitäten/Tag',
                'recommendation': 'Qualität vor Quantität priorisieren'
            })

        # Conversion insights
        if metrics['conversion_rate'] > 30:
            insights.append({
                'type': 'strong_conversion',
                'priority': 'high',
                'message': f'Hervorragende Conversion-Rate von {metrics["conversion_rate"]:.1f}%',
                'recommendation': 'Erfolgsstrategie analysieren und skalieren'
            })
        elif metrics['conversion_rate'] < 10:
            insights.append({
                'type': 'low_conversion',
                'priority': 'high',
                'message': f'Niedrige Conversion-Rate von {metrics["conversion_rate"]:.1f}%',
                'recommendation': 'Angebotsprozess und Preisstrategie überprüfen'
            })

        # Trend insights
        if trends['activities_change'] > 20:
            insights.append({
                'type': 'activity_increase',
                'priority': 'medium',
                'message': f'Aktivitäten um {trends["activities_change"]:.1f}% gegenüber Vorwoche gestiegen',
                'recommendation': 'Positiven Trend beibehalten'
            })

        # Customer feedback insights
        if metrics['positive_feedback_count'] > metrics['total_visits'] * 0.8:
            insights.append({
                'type': 'excellent_feedback',
                'priority': 'high',
                'message': f'Ausgezeichnete Kundenzufriedenheit ({metrics["positive_feedback_count"]}/{metrics["total_visits"]} positive Bewertungen)',
                'recommendation': 'Erfolgsfaktoren identifizieren und dokumentieren'
            })

        return insights

    def _daily_breakdown(self, activities: List[Any], visits: List[Any], week_start: datetime, week_end: datetime) -> Dict[str, Any]:
        """Break down activities by day"""

        daily_stats = {}
        current_date = week_start

        while current_date <= week_end:
            day_activities = [a for a in activities if a.activity_date.date() == current_date.date()]
            day_visits = [v for v in visits if v.visit_date.date() == current_date.date()]

            daily_stats[current_date.strftime('%A')] = {
                'date': current_date.date(),
                'activities': len(day_activities),
                'visits': len(day_visits),
                'time_minutes': sum(a.duration_minutes or 0 for a in day_activities),
                'kilometers': sum(float(v.kilometers_driven or 0) for v in day_visits)
            }

            current_date += timedelta(days=1)

        return daily_stats

    def _top_performers(self, activities: List[Any], visits: List[Any]) -> Dict[str, Any]:
        """Identify top performing customers and activities"""

        # Top customers by visits
        customer_visits = {}
        for visit in visits:
            customer_visits[visit.customer_id] = customer_visits.get(visit.customer_id, 0) + 1

        top_customers = sorted(customer_visits.items(), key=lambda x: x[1], reverse=True)[:5]

        # Most successful activity types
        activity_success = {}
        for activity in activities:
            # Simplified success metric
            success_score = 1  # Could be enhanced with actual success tracking
            activity_success[activity.activity_type] = activity_success.get(activity.activity_type, 0) + success_score

        top_activities = sorted(activity_success.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'top_customers': top_customers,
            'top_activity_types': top_activities
        }

    def _identify_challenges(self, activities: List[Any], visits: List[Any]) -> List[Dict[str, Any]]:
        """Identify potential challenges and areas for improvement"""

        challenges = []

        # Check for days with no activity
        daily_breakdown = self._daily_breakdown(activities, visits, datetime.now() - timedelta(days=7), datetime.now() - timedelta(days=1))

        inactive_days = [day for day, stats in daily_breakdown.items() if stats['activities'] == 0 and stats['visits'] == 0]
        if inactive_days:
            challenges.append({
                'type': 'inactive_days',
                'severity': 'medium',
                'description': f'Inaktive Tage: {", ".join(inactive_days)}',
                'recommendation': 'Tagesplanung optimieren oder zusätzliche Aufgaben zuweisen'
            })

        # Check for low conversion
        total_quotes = sum(len(visit.quotes_created or []) for visit in visits)
        total_orders = sum(len(visit.orders_placed or []) for visit in visits)

        if total_quotes > 0 and (total_orders / total_quotes) < 0.1:
            challenges.append({
                'type': 'conversion_issues',
                'severity': 'high',
                'description': f'Niedrige Conversion: nur {total_orders}/{total_quotes} Angebote wurden bestellt',
                'recommendation': 'Angebotsprozess und Preisgestaltung überprüfen'
            })

        return challenges

    def format_weekly_report_markdown(self, sales_rep_data: Dict[str, Any]) -> str:
        """Format weekly report as Markdown"""

        rep = sales_rep_data['sales_rep']
        week_start = sales_rep_data['week_start']
        week_end = sales_rep_data['week_end']
        data = sales_rep_data['data']

        metrics = data['metrics']
        trends = data['trends']
        insights = data['insights']

        lines = [
            f"# 📈 Wöchentlicher Verkaufsreport – {rep.first_name} {rep.last_name}",
            f"**Zeitraum:** {week_start} bis {week_end}",
            "",
            "## 📊 Kennzahlen",
            f"- **Aktivitäten:** {metrics['total_activities']} ({metrics['avg_activities_per_day']:.1f}/Tag)",
            f"- **Kundenbesuche:** {metrics['total_visits']} ({metrics['avg_visits_per_day']:.1f}/Tag)",
            f"- **Einzigartige Kunden:** {metrics['unique_customers']}",
            f"- **Zeitaufwand:** {metrics['total_time_minutes']} Minuten",
            f"- **Gefahrene Kilometer:** {metrics['total_kilometers']} km",
            f"- **Aufträge:** {metrics['orders_placed']}",
            f"- **Angebote:** {metrics['quotes_created']}",
            f"- **Conversion-Rate:** {metrics['conversion_rate']:.1f}%",
            "",
            "## 📈 Trends zur Vorwoche",
            f"- **Aktivitäten:** {trends['activities_change']:+.1f}%",
            f"- **Besuche:** {trends['visits_change']:+.1f}%",
            f"- **Produktivität:** {trends['productivity_trend']}",
            f"- **Kundenengagement:** {trends['customer_engagement_trend']}",
            ""
        ]

        if insights:
            lines.extend([
                "## 💡 KI-Insights",
                *[f"- **{insight['type'].replace('_', ' ').title()}:** {insight['message']}" for insight in insights],
                ""
            ])

        return "\n".join(lines)


# Scheduled task function
def generate_weekly_reports():
    """Scheduled function to generate and send weekly reports"""
    from ....core.database import get_db
    from ..services.notification_service import notification_service

    db = next(get_db())

    try:
        service = WeeklyReportService(db)
        reports = service.generate_weekly_reports()

        if reports:
            # Send reports via notification service
            results = {}
            for rep_id, report_data in reports.items():
                markdown_report = service.format_weekly_report_markdown(report_data)

                # Send to management team
                result = notification_service.send_notification(
                    'teams',
                    'management',
                    f'📈 Wöchentlicher Verkaufsreport: {report_data["sales_rep"].first_name} {report_data["sales_rep"].last_name}',
                    markdown_report,
                    'markdown'
                )

                results[rep_id] = {
                    'success': result['success'],
                    'error': result.get('error')
                }

            logger.info(f"Generated and sent {len(reports)} weekly reports")
            return results
        else:
            logger.info("No weekly reports to generate")
            return {}

    except Exception as e:
        logger.error(f"Error in weekly report generation: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # For testing
    results = generate_weekly_reports()
    print(f"Weekly report execution result: {results}")