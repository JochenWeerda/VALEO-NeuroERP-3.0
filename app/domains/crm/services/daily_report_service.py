"""
CRM Daily Report Service
Generates automated daily reports for field sales activities
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from ....core.database import get_db
from ....infrastructure.models import User
from .models import Activity, VisitReport, Customer, Contact

logger = logging.getLogger(__name__)


class DailyReportService:
    """Service for generating automated daily reports"""

    def __init__(self, db: Session):
        self.db = db

    def generate_daily_reports(self, report_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate daily reports for all active sales reps

        Args:
            report_date: Date for which to generate reports (default: yesterday)

        Returns:
            Dictionary with report data for each sales rep
        """
        if report_date is None:
            report_date = datetime.now() - timedelta(days=1)

        # Get all active sales reps
        sales_reps = self.db.query(User).filter(
            User.is_active == True,
            User.role.in_(['sales', 'field_sales', 'manager'])
        ).all()

        reports = {}
        for rep in sales_reps:
            try:
                report = self._generate_rep_report(rep.id, report_date)
                if report and (report['activities'] or report['visits']):
                    reports[rep.id] = {
                        'sales_rep': rep,
                        'report_date': report_date.date(),
                        'data': report
                    }
            except Exception as e:
                logger.error(f"Error generating report for {rep.username}: {e}")
                continue

        return reports

    def _generate_rep_report(self, sales_rep_id: str, report_date: datetime) -> Optional[Dict[str, Any]]:
        """Generate report for a specific sales rep"""

        # Date range for the report (full day)
        start_date = datetime.combine(report_date.date(), time.min)
        end_date = datetime.combine(report_date.date(), time.max)

        # Get activities for the day
        activities = self.db.query(Activity).filter(
            and_(
                Activity.assigned_to == sales_rep_id,
                Activity.activity_date >= start_date,
                Activity.activity_date <= end_date,
                Activity.status == 'completed'
            )
        ).order_by(Activity.activity_date).all()

        # Get visit reports for the day
        visits = self.db.query(VisitReport).filter(
            and_(
                VisitReport.sales_rep == sales_rep_id,
                VisitReport.visit_date >= start_date,
                VisitReport.visit_date <= end_date
            )
        ).order_by(VisitReport.visit_date).all()

        if not activities and not visits:
            return None

        # Aggregate data
        report_data = {
            'activities': self._format_activities(activities),
            'visits': self._format_visits(visits),
            'summary': self._calculate_summary(activities, visits),
            'route': self._calculate_route(visits),
            'follow_ups': self._extract_follow_ups(activities, visits)
        }

        return report_data

    def _format_activities(self, activities: List[Activity]) -> List[Dict[str, Any]]:
        """Format activities for report"""
        formatted = []

        for activity in activities:
            customer = self.db.query(Customer).filter(Customer.id == activity.customer_id).first()
            contact = None
            if activity.contact_id:
                contact = self.db.query(Contact).filter(Contact.id == activity.contact_id).first()

            formatted.append({
                'time': activity.activity_date.strftime('%H:%M'),
                'type': activity.activity_type,
                'customer': customer.company_name if customer else 'Unbekannt',
                'contact': f"{contact.first_name} {contact.last_name}" if contact else None,
                'subject': activity.subject,
                'description': activity.description,
                'duration': activity.duration_minutes,
                'next_action': activity.next_action_description,
                'next_action_date': activity.next_action_date.isoformat() if activity.next_action_date else None
            })

        return formatted

    def _format_visits(self, visits: List[VisitReport]) -> List[Dict[str, Any]]:
        """Format visit reports for report"""
        formatted = []

        for visit in visits:
            customer = self.db.query(Customer).filter(Customer.id == visit.customer_id).first()
            contact = None
            if visit.contact_person:
                contact = self.db.query(Contact).filter(Contact.id == visit.contact_person).first()

            formatted.append({
                'time': visit.visit_date.strftime('%H:%M'),
                'customer': customer.company_name if customer else 'Unbekannt',
                'contact': f"{contact.first_name} {contact.last_name}" if contact else None,
                'location': visit.location,
                'kilometers': float(visit.kilometers_driven) if visit.kilometers_driven else 0,
                'main_topics': visit.main_topics or [],
                'products_discussed': visit.products_discussed or [],
                'customer_feedback': visit.customer_feedback,
                'sales_opportunities': visit.sales_opportunities or [],
                'orders_placed': visit.orders_placed or [],
                'quotes_created': visit.quotes_created or [],
                'follow_up_actions': visit.follow_up_actions or [],
                'next_visit_date': visit.next_visit_date.isoformat() if visit.next_visit_date else None
            })

        return formatted

    def _calculate_summary(self, activities: List[Activity], visits: List[VisitReport]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total_activities = len(activities)
        total_visits = len(visits)

        # Calculate total time spent
        total_minutes = sum(activity.duration_minutes or 0 for activity in activities)
        total_kilometers = sum(float(visit.kilometers_driven or 0) for visit in visits)

        # Count different activity types
        activity_types = {}
        for activity in activities:
            activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1

        # Extract main topics from visits
        all_topics = []
        all_products = []
        for visit in visits:
            if visit.main_topics:
                all_topics.extend(visit.main_topics)
            if visit.products_discussed:
                all_products.extend(visit.products_discussed)

        # Count orders and quotes
        total_orders = sum(len(visit.orders_placed or []) for visit in visits)
        total_quotes = sum(len(visit.quotes_created or []) for visit in visits)

        return {
            'total_activities': total_activities,
            'total_visits': total_visits,
            'total_time_minutes': total_minutes,
            'total_kilometers': total_kilometers,
            'activity_types': activity_types,
            'main_topics': list(set(all_topics)),
            'products_discussed': list(set(all_products)),
            'orders_placed': total_orders,
            'quotes_created': total_quotes
        }

    def _calculate_route(self, visits: List[VisitReport]) -> List[Dict[str, Any]]:
        """Calculate the route taken during visits"""
        route = []

        for visit in visits:
            customer = self.db.query(Customer).filter(Customer.id == visit.customer_id).first()

            route.append({
                'time': visit.visit_date.strftime('%H:%M'),
                'customer': customer.company_name if customer else 'Unbekannt',
                'location': visit.location,
                'latitude': float(visit.latitude) if visit.latitude else None,
                'longitude': float(visit.longitude) if visit.longitude else None,
                'kilometers': float(visit.kilometers_driven) if visit.kilometers_driven else 0
            })

        return route

    def _extract_follow_ups(self, activities: List[Activity], visits: List[VisitReport]) -> List[Dict[str, Any]]:
        """Extract all follow-up actions"""
        follow_ups = []

        # From activities
        for activity in activities:
            if activity.next_action_description and activity.next_action_date:
                customer = self.db.query(Customer).filter(Customer.id == activity.customer_id).first()
                follow_ups.append({
                    'date': activity.next_action_date.isoformat(),
                    'customer': customer.company_name if customer else 'Unbekannt',
                    'action': activity.next_action_description,
                    'source': 'activity'
                })

        # From visits
        for visit in visits:
            if visit.follow_up_actions:
                customer = self.db.query(Customer).filter(Customer.id == visit.customer_id).first()
                for action in visit.follow_up_actions:
                    follow_ups.append({
                        'date': action.get('due_date'),
                        'customer': customer.company_name if customer else 'Unbekannt',
                        'action': action.get('description'),
                        'source': 'visit'
                    })

            if visit.next_visit_date:
                customer = self.db.query(Customer).filter(Customer.id == visit.customer_id).first()
                follow_ups.append({
                    'date': visit.next_visit_date.isoformat(),
                    'customer': customer.company_name if customer else 'Unbekannt',
                    'action': 'Nächster Besuch',
                    'source': 'visit'
                })

        # Sort by date
        follow_ups.sort(key=lambda x: x['date'] or '9999-99-99')

        return follow_ups

    def format_report_markdown(self, sales_rep_data: Dict[str, Any]) -> str:
        """Format report data as Markdown"""
        rep = sales_rep_data['sales_rep']
        report_date = sales_rep_data['report_date']
        data = sales_rep_data['data']

        summary = data['summary']
        activities = data['activities']
        visits = data['visits']
        route = data['route']
        follow_ups = data['follow_ups']

        # Build markdown report
        lines = []

        # Header
        lines.append(f"# Tagesprotokoll – Außendienst ({rep.first_name} {rep.last_name})")
        lines.append(f"**Datum:** {report_date.strftime('%d.%m.%Y')}")
        lines.append("")

        # Summary
        lines.append("## Zusammenfassung")
        lines.append(f"- **Besuche:** {summary['total_visits']}")
        lines.append(f"- **Aktivitäten:** {summary['total_activities']}")
        lines.append(f"- **Zeit:** {summary['total_time_minutes']} Minuten")
        lines.append(f"- **Kilometer:** {summary['total_kilometers']} km")
        lines.append(f"- **Aufträge:** {summary['orders_placed']}")
        lines.append(f"- **Angebote:** {summary['quotes_created']}")
        lines.append("")

        # Route
        if route:
            lines.append("## Route")
            for stop in route:
                lines.append(f"- **{stop['time']}** - {stop['customer']} ({stop['location'] or 'Keine Adresse'})")
                if stop['kilometers'] > 0:
                    lines.append(f"  - {stop['kilometers']} km gefahren")
            lines.append("")

        # Main topics
        if summary['main_topics']:
            lines.append("## Hauptthemen")
            for topic in summary['main_topics'][:5]:  # Top 5
                lines.append(f"- {topic}")
            lines.append("")

        # Products discussed
        if summary['products_discussed']:
            lines.append("## Besprochene Produkte")
            for product in summary['products_discussed'][:5]:  # Top 5
                lines.append(f"- {product}")
            lines.append("")

        # Activities
        if activities:
            lines.append("## Aktivitäten")
            for activity in activities:
                lines.append(f"### {activity['time']} - {activity['type'].title()}")
                lines.append(f"**Kunde:** {activity['customer']}")
                if activity['contact']:
                    lines.append(f"**Ansprechpartner:** {activity['contact']}")
                lines.append(f"**Betreff:** {activity['subject']}")
                if activity['description']:
                    lines.append(f"**Details:** {activity['description']}")
                if activity['next_action']:
                    lines.append(f"**Nächste Aktion:** {activity['next_action']} ({activity['next_action_date'] or 'Kein Datum'})")
                lines.append("")

        # Visits
        if visits:
            lines.append("## Besuchsberichte")
            for visit in visits:
                lines.append(f"### {visit['time']} - {visit['customer']}")
                if visit['contact']:
                    lines.append(f"**Ansprechpartner:** {visit['contact']}")
                if visit['location']:
                    lines.append(f"**Ort:** {visit['location']}")
                if visit['main_topics']:
                    lines.append(f"**Themen:** {', '.join(visit['main_topics'])}")
                if visit['products_discussed']:
                    lines.append(f"**Produkte:** {', '.join(visit['products_discussed'])}")
                if visit['customer_feedback']:
                    lines.append(f"**Kundenfeedback:** {visit['customer_feedback']}")
                if visit['sales_opportunities']:
                    lines.append("**Verkaufschancen:**")
                    for opp in visit['sales_opportunities']:
                        lines.append(f"  - {opp}")
                if visit['orders_placed']:
                    lines.append("**Aufträge erstellt:**")
                    for order in visit['orders_placed']:
                        lines.append(f"  - {order}")
                if visit['quotes_created']:
                    lines.append("**Angebote erstellt:**")
                    for quote in visit['quotes_created']:
                        lines.append(f"  - {quote}")
                lines.append("")

        # Follow-ups
        if follow_ups:
            lines.append("## Geplante Nachverfolgungen")
            for follow_up in follow_ups[:10]:  # Top 10
                date_str = follow_up['date']
                if date_str:
                    try:
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_str = date_obj.strftime('%d.%m.%Y')
                    except:
                        pass
                lines.append(f"- **{date_str or 'Kein Datum'}** - {follow_up['customer']}: {follow_up['action']}")
            lines.append("")

        return "\n".join(lines)

    def send_daily_reports(self, reports: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send daily reports to sales reps and management

        Args:
            reports: Report data from generate_daily_reports()

        Returns:
            Dictionary with sending results
        """
        results = {}

        for rep_id, report_data in reports.items():
            try:
                # Generate markdown report
                markdown_report = self.format_report_markdown(report_data)

                # Here you would integrate with your notification/email service
                # For now, we'll just log the report
                logger.info(f"Daily report for {report_data['sales_rep'].username}:")
                logger.info(markdown_report)

                # TODO: Send via email, Teams, Telegram, etc.
                # self.email_service.send_report(report_data['sales_rep'].email, markdown_report)
                # self.notification_service.send_to_management(markdown_report)

                results[rep_id] = {
                    'success': True,
                    'report_length': len(markdown_report),
                    'activities_count': len(report_data['data']['activities']),
                    'visits_count': len(report_data['data']['visits'])
                }

            except Exception as e:
                logger.error(f"Error sending report for {rep_id}: {e}")
                results[rep_id] = {
                    'success': False,
                    'error': str(e)
                }

        return results


# Scheduled task function
def generate_daily_reports():
    """Scheduled function to generate and send daily reports"""
    db = next(get_db())

    try:
        service = DailyReportService(db)
        reports = service.generate_daily_reports()

        if reports:
            results = service.send_daily_reports(reports)
            logger.info(f"Generated and sent {len(reports)} daily reports")
            return results
        else:
            logger.info("No daily reports to generate")
            return {}

    except Exception as e:
        logger.error(f"Error in daily report generation: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # For testing
    results = generate_daily_reports()
    print(f"Generated {len(results)} reports")