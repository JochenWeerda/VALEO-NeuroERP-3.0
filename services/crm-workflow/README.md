# CRM Workflow

Microservice handling automated workflows, triggers, notifications, and business process automation for the CRM system.

## Features

- **Workflow Engine**: Define and execute automated business processes
- **Event Triggers**: React to CRM events (case created, opportunity updated, etc.)
- **Automated Actions**: Send notifications, update records, create tasks
- **Escalation Rules**: Automatic escalation based on time/conditions
- **Notification System**: Email, in-app, and external notifications
- **SLA Monitoring**: Automatic breach detection and notifications

## API Endpoints

- `GET/POST/PUT/DELETE /api/v1/workflows` - Workflow definition management
- `GET/POST/PUT/DELETE /api/v1/triggers` - Event trigger configuration
- `POST /api/v1/workflows/{id}/execute` - Manual workflow execution
- `GET /api/v1/notifications` - Notification history and management
- `POST /api/v1/events/process` - Process incoming events

## Database Tables

- `crm_workflow_workflows`
- `crm_workflow_triggers`
- `crm_workflow_actions`
- `crm_workflow_executions`
- `crm_workflow_notifications`

## Dependencies

- PostgreSQL for workflow definitions and execution history
- Redis for event queuing and caching
- Event bus for integration with other CRM services
- Email service for notifications