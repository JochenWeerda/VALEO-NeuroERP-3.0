***REMOVED*** @valero-neuroerp/scheduler-domain

Enterprise-wide orchestrator for scheduled/timed tasks in the VALEO NeuroERP system.

***REMOVED******REMOVED*** Overview

The Scheduler Domain provides a comprehensive scheduling system that enables:

- **Schedules**: CRON, RRULE, Fixed-Delay, and One-Shot triggers with calendar support
- **Jobs**: Configurable job types with retry logic, backoff strategies, and concurrency limits
- **Runs**: Individual execution instances with status tracking and metrics
- **Workers**: Distributed worker management with capabilities and heartbeats
- **Calendars**: Holiday and business day management for scheduling

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Domain-Driven Design (DDD)
- **Entities**: Schedule, Job, Run, Worker, Calendar
- **Services**: Scheduling logic, execution management, worker coordination
- **Events**: Domain events for observability and integration

***REMOVED******REMOVED******REMOVED*** Key Features
- **Tenant Isolation**: All resources are tenant-scoped
- **Time Zone Support**: UTC storage with tenant-specific timezone evaluation
- **Distributed Execution**: Leader election and worker coordination
- **Resilience**: Retry logic, dead letter queues, idempotency
- **Observability**: OpenTelemetry tracing, structured logging, metrics

***REMOVED******REMOVED*** Domain Entities

***REMOVED******REMOVED******REMOVED*** Schedule
Represents a scheduled task configuration with triggers, targets, and calendar rules.

**Triggers:**
- `CRON`: Standard cron expressions
- `RRULE`: iCal recurrence rules
- `FIXED_DELAY`: Fixed interval scheduling
- `ONE_SHOT`: Single execution

**Targets:**
- `EVENT`: Publish to NATS/Kafka
- `HTTP`: Webhook with HMAC signing
- `QUEUE`: Send to message queue

***REMOVED******REMOVED******REMOVED*** Job
Configuration for job types including retry policies and execution constraints.

***REMOVED******REMOVED******REMOVED*** Run
Individual execution instance with status tracking and metrics.

***REMOVED******REMOVED******REMOVED*** Worker
Registered worker nodes with capabilities and health monitoring.

***REMOVED******REMOVED******REMOVED*** Calendar
Holiday and business day definitions for scheduling logic.

***REMOVED******REMOVED*** API Design

***REMOVED******REMOVED******REMOVED*** REST Endpoints
- `POST /schedules` - Create schedule
- `GET /schedules` - List schedules with pagination
- `GET /schedules/:id` - Get schedule details
- `PATCH /schedules/:id` - Update schedule
- `POST /schedules/:id/trigger` - Manual trigger
- `POST /schedules/:id/backfill` - Backfill missed runs

- `POST /jobs` - Create job configuration
- `GET /jobs` - List jobs
- `PATCH /jobs/:id` - Update job

- `GET /runs` - List runs with filtering
- `GET /runs/:id` - Get run details
- `POST /runs/:id/retry` - Retry failed run
- `POST /runs/:id/cancel` - Cancel pending run

- `POST /workers/register` - Register worker
- `POST /workers/:id/heartbeat` - Worker heartbeat
- `GET /workers` - List workers

***REMOVED******REMOVED*** Database Schema

***REMOVED******REMOVED******REMOVED*** Tables
- `schedules` - Schedule configurations
- `jobs` - Job type definitions
- `runs` - Execution instances
- `workers` - Worker registrations
- `calendars` - Calendar definitions

***REMOVED******REMOVED******REMOVED*** Key Relationships
- Schedule → Runs (1:N)
- Job → Runs (1:N)
- Worker → Runs (1:N)

***REMOVED******REMOVED*** Event System

***REMOVED******REMOVED******REMOVED*** Domain Events
- `scheduler.schedule.created|updated|enabled|disabled`
- `scheduler.run.started|succeeded|failed|missed|dead`
- `scheduler.worker.registered|heartbeat|offline`

***REMOVED******REMOVED******REMOVED*** Integration Events
Consumed from other domains for trigger-based scheduling.

***REMOVED******REMOVED*** Security

- **JWT Authentication**: Bearer token validation
- **RBAC**: scheduler:admin|read|operate scopes
- **Tenant Isolation**: All queries filtered by tenantId
- **HMAC Webhooks**: Signed HTTP targets for security

***REMOVED******REMOVED*** Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables
```bash
PORT=3080
POSTGRES_URL=postgres://user:pass@db:5432/scheduler
NATS_URL=nats://nats:4222
REDIS_URL=redis://redis:6379
JWKS_URL=https://auth.example.com/.well-known/jwks.json
DEFAULT_TZ=Europe/Berlin
WEBHOOK_HMAC_SECRET=change-me-in-production
```

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Prerequisites
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- NATS Server

***REMOVED******REMOVED******REMOVED*** Setup
```bash
npm install
npm run migrate:up
npm run dev
```

***REMOVED******REMOVED******REMOVED*** Testing
```bash
npm run test:unit
npm run test:integration
npm run test:e2e
```

***REMOVED******REMOVED******REMOVED*** Building
```bash
npm run build
npm start
```

***REMOVED******REMOVED*** Use Cases

***REMOVED******REMOVED******REMOVED*** Analytics Domain
- Nightly KPI rebuilds (CRON 0 2 * * *)
- Forecast calculations every 6 hours
- Report generation on demand

***REMOVED******REMOVED******REMOVED*** Notifications Domain
- Daily invoice reminders (business days only)
- Weekly campaign summaries
- SLA breach alerts

***REMOVED******REMOVED******REMOVED*** Document Domain
- Retention policy enforcement (monthly)
- Legal hold checks (daily)
- Archive cleanup (weekly)

***REMOVED******REMOVED******REMOVED*** HR Domain
- Payroll processing (end of month)
- Time tracking summaries (daily)
- Compliance reporting (quarterly)

***REMOVED******REMOVED*** Monitoring & Observability

***REMOVED******REMOVED******REMOVED*** Metrics
- Schedule execution latency
- Job success/failure rates
- Worker utilization
- Queue depths

***REMOVED******REMOVED******REMOVED*** Health Checks
- Database connectivity
- Message broker status
- Worker heartbeats
- Leader election status

***REMOVED******REMOVED*** Deployment

***REMOVED******REMOVED******REMOVED*** Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist/ ./dist/
EXPOSE 3080
CMD ["npm", "start"]
```

***REMOVED******REMOVED******REMOVED*** Kubernetes
- Deployment with leader election
- Horizontal Pod Autoscaling
- ConfigMap for calendar data
- Persistent volume for state

***REMOVED******REMOVED*** Contributing

1. Follow DDD principles
2. Write comprehensive tests
3. Update OpenAPI documentation
4. Ensure tenant isolation
5. Add appropriate logging

***REMOVED******REMOVED*** License

Proprietary - VALEO NeuroERP