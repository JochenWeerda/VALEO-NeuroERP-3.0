***REMOVED*** Scheduler Domain

A comprehensive scheduling service built with Domain-Driven Design (DDD) principles, providing reliable job scheduling with support for CRON expressions, recurring rules, and event-driven execution.

***REMOVED******REMOVED*** Features

- **Multiple Trigger Types**: CRON expressions, RRULE (iCal), fixed delays, and one-shot schedules
- **Flexible Targets**: Event publishing, HTTP webhooks, and queue messaging
- **Tenant Isolation**: Multi-tenant support with proper data isolation
- **Security**: JWT-based authentication with role-based access control (RBAC)
- **Observability**: OpenTelemetry tracing and structured logging
- **Health Checks**: Comprehensive health, readiness, and liveness endpoints
- **Docker Support**: Production-ready containerization

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Domain Layer
- **Entities**: `ScheduleEntity` with business logic and validation
- **Services**: `SchedulingService` for schedule execution and management
- **Events**: Domain events for schedule lifecycle

***REMOVED******REMOVED******REMOVED*** Infrastructure Layer
- **Repository**: Data access layer with Drizzle ORM
- **Messaging**: Event publishing infrastructure
- **Security**: JWT authentication and RBAC
- **Telemetry**: Logging and tracing

***REMOVED******REMOVED******REMOVED*** Application Layer
- **Routes**: REST API endpoints with OpenAPI documentation
- **Middleware**: Authentication, tenant isolation, and request logging
- **Server**: Fastify-based HTTP server

***REMOVED******REMOVED*** Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites
- Node.js 18+
- PostgreSQL
- Redis (optional, for distributed locking)
- NATS (optional, for event publishing)

***REMOVED******REMOVED******REMOVED*** Installation

```bash
npm install
```

***REMOVED******REMOVED******REMOVED*** Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the following environment variables:

```env
***REMOVED*** Server
PORT=3080
HOST=0.0.0.0

***REMOVED*** Database
POSTGRES_URL=postgres://user:pass@localhost:5432/scheduler

***REMOVED*** Authentication
JWKS_URL=https://auth.example.com/.well-known/jwks.json

***REMOVED*** Observability
LOG_LEVEL=info
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

***REMOVED******REMOVED******REMOVED*** Database Setup

Run the database migrations:

```bash
npm run migrate:up
```

***REMOVED******REMOVED******REMOVED*** Development

```bash
npm run dev
```

***REMOVED******REMOVED******REMOVED*** Production

```bash
npm run build
npm start
```

***REMOVED******REMOVED*** API Documentation

***REMOVED******REMOVED******REMOVED*** Create Schedule

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

***REMOVED******REMOVED******REMOVED*** List Schedules

```http
GET /schedules?tenantId=tenant-123&page=1&pageSize=20
Authorization: Bearer <token>
X-Tenant-Id: <tenant-id>
```

***REMOVED******REMOVED******REMOVED*** Update Schedule

```http
PATCH /schedules/{id}
Authorization: Bearer <token>
X-Tenant-Id: <tenant-id>
Content-Type: application/json

{
  "enabled": false
}
```

***REMOVED******REMOVED*** Schedule Types

***REMOVED******REMOVED******REMOVED*** CRON Schedules
```json
{
  "trigger": {
    "type": "CRON",
    "cron": "0 9 * * 1-5"
  }
}
```

***REMOVED******REMOVED******REMOVED*** RRULE Schedules
```json
{
  "trigger": {
    "type": "RRULE",
    "rrule": "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9"
  }
}
```

***REMOVED******REMOVED******REMOVED*** Fixed Delay Schedules
```json
{
  "trigger": {
    "type": "FIXED_DELAY",
    "delaySec": 3600
  }
}
```

***REMOVED******REMOVED******REMOVED*** One-shot Schedules
```json
{
  "trigger": {
    "type": "ONE_SHOT",
    "startAt": "2024-01-01T09:00:00Z"
  }
}
```

***REMOVED******REMOVED*** Target Types

***REMOVED******REMOVED******REMOVED*** Event Targets
```json
{
  "target": {
    "kind": "EVENT",
    "eventTopic": "my.custom.event"
  }
}
```

***REMOVED******REMOVED******REMOVED*** HTTP Targets
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

***REMOVED******REMOVED******REMOVED*** Queue Targets
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

***REMOVED******REMOVED*** Health Checks

***REMOVED******REMOVED******REMOVED*** Health Check
```http
GET /health
```

***REMOVED******REMOVED******REMOVED*** Readiness Check
```http
GET /ready
```

***REMOVED******REMOVED******REMOVED*** Liveness Check
```http
GET /live
```

***REMOVED******REMOVED*** Docker

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

***REMOVED******REMOVED*** Testing

Run unit tests:

```bash
npm test
```

Run tests with coverage:

```bash
npm run test:coverage
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Project Structure

```
src/
├── app/
│   ├── middleware/     ***REMOVED*** Request middleware
│   ├── routes/         ***REMOVED*** API routes
│   └── server.ts       ***REMOVED*** Fastify server setup
├── domain/
│   ├── entities/       ***REMOVED*** Domain entities
│   └── services/       ***REMOVED*** Domain services
├── infra/
│   ├── db/            ***REMOVED*** Database schema and connections
│   ├── messaging/     ***REMOVED*** Event publishing
│   ├── repo/          ***REMOVED*** Data repositories
│   ├── security/      ***REMOVED*** Authentication & authorization
│   └── telemetry/     ***REMOVED*** Logging and tracing
└── index.ts           ***REMOVED*** Main exports
```

***REMOVED******REMOVED******REMOVED*** Adding New Features

1. **Domain Logic**: Add to `src/domain/`
2. **API Endpoints**: Add to `src/app/routes/`
3. **Infrastructure**: Add to `src/infra/`
4. **Tests**: Add to `tests/`

***REMOVED******REMOVED*** License

MIT