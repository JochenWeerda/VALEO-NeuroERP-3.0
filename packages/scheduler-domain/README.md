# Scheduler Domain

A comprehensive scheduling service built with Domain-Driven Design (DDD) principles, providing reliable job scheduling with support for CRON expressions, recurring rules, and event-driven execution.

## Features

- **Multiple Trigger Types**: CRON expressions, RRULE (iCal), fixed delays, and one-shot schedules
- **Flexible Targets**: Event publishing, HTTP webhooks, and queue messaging
- **Tenant Isolation**: Multi-tenant support with proper data isolation
- **Security**: JWT-based authentication with role-based access control (RBAC)
- **Observability**: OpenTelemetry tracing and structured logging
- **Health Checks**: Comprehensive health, readiness, and liveness endpoints
- **Docker Support**: Production-ready containerization

## Architecture

### Domain Layer
- **Entities**: `ScheduleEntity` with business logic and validation
- **Services**: `SchedulingService` for schedule execution and management
- **Events**: Domain events for schedule lifecycle

### Infrastructure Layer
- **Repository**: Data access layer with Drizzle ORM
- **Messaging**: Event publishing infrastructure
- **Security**: JWT authentication and RBAC
- **Telemetry**: Logging and tracing

### Application Layer
- **Routes**: REST API endpoints with OpenAPI documentation
- **Middleware**: Authentication, tenant isolation, and request logging
- **Server**: Fastify-based HTTP server

## Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL
- Redis (optional, for distributed locking)
- NATS (optional, for event publishing)

### Installation

```bash
npm install
```

### Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the following environment variables:

```env
# Server
PORT=3080
HOST=0.0.0.0

# Database
POSTGRES_URL=postgres://user:pass@localhost:5432/scheduler

# Authentication
JWKS_URL=https://auth.example.com/.well-known/jwks.json

# Observability
LOG_LEVEL=info
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### Database Setup

Run the database migrations:

```bash
npm run migrate:up
```

### Development

```bash
npm run dev
```

### Production

```bash
npm run build
npm start
```

## API Documentation

### Create Schedule

```http
POST /schedules
Authorization: Bearer <token>
X-Tenant-Id: <tenant-id>
Content-Type: application/json

{
  "tenantId": "tenant-123",
  "name": "Daily Report",
  "tz": "Europe/Berlin",
  "trigger": {
    "type": "CRON",
    "cron": "0 9 * * *"
  },
  "target": {
    "kind": "EVENT",
    "eventTopic": "reports.daily.generate"
  },
  "enabled": true
}
```

### List Schedules

```http
GET /schedules?tenantId=tenant-123&page=1&pageSize=20
Authorization: Bearer <token>
X-Tenant-Id: <tenant-id>
```

### Update Schedule

```http
PATCH /schedules/{id}
Authorization: Bearer <token>
X-Tenant-Id: <tenant-id>
Content-Type: application/json

{
  "enabled": false
}
```

## Schedule Types

### CRON Schedules
```json
{
  "trigger": {
    "type": "CRON",
    "cron": "0 9 * * 1-5"
  }
}
```

### RRULE Schedules
```json
{
  "trigger": {
    "type": "RRULE",
    "rrule": "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9"
  }
}
```

### Fixed Delay Schedules
```json
{
  "trigger": {
    "type": "FIXED_DELAY",
    "delaySec": 3600
  }
}
```

### One-shot Schedules
```json
{
  "trigger": {
    "type": "ONE_SHOT",
    "startAt": "2024-01-01T09:00:00Z"
  }
}
```

## Target Types

### Event Targets
```json
{
  "target": {
    "kind": "EVENT",
    "eventTopic": "my.custom.event"
  }
}
```

### HTTP Targets
```json
{
  "target": {
    "kind": "HTTP",
    "http": {
      "url": "https://api.example.com/webhook",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  }
}
```

### Queue Targets
```json
{
  "target": {
    "kind": "QUEUE",
    "queue": {
      "topic": "my-queue-topic"
    }
  }
}
```

## Health Checks

### Health Check
```http
GET /health
```

### Readiness Check
```http
GET /ready
```

### Liveness Check
```http
GET /live
```

## Docker

Build the Docker image:

```bash
docker build -t scheduler-domain .
```

Run with Docker Compose:

```yaml
version: '3.8'
services:
  scheduler:
    image: scheduler-domain
    ports:
      - "3080:3000"
    environment:
      - POSTGRES_URL=postgres://user:pass@db:5432/scheduler
      - JWKS_URL=https://auth.example.com/.well-known/jwks.json
    depends_on:
      - db
```

## Testing

Run unit tests:

```bash
npm test
```

Run tests with coverage:

```bash
npm run test:coverage
```

## Development

### Project Structure

```
src/
├── app/
│   ├── middleware/     # Request middleware
│   ├── routes/         # API routes
│   └── server.ts       # Fastify server setup
├── domain/
│   ├── entities/       # Domain entities
│   └── services/       # Domain services
├── infra/
│   ├── db/            # Database schema and connections
│   ├── messaging/     # Event publishing
│   ├── repo/          # Data repositories
│   ├── security/      # Authentication & authorization
│   └── telemetry/     # Logging and tracing
└── index.ts           # Main exports
```

### Adding New Features

1. **Domain Logic**: Add to `src/domain/`
2. **API Endpoints**: Add to `src/app/routes/`
3. **Infrastructure**: Add to `src/infra/`
4. **Tests**: Add to `tests/`

## License

MIT