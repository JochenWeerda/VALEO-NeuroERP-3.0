***REMOVED*** Sales Domain Service

A comprehensive, production-ready domain service for managing sales operations including quotes, orders, invoices, and credit notes within the VALEO NeuroERP system.

***REMOVED******REMOVED*** Features

- **Domain-Driven Design (DDD)**: Clean architecture with aggregate roots, entities, and domain services
- **Event-Driven Architecture**: Domain events for all state changes with NATS/Kafka publishing
- **REST API**: Fastify-based REST API with OpenAPI/Swagger documentation
- **Security**: JWT authentication with JWKS, tenant isolation, and RBAC
- **Observability**: OpenTelemetry tracing and structured logging
- **Database**: PostgreSQL with Drizzle ORM and migrations
- **Testing**: Vitest for unit tests, Supertest for E2E tests
- **Containerization**: Docker-ready with multi-stage builds

***REMOVED******REMOVED*** Architecture

***REMOVED******REMOVED******REMOVED*** Domain Model

- **Quote**: Sales quotes with line items, validity periods, and status transitions
- **Order**: Customer orders with confirmation and invoicing workflows
- **Invoice**: Billing documents with payment tracking and overdue management
- **CreditNote**: Credit notes for adjustments and settlements

***REMOVED******REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED******REMOVED*** Quotes
- `GET /quotes` - List quotes with pagination and filtering
- `POST /quotes` - Create new quote
- `GET /quotes/:id` - Get quote details
- `PATCH /quotes/:id` - Update quote
- `POST /quotes/:id/send` - Send quote to customer

***REMOVED******REMOVED******REMOVED******REMOVED*** Orders
- `GET /orders` - List orders
- `POST /orders` - Create order from quote
- `GET /orders/:id` - Get order details
- `PATCH /orders/:id` - Update order
- `POST /orders/:id/confirm` - Confirm order

***REMOVED******REMOVED******REMOVED******REMOVED*** Invoices
- `GET /invoices` - List invoices
- `POST /invoices` - Create invoice from order
- `GET /invoices/:id` - Get invoice details
- `PATCH /invoices/:id` - Update invoice
- `POST /invoices/:id/pay` - Mark invoice as paid

***REMOVED******REMOVED******REMOVED******REMOVED*** Credit Notes
- `GET /credit-notes` - List credit notes
- `POST /credit-notes` - Create credit note
- `GET /credit-notes/:id` - Get credit note details
- `PATCH /credit-notes/:id` - Update credit note
- `POST /credit-notes/:id/settle` - Settle credit note

***REMOVED******REMOVED******REMOVED******REMOVED*** Health & Monitoring
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /live` - Liveness check
- `GET /docs` - OpenAPI documentation

***REMOVED******REMOVED*** Getting Started

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Node.js 18+
- PostgreSQL 13+
- NATS or Kafka (optional, for event publishing)
- Redis (optional, for caching)

***REMOVED******REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Install dependencies
npm install

***REMOVED*** Copy environment configuration
cp .env.example .env

***REMOVED*** Configure your environment variables
***REMOVED*** Edit .env with your database, auth, and messaging settings
```

***REMOVED******REMOVED******REMOVED*** Database Setup

```bash
***REMOVED*** Generate and run migrations
npm run migrate:gen
npm run migrate:up
```

***REMOVED******REMOVED******REMOVED*** Development

```bash
***REMOVED*** Start development server with hot reload
npm run dev

***REMOVED*** Run tests
npm test

***REMOVED*** Run tests in watch mode
npm run test:watch

***REMOVED*** Run with coverage
npm run test:coverage

***REMOVED*** Build for production
npm run build

***REMOVED*** Start production server
npm start
```

***REMOVED******REMOVED******REMOVED*** Docker

```bash
***REMOVED*** Build Docker image
docker build -t valero-neuroerp/sales-domain .

***REMOVED*** Run with Docker Compose
docker-compose up
```

***REMOVED******REMOVED*** Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3001` |
| `HOST` | Server host | `0.0.0.0` |
| `NODE_ENV` | Environment | `production` |
| `LOG_LEVEL` | Log level | `info` |
| `POSTGRES_URL` | PostgreSQL connection URL | Required |
| `JWKS_URL` | JWKS endpoint URL | Required |
| `JWT_ISSUER` | JWT issuer | Optional |
| `JWT_AUDIENCE` | JWT audience | Optional |
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry endpoint | `http://localhost:4317` |

***REMOVED******REMOVED*** Domain Events

The service publishes domain events for all state changes:

***REMOVED******REMOVED******REMOVED*** Quote Events
- `sales.quote.created`
- `sales.quote.sent`
- `sales.quote.accepted`
- `sales.quote.rejected`
- `sales.quote.expired`

***REMOVED******REMOVED******REMOVED*** Order Events
- `sales.order.created`
- `sales.order.confirmed`
- `sales.order.invoiced`
- `sales.order.cancelled`

***REMOVED******REMOVED******REMOVED*** Invoice Events
- `sales.invoice.issued`
- `sales.invoice.paid`
- `sales.invoice.overdue`
- `sales.invoice.cancelled`

***REMOVED******REMOVED******REMOVED*** Credit Note Events
- `sales.credit_note.issued`
- `sales.credit_note.settled`

***REMOVED******REMOVED*** Security

- **Authentication**: JWT tokens validated against JWKS
- **Authorization**: Role-based access control (RBAC)
- **Tenant Isolation**: Multi-tenant architecture with tenant IDs
- **Request Validation**: Zod schemas for all inputs
- **Rate Limiting**: Configurable request limits

***REMOVED******REMOVED*** Observability

- **Tracing**: OpenTelemetry distributed tracing
- **Logging**: Structured logging with Pino
- **Metrics**: Health checks and readiness probes
- **Request IDs**: Correlation IDs for request tracking

***REMOVED******REMOVED*** Testing

```bash
***REMOVED*** Run all tests
npm test

***REMOVED*** Run unit tests only
npm run test:unit

***REMOVED*** Run integration tests
npm run test:integration

***REMOVED*** Run E2E tests
npm run test:e2e
```

***REMOVED******REMOVED*** API Documentation

When running the server, visit `http://localhost:3001/docs` for interactive OpenAPI documentation.

***REMOVED******REMOVED*** Contributing

1. Follow the existing code style and architecture patterns
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting PRs

***REMOVED******REMOVED*** License

This project is part of the VALEO NeuroERP system. See the main project license for details.