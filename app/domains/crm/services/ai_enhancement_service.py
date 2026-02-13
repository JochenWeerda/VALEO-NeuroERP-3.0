"""
CRM AI Enhancement Service
AI-powered features for CRM: sentiment analysis, follow-up suggestions, report insights
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

logger = logging.getLogger(__name__)


class AIEnhancementService:
    """AI-powered CRM enhancements"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of customer feedback text

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis results
        """
        # Simple rule-based sentiment analysis (can be enhanced with ML models)
        positive_words = [
            'zufrieden', 'gut', 'super', 'exzellent', 'perfekt', 'toll', 'freue',
            'danke', 'lob', 'positiv', 'erfolgreich', 'zufriedenstellend', 'angenehm'
        ]

        negative_words = [
            'unzufrieden', 'schlecht', 'enttäuscht', 'ärgerlich', 'problem', 'fehler',
            'beschwerde', 'reklamation', 'verärgert', 'frustrierend', 'negativ', 'schwierig'
        ]

        neutral_words = [
            'ok', 'normal', 'durchschnittlich', 'standard', 'gewöhnlich', 'üblich'
        ]

        text_lower = text.lower()

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        neutral_score = sum(1 for word in neutral_words if word in text_lower)

        total_score = positive_score - negative_score

        if total_score > 0:
            sentiment = 'positive'
            confidence = min(0.9, positive_score / max(1, positive_score + negative_score + neutral_score))
        elif total_score < 0:
            sentiment = 'negative'
            confidence = min(0.9, negative_score / max(1, positive_score + negative_score + neutral_score))
        else:
            sentiment = 'neutral'
            confidence = 0.5

        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {
                'positive': positive_score,
                'negative': negative_score,
                'neutral': neutral_score
            },
            'keywords': self._extract_keywords(text)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Product-related keywords
        product_keywords = [
            'dünger', 'saatgut', 'psm', 'pflanzenschutz', 'futtermittel',
            'getreide', 'mais', 'raps', 'weizen', 'gerste', 'protein',
            'mineralstoff', 'biostimulanzien', 'preis', 'qualität'
        ]

        # Action keywords
        action_keywords = [
            'bestellung', 'lieferung', 'angebot', 'reklamation', 'support',
            'beratung', 'besuch', 'anruf', 'email', 'termin'
        ]

        text_lower = text.lower()
        keywords = []

        for keyword in product_keywords + action_keywords:
            if keyword in text_lower:
                keywords.append(keyword)

        return list(set(keywords))  # Remove duplicates

    def suggest_follow_ups(self, activity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest follow-up actions based on activity data

        Args:
            activity_data: Activity information

        Returns:
            List of suggested follow-up actions
        """
        suggestions = []
        activity_type = activity_data.get('activity_type', '')
        description = activity_data.get('description', '').lower()
        customer_id = activity_data.get('customer_id')

        # Get customer information for context
        customer = self.db.query(self.db.query().filter_by(id=customer_id).first()) if customer_id else None

        # Analyze activity content for suggestions
        if 'angebot' in description or 'offer' in description:
            suggestions.append({
                'action': 'Angebot nachfassen',
                'description': 'Überprüfen ob Angebot angenommen wurde',
                'priority': 'high',
                'suggested_date': datetime.now() + timedelta(days=7),
                'reason': 'Angebote sollten innerhalb 1-2 Wochen nachverfolgt werden'
            })

        if 'reklamation' in description or 'complaint' in description or 'problem' in description:
            suggestions.append({
                'action': 'Reklamation lösen',
                'description': 'Kundenproblem lösen und Feedback einholen',
                'priority': 'urgent',
                'suggested_date': datetime.now() + timedelta(days=1),
                'reason': 'Reklamationen sollten schnell bearbeitet werden'
            })

        if 'besuch' in activity_type or 'visit' in activity_type:
            suggestions.append({
                'action': 'Besuchsfolge durchführen',
                'description': 'Vereinbarte Maßnahmen aus Besuchsprotokoll umsetzen',
                'priority': 'medium',
                'suggested_date': datetime.now() + timedelta(days=3),
                'reason': 'Besuchsvereinbarungen sollten zeitnah umgesetzt werden'
            })

        if 'preis' in description or 'price' in description:
            suggestions.append({
                'action': 'Preisverhandlung führen',
                'description': 'Preisdiskussion fortführen und Konditionen klären',
                'priority': 'medium',
                'suggested_date': datetime.now() + timedelta(days=5),
                'reason': 'Preisgespräche sollten strukturiert geführt werden'
            })

        # Default follow-up for any activity
        if not suggestions:
            suggestions.append({
                'action': 'Allgemeine Nachverfolgung',
                'description': 'Kundenzufriedenheit überprüfen und weitere Bedarfe erfragen',
                'priority': 'low',
                'suggested_date': datetime.now() + timedelta(days=14),
                'reason': 'Regelmäßiger Kundenkontakt stärkt die Beziehung'
            })

        return suggestions

    def generate_report_insights(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI insights from report data

        Args:
            report_data: Daily/weekly report data

        Returns:
            AI-generated insights and recommendations
        """
        insights = {
            'key_findings': [],
            'recommendations': [],
            'trends': [],
            'alerts': []
        }

        summary = report_data.get('summary', {})
        activities = report_data.get('activities', [])
        visits = report_data.get('visits', [])

        # Analyze activity patterns
        total_activities = summary.get('total_activities', 0)
        total_visits = summary.get('total_visits', 0)

        if total_activities > 10:
            insights['key_findings'].append({
                'type': 'activity_volume',
                'message': f'Hochaktiver Tag mit {total_activities} Aktivitäten',
                'impact': 'positive'
            })

        if total_visits == 0:
            insights['alerts'].append({
                'type': 'no_visits',
                'message': 'Keine Kundenbesuche heute - Außendienst-Aktivität prüfen',
                'priority': 'medium'
            })

        # Analyze topics
        main_topics = summary.get('main_topics', [])
        if len(main_topics) > 3:
            insights['trends'].append({
                'type': 'topic_diversity',
                'message': f'Breite Themenpalette: {", ".join(main_topics[:3])}',
                'insight': 'Vielfältige Kundenbedarfe zeigen gute Marktabdeckung'
            })

        # Analyze conversion
        orders_placed = summary.get('orders_placed', 0)
        quotes_created = summary.get('quotes_created', 0)

        if orders_placed > 0:
            conversion_rate = orders_placed / max(1, quotes_created) * 100
            if conversion_rate > 50:
                insights['key_findings'].append({
                    'type': 'high_conversion',
                    'message': f'Starke Conversion: {conversion_rate:.1f}% der Angebote wurden bestellt',
                    'impact': 'positive'
                })

        # Generate recommendations
        if summary.get('total_time_minutes', 0) > 480:  # 8 hours
            insights['recommendations'].append({
                'type': 'workload',
                'message': 'Hohe Arbeitsbelastung - Work-Life-Balance beachten',
                'action': 'Arbeitszeiten überprüfen und bei Bedarf reduzieren'
            })

        # Analyze customer feedback
        negative_feedback = []
        for visit in visits:
            feedback = visit.get('customer_feedback', '')
            if feedback:
                sentiment = self.analyze_sentiment(feedback)
                if sentiment['sentiment'] == 'negative':
                    negative_feedback.append(visit.get('customer', 'Unbekannt'))

        if negative_feedback:
            insights['alerts'].append({
                'type': 'negative_feedback',
                'message': f'Unzufriedenheit bei Kunden: {", ".join(negative_feedback)}',
                'priority': 'high',
                'action': 'Sofortige Nachverfolgung erforderlich'
            })

        return insights

    def predict_customer_value(self, customer_id: str) -> Dict[str, Any]:
        """
        Predict customer lifetime value and segment

        Args:
            customer_id: Customer ID

        Returns:
            Customer value prediction
        """
        # Get customer data
        customer = self.db.query(
            self.db.query().filter_by(id=customer_id).first()
        ).first()

        if not customer:
            return {'error': 'Customer not found'}

        # Simple prediction based on historical data
        total_revenue = customer.total_revenue or 0
        last_order_days = 0

        if customer.last_order_date:
            last_order_days = (datetime.now() - customer.last_order_date).days

        # Predict next order probability
        if last_order_days < 30:
            next_order_probability = 0.8
        elif last_order_days < 90:
            next_order_probability = 0.5
        elif last_order_days < 180:
            next_order_probability = 0.2
        else:
            next_order_probability = 0.1

        # Predict lifetime value
        avg_order_value = total_revenue / max(1, customer.order_count or 1)
        predicted_lifetime_value = total_revenue + (avg_order_value * next_order_probability * 12)

        # Determine segment
        if predicted_lifetime_value > 50000:
            segment = 'A - Premium'
        elif predicted_lifetime_value > 20000:
            segment = 'B - Wichtig'
        elif predicted_lifetime_value > 5000:
            segment = 'C - Standard'
        else:
            segment = 'D - Gelegenheitskunde'

        return {
            'customer_id': customer_id,
            'current_value': total_revenue,
            'predicted_lifetime_value': predicted_lifetime_value,
            'next_order_probability': next_order_probability,
            'segment': segment,
            'risk_level': 'high' if last_order_days > 180 else 'medium' if last_order_days > 90 else 'low',
            'recommendations': self._generate_customer_recommendations(customer, predicted_lifetime_value)
        }

    def _generate_customer_recommendations(self, customer: Any, predicted_value: float) -> List[str]:
        """Generate customer-specific recommendations"""
        recommendations = []

        if predicted_value > 30000:
            recommendations.append("Premium-Kundenbetreuung priorisieren")
            recommendations.append("Persönliche Ansprechpartner zuweisen")

        if customer.last_order_date and (datetime.now() - customer.last_order_date).days > 60:
            recommendations.append("Reaktivierungskampagne starten")

        if customer.credit_rating == 'schlecht':
            recommendations.append("Zahlungskonditionen überprüfen")

        return recommendations

    def optimize_route(self, visits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize visit routes for better efficiency

        Args:
            visits: List of planned visits

        Returns:
            Optimized route suggestions
        """
        # Simple nearest neighbor optimization (can be enhanced with TSP algorithms)
        if len(visits) <= 1:
            return {'optimized_route': visits, 'savings': 0}

        # Calculate current total distance (simplified)
        current_distance = sum(visit.get('kilometers', 0) for visit in visits)

        # For demonstration, suggest a more efficient order
        # In practice, this would use GPS coordinates and routing APIs
        optimized_visits = sorted(visits, key=lambda x: x.get('location', ''))

        return {
            'original_route': visits,
            'optimized_route': optimized_visits,
            'estimated_savings_km': max(0, current_distance * 0.15),  # 15% savings estimate
            'estimated_savings_time': max(0, current_distance * 0.15 * 2),  # 2 min per km
            'recommendations': [
                'Start mit südlichen Kunden für bessere Tagesstruktur',
                'Berücksichtige Verkehrszeiten bei Routenplanung',
                'Pausen zwischen Besuchen einplanen'
            ]
        }