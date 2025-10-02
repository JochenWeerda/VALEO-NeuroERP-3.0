# Sales Domain Service

A comprehensive, production-ready domain service for managing sales operations including quotes, orders, invoices, and credit notes within the VALEO NeuroERP system.

## Features

- **Domain-Driven Design (DDD)**: Clean architecture with aggregate roots, entities, and domain services
- **Event-Driven Architecture**: Domain events for all state changes with NATS/Kafka publishing
- **REST API**: Fastify-based REST API with OpenAPI/Swagger documentation
- **Security**: JWT authentication with JWKS, tenant isolation, and RBAC
- **Observability**: OpenTelemetry tracing and structured logging
- **Database**: PostgreSQL with Drizzle ORM and migrations
- **Testing**: Vitest for unit tests, Supertest for E2E tests
- **Containerization**: Docker-ready with multi-stage builds

## Architecture

### Domain Model

- **Quote**: Sales quotes with line items, validity periods, and status transitions
- **Order**: Customer orders with confirmation and invoicing workflows
- **Invoice**: Billing documents with payment tracking and overdue management
- **CreditNote**: Credit notes for adjustments and settlements

### API Endpoints

#### Quotes
- `GET /quotes` - List quotes with pagination and filtering
- `POST /quotes` - Create new quote
- `GET /quotes/:id` - Get quote details
- `PATCH /quotes/:id` - Update quote
- `POST /quotes/:id/send` - Send quote to customer

#### Orders
- `GET /orders` - List orders
- `POST /orders` - Create order from quote
- `GET /orders/:id` - Get order details
- `PATCH /orders/:id` - Update order
- `POST /orders/:id/confirm` - Confirm order

#### Invoices
- `GET /invoices` - List invoices
- `POST /invoices` - Create invoice from order
- `GET /invoices/:id` - Get invoice details
- `PATCH /invoices/:id` - Update invoice
- `POST /invoices/:id/pay` - Mark invoice as paid

#### Credit Notes
- `GET /credit-notes` - List credit notes
- `POST /credit-notes` - Create credit note
- `GET /credit-notes/:id` - Get credit note details
- `PATCH /credit-notes/:id` - Update credit note
- `POST /credit-notes/:id/settle` - Settle credit note

#### Health & Monitoring
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /live` - Liveness check
- `GET /docs` - OpenAPI documentation

## Getting Started

### Prerequisites

- Node.js 18+
- PostgreSQL 13+
- NATS or Kafka (optional, for event publishing)
- Redis (optional, for caching)

### Installation

```bash
# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env

# Configure your environment variables
# Edit .env with your database, auth, and messaging settings
```

### Database Setup

```bash
# Generate and run migrations
npm run migrate:gen
npm run migrate:up
```

### Development

```bash
# Start development server with hot reload
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Build for production
npm run build

# Start production server
npm start
```

### Docker

```bash
# Build Docker image
docker build -t valero-neuroerp/sales-domain .

# Run with Docker Compose
docker-compose up
```

## Configuration

### Environment Variables

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

## Domain Events

The service publishes domain events for all state changes:

### Quote Events
- `sales.quote.created`
- `sales.quote.sent`
- `sales.quote.accepted`
- `sales.quote.rejected`
- `sales.quote.expired`

### Order Events
- `sales.order.created`
- `sales.order.confirmed`
- `sales.order.invoiced`
- `sales.order.cancelled`

### Invoice Events
- `sales.invoice.issued`
- `sales.invoice.paid`
- `sales.invoice.overdue`
- `sales.invoice.cancelled`

### Credit Note Events
- `sales.credit_note.issued`
- `sales.credit_note.settled`

## Security

- **Authentication**: JWT tokens validated against JWKS
- **Authorization**: Role-based access control (RBAC)
- **Tenant Isolation**: Multi-tenant architecture with tenant IDs
- **Request Validation**: Zod schemas for all inputs
- **Rate Limiting**: Configurable request limits

## Observability

- **Tracing**: OpenTelemetry distributed tracing
- **Logging**: Structured logging with Pino
- **Metrics**: Health checks and readiness probes
- **Request IDs**: Correlation IDs for request tracking

## Testing

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

## API Documentation

When running the server, visit `http://localhost:3001/docs` for interactive OpenAPI documentation.

## Contributing

1. Follow the existing code style and architecture patterns
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting PRs

## License

This project is part of the VALEO NeuroERP system. See the main project license for details.