# CRM Communication

Microservice handling email integration, communication tracking, templates, and automated responses for the CRM system.

## Features

- **Email Integration**: Send/receive emails with full CRM context
- **Template System**: Dynamic email templates with merge fields
- **Communication Tracking**: Complete audit trail of all customer communications
- **Automated Responses**: AI-powered and rule-based auto-replies
- **Email Campaigns**: Bulk email sending with tracking and analytics
- **Attachment Management**: Secure file attachments and document sharing

## API Endpoints

- `POST /api/v1/communication/emails/send` - Send emails with templates
- `GET /api/v1/communication/emails` - List communication history
- `GET /api/v1/communication/templates` - Manage email templates
- `POST /api/v1/communication/campaigns` - Create email campaigns
- `POST /api/v1/communication/webhooks/email` - Receive inbound emails
- `GET /api/v1/communication/analytics` - Communication analytics

## Database Tables

- `crm_communication_emails` - Email messages and metadata
- `crm_communication_templates` - Email templates and variables
- `crm_communication_campaigns` - Email campaign definitions
- `crm_communication_attachments` - File attachments
- `crm_communication_automations` - Automated response rules

## Dependencies

- PostgreSQL for communication data storage
- Redis for email queue and caching
- SMTP server for outbound emails
- IMAP/POP3 for inbound email processing
- Integration with CRM services for context and personalization