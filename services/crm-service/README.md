# CRM Service

Microservice handling customer service management, support tickets, cases, SLAs, and knowledge base.

## Features

- **Support Cases/Tickets**: Customer support request tracking
- **SLA Management**: Service level agreements and escalations
- **Case Assignment**: Automatic and manual ticket routing
- **Knowledge Base**: Articles, FAQs, and self-service resources
- **Case History**: Complete audit trail of all interactions
- **Escalation Rules**: Automatic escalation based on time/priority

## API Endpoints

- `GET/POST/PUT/DELETE /api/v1/cases` - Case management
- `GET/POST/PUT/DELETE /api/v1/knowledge-base` - Knowledge base articles
- `POST /api/v1/cases/{id}/escalate` - Case escalation
- `GET /api/v1/cases/metrics` - Service metrics and KPIs

## Database Tables

- `crm_service_cases`
- `crm_service_case_history`
- `crm_service_slas`
- `crm_service_knowledge_articles`
- `crm_service_categories`

## Dependencies

- PostgreSQL for data persistence
- Redis for caching (optional)
- Event bus for integration with other services
