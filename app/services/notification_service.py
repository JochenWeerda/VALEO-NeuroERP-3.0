"""
Notification Service
Multi-channel notification delivery for VALEO NeuroERP
Supports Email, Teams, Telegram, SMS
"""

import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NotificationChannel:
    """Configuration for a notification channel"""
    name: str
    type: str  # email, teams, telegram, sms
    enabled: bool
    config: Dict[str, Any]


class NotificationService:
    """Multi-channel notification service"""

    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {}
        self._load_channels()

    def _load_channels(self):
        """Load notification channels from configuration"""
        # Email channel
        self.channels['email'] = NotificationChannel(
            name='email',
            type='email',
            enabled=True,
            config={
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'noreply@valeo-neuroerp.de',
                'password': 'your-email-password',  # Should come from env/secrets
                'from_email': 'noreply@valeo-neuroerp.de'
            }
        )

        # Microsoft Teams channel
        self.channels['teams'] = NotificationChannel(
            name='teams',
            type='teams',
            enabled=True,
            config={
                'webhook_url': 'https://outlook.office.com/webhook/your-webhook-url'
            }
        )

        # Telegram channel
        self.channels['telegram'] = NotificationChannel(
            name='telegram',
            type='telegram',
            enabled=True,
            config={
                'bot_token': 'your-telegram-bot-token',
                'chat_ids': {
                    'management': '-1001234567890',
                    'sales_team': '-1001234567891'
                }
            }
        )

    def send_notification(self, channel: str, recipient: str, subject: str,
                         message: str, message_type: str = 'text') -> Dict[str, Any]:
        """
        Send notification via specified channel

        Args:
            channel: Channel name (email, teams, telegram)
            recipient: Recipient identifier
            subject: Message subject
            message: Message content
            message_type: Type of message (text, html, markdown)

        Returns:
            Result dictionary
        """
        if channel not in self.channels:
            return {'success': False, 'error': f'Channel {channel} not found'}

        channel_config = self.channels[channel]
        if not channel_config.enabled:
            return {'success': False, 'error': f'Channel {channel} is disabled'}

        try:
            if channel == 'email':
                return self._send_email(recipient, subject, message, message_type)
            elif channel == 'teams':
                return self._send_teams_message(message, message_type)
            elif channel == 'telegram':
                return self._send_telegram_message(recipient, message, message_type)
            else:
                return {'success': False, 'error': f'Unsupported channel type: {channel_config.type}'}

        except Exception as e:
            logger.error(f"Error sending {channel} notification: {e}")
            return {'success': False, 'error': str(e)}

    def send_daily_reports(self, reports: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send daily reports to all configured channels

        Args:
            reports: Report data from DailyReportService

        Returns:
            Results for all channels
        """
        results = {
            'email': [],
            'teams': [],
            'telegram': []
        }

        for rep_id, report_data in reports.items():
            sales_rep = report_data['sales_rep']

            # Format report for different channels
            markdown_report = self._format_report_for_channel(report_data, 'markdown')
            html_report = self._format_report_for_channel(report_data, 'html')

            # Send via email
            if self.channels['email'].enabled:
                email_result = self.send_notification(
                    'email',
                    sales_rep.email,
                    f'Tagesprotokoll {sales_rep.first_name} {sales_rep.last_name}',
                    html_report,
                    'html'
                )
                results['email'].append({
                    'recipient': sales_rep.email,
                    'success': email_result['success'],
                    'error': email_result.get('error')
                })

            # Send to Teams
            if self.channels['teams'].enabled:
                teams_result = self.send_notification(
                    'teams',
                    'management',
                    f'📊 Tagesprotokoll: {sales_rep.first_name} {sales_rep.last_name}',
                    markdown_report,
                    'markdown'
                )
                results['teams'].append({
                    'recipient': 'management',
                    'success': teams_result['success'],
                    'error': teams_result.get('error')
                })

            # Send to Telegram
            if self.channels['telegram'].enabled:
                telegram_result = self.send_notification(
                    'telegram',
                    'management',
                    f'Tagesprotokoll {sales_rep.first_name} {sales_rep.last_name}',
                    markdown_report,
                    'markdown'
                )
                results['telegram'].append({
                    'recipient': 'management',
                    'success': telegram_result['success'],
                    'error': telegram_result.get('error')
                })

        return results

    def _send_email(self, recipient: str, subject: str, message: str, message_type: str) -> Dict[str, Any]:
        """Send email notification"""
        config = self.channels['email'].config

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = config['from_email']
            msg['To'] = recipient

            if message_type == 'html':
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))

            # Send email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.sendmail(config['from_email'], recipient, msg.as_string())
            server.quit()

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _send_teams_message(self, message: str, message_type: str) -> Dict[str, Any]:
        """Send Microsoft Teams notification"""
        config = self.channels['teams'].config

        try:
            # Format for Teams
            if message_type == 'markdown':
                teams_message = {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    "themeColor": "0076D7",
                    "title": "VALEO NeuroERP - Tagesprotokoll",
                    "text": message
                }
            else:
                teams_message = {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    "themeColor": "0076D7",
                    "title": "VALEO NeuroERP - Tagesprotokoll",
                    "text": message
                }

            response = requests.post(
                config['webhook_url'],
                json=teams_message,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                return {'success': True}
            else:
                return {'success': False, 'error': f'Teams API error: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _send_telegram_message(self, recipient: str, message: str, message_type: str) -> Dict[str, Any]:
        """Send Telegram notification"""
        config = self.channels['telegram'].config

        try:
            chat_id = config['chat_ids'].get(recipient, config['chat_ids'].get('management'))

            if message_type == 'markdown':
                # Convert basic markdown to HTML for Telegram
                telegram_message = message.replace('**', '<b>').replace('**', '</b>')
                telegram_message = telegram_message.replace('*', '<i>').replace('*', '</i>')
            else:
                telegram_message = message

            url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': telegram_message,
                'parse_mode': 'HTML' if message_type == 'markdown' else 'text'
            }

            response = requests.post(url, data=data)

            if response.status_code == 200:
                return {'success': True}
            else:
                return {'success': False, 'error': f'Telegram API error: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _format_report_for_channel(self, report_data: Dict[str, Any], format_type: str) -> str:
        """
        Format report for specific channel

        Args:
            report_data: Report data
            format_type: markdown, html, text

        Returns:
            Formatted report
        """
        sales_rep = report_data['sales_rep']
        report_date = report_data['report_date']
        data = report_data['data']

        if format_type == 'markdown':
            return self._format_markdown_report(sales_rep, report_date, data)
        elif format_type == 'html':
            return self._format_html_report(sales_rep, report_date, data)
        else:
            return self._format_text_report(sales_rep, report_date, data)

    def _format_markdown_report(self, sales_rep: Any, report_date: str, data: Dict[str, Any]) -> str:
        """Format report as Markdown"""
        summary = data['summary']

        lines = [
            f"# 📊 Tagesprotokoll – Außendienst ({sales_rep.first_name} {sales_rep.last_name})",
            f"**Datum:** {report_date}",
            "",
            "## 📈 Zusammenfassung",
            f"- **Besuche:** {summary['total_visits']}",
            f"- **Aktivitäten:** {summary['total_activities']}",
            f"- **Zeit:** {summary['total_time_minutes']} Minuten",
            f"- **Kilometer:** {summary['total_kilometers']} km",
            f"- **Aufträge:** {summary['orders_placed']}",
            f"- **Angebote:** {summary['quotes_created']}",
            ""
        ]

        if summary['main_topics']:
            lines.extend([
                "## 🎯 Hauptthemen",
                *[f"- {topic}" for topic in summary['main_topics'][:5]],
                ""
            ])

        return "\n".join(lines)

    def _format_html_report(self, sales_rep: Any, report_date: str, data: Dict[str, Any]) -> str:
        """Format report as HTML"""
        summary = data['summary']

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .summary {{ background: #e8f4f8; padding: 10px; margin: 10px 0; }}
                .topics {{ background: #f8f0e8; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>VALEO NeuroERP - Tagesprotokoll</h1>
                <h2>{sales_rep.first_name} {sales_rep.last_name}</h2>
                <p><strong>Datum:</strong> {report_date}</p>
            </div>

            <div class="summary">
                <h3>Zusammenfassung</h3>
                <ul>
                    <li><strong>Besuche:</strong> {summary['total_visits']}</li>
                    <li><strong>Aktivitäten:</strong> {summary['total_activities']}</li>
                    <li><strong>Zeit:</strong> {summary['total_time_minutes']} Minuten</li>
                    <li><strong>Kilometer:</strong> {summary['total_kilometers']} km</li>
                    <li><strong>Aufträge:</strong> {summary['orders_placed']}</li>
                    <li><strong>Angebote:</strong> {summary['quotes_created']}</li>
                </ul>
            </div>

            {"".join([f'<div class="topics"><h3>Hauptthemen</h3><ul>{"".join([f"<li>{topic}</li>" for topic in summary["main_topics"][:5]])}</ul></div>' if summary['main_topics'] else ''])}
        </body>
        </html>
        """

        return html

    def _format_text_report(self, sales_rep: Any, report_date: str, data: Dict[str, Any]) -> str:
        """Format report as plain text"""
        summary = data['summary']

        return f"""
VALEO NeuroERP - Tagesprotokoll
{sales_rep.first_name} {sales_rep.last_name}
Datum: {report_date}

ZUSAMMENFASSUNG:
- Besuche: {summary['total_visits']}
- Aktivitäten: {summary['total_activities']}
- Zeit: {summary['total_time_minutes']} Minuten
- Kilometer: {summary['total_kilometers']} km
- Aufträge: {summary['orders_placed']}
- Angebote: {summary['quotes_created']}

HAUPTTHEMEN:
{chr(10).join(f"- {topic}" for topic in summary['main_topics'][:5])}
        """.strip()


# Global notification service instance
notification_service = NotificationService()


def send_daily_reports_notification(reports: Dict[str, Any]):
    """Send daily reports via all configured channels"""
    return notification_service.send_daily_reports(reports)


# For testing
if __name__ == "__main__":
    # Test notification
    test_report = {
        'rep1': {
            'sales_rep': type('obj', (object,), {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'})(),
            'report_date': '2025-10-15',
            'data': {
                'summary': {
                    'total_visits': 5,
                    'total_activities': 12,
                    'total_time_minutes': 240,
                    'total_kilometers': 150,
                    'orders_placed': 2,
                    'quotes_created': 4,
                    'main_topics': ['Dünger', 'Saatgut', 'Preise']
                }
            }
        }
    }

    result = send_daily_reports_notification(test_report)
    print(f"Notification result: {result}")