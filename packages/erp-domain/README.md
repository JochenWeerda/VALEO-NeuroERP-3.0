# VALEO NeuroERP 3.0 - ERP Domain Service

## Overview

The ERP Domain Service is a core component of the VALEO NeuroERP 3.0 MSOA (Modular Service-Oriented Architecture) system. It handles all Enterprise Resource Planning functionality including product management, inventory control, order processing, and financial operations.

## Architecture

This service follows Domain-Driven Design (DDD) principles with clear separation of concerns:

- **Domain Layer**: Business logic and domain entities
- **Application Layer**: Use cases and command/query handlers
- **Infrastructure Layer**: External concerns (database, messaging, etc.)
- **Presentation Layer**: API controllers and DTOs

## Features

### Product Management
- Product catalog management
- SKU and pricing management
- Product lifecycle management
- Category and attribute management

### Inventory Management
- Real-time inventory tracking
- Automatic reorder point alerts
- Reservation system for orders
- Multi-warehouse support

### Order Processing
- Order creation and management
- Order status tracking
- Inventory reservation and release
- Order fulfillment workflow

### Financial Integration
- Order value calculations
- Tax computation
- Revenue tracking
- Financial reporting data

## API Boundary

`packages/erp-domain` exposes order logic as in-process domain commands and
queries for tests and potential BFF integration. It does **not** provide public
Order REST endpoints.

The public UI/API route for sales orders is owned by the Python FastAPI backend:

- `GET /api/v1/sales/orders` - List sales orders
- `POST /api/v1/sales/orders` - Create sales order
- `GET /api/v1/sales/orders/{id}` - Get sales order details
- `PUT /api/v1/sales/orders/{id}` - Update sales order
- `DELETE /api/v1/sales/orders/{id}` - Delete sales order
- `POST /api/v1/sales/orders/{id}/print` - Record print action
- `POST /api/v1/sales/orders/{id}/post` - Post sales order

The bootstrap invariant is covered by
[`tests/integration/erp-bootstrap-orders.spec.ts`](tests/integration/erp-bootstrap-orders.spec.ts):
`ERP_DOMAIN_SERVICE_TOKENS.controller` remains unregistered.

## Package-Local API Examples

### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `GET /api/products/:id` - Get product details
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product

### Inventory
- `GET /api/inventory` - Get inventory levels
- `PUT /api/inventory/:productId` - Update inventory
- `POST /api/inventory/:productId/reserve` - Reserve inventory
- `POST /api/inventory/:productId/release` - Release inventory

## Domain Events

The service publishes the following domain events:

- `ProductCreated`
- `ProductUpdated`
- `InventoryUpdated`
- `InventoryReserved`
- `InventoryReleased`
- `OrderCreated`
- `OrderStatusUpdated`
- `OrderCancelled`

## Dependencies

### Internal Services
- Service Registry (for service discovery)
- Service Bus (for event publishing)
- Shared packages (@packages/data-models, @packages/utilities)

### External Services
- PostgreSQL database
- Redis cache
- RabbitMQ message broker

## Configuration

Environment variables:

```bash
NODE_ENV=production
SERVICE_NAME=erp-service
SERVICE_PORT=3002
SERVICE_REGISTRY_URL=http://service-registry:3000
SERVICE_BUS_URL=amqp://rabbitmq:5672
DATABASE_URL=postgresql://user:password@host:port/database
# Optional: preferred by tools/migration/run_sql_migration.ts for ERP SQL
ERP_DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port
# Dev/test tenant fallback only (see ADR M-01)
# ERP_ALLOW_MISSING_TENANT=1
# ERP_DEV_TENANT_ID=my-tenant
```

### Multi-tenancy (finance master data & purchase orders)

PostgreSQL schema **`finanz`** (accounts, creditors, debtors, bank accounts, postings) is isolated by **`tenant_id`**. Apply SQL migrations **`migrations/sql/erp/001_finance_core.sql`** then **`003_finanz_tenant_id.sql`** before running the finance APIs (see **`docs/erp-finanz-multitenancy.md`** and **`migrations/sql/erp/README.md`**). Express handlers use **`resolveTenantId`** (`src/presentation/utils/request-context.ts`) and the finance routers (`buildFinanz*Router`). Purchase-order **GET by ID** and mutations are scoped by **`tenant_id`** as documented in the same guide.

Run migrations from the **repository root** (connection string precedence: `ERP_DATABASE_URL`, then `DATABASE_URL`, then `CRM_DATABASE_URL`):

```bash
pnpm migrate:erp-finanz

# Equivalent:
npx ts-node tools/migration/run_sql_migration.ts \
  --file migrations/sql/erp/001_finance_core.sql \
  --file migrations/sql/erp/003_finanz_tenant_id.sql
```

The migration runner resolves `.env` from the repo root **and** optionally `./.env` in the working directory (see [`tools/migration/run_sql_migration.ts`](../../tools/migration/run_sql_migration.ts)).

## Development

### Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.12+

### Setup
```bash
npm install
npm run build
npm run dev
```

### Testing
```bash
cd packages/erp-domain
pnpm test             # npm test equivalent; Jest via jest.config.cjs
pnpm run test:coverage
```

From the **repository root**:

```bash
pnpm test:erp-domain    # alias: pnpm --filter @valero-neuroerp/erp-domain test
```

Tests are **`*.spec.ts`** under [`tests/`](tests/); handlers and DI wiring are covered (e.g. [`tests/integration/erp-bootstrap-orders.spec.ts`](tests/integration/erp-bootstrap-orders.spec.ts), `ERP_DOMAIN_SERVICE_TOKENS` in [`src/bootstrap.ts`](src/bootstrap.ts)).

### Docker
```bash
docker build -t valero-neuroerp/erp-service .
docker run -p 3002:3002 valero-neuroerp/erp-service
```

## Deployment

The service is deployed using the provided docker-compose.yml file as part of the larger VALEO NeuroERP 3.0 system.

## Monitoring

- Health checks available at `/health`
- Metrics exposed via Prometheus endpoint
- Structured logging with correlation IDs
- Distributed tracing support

## Security

- JWT-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## Contributing

Follow the VALEO NeuroERP 3.0 development guidelines:

1. Create feature branch from `main`
2. Implement TDD approach
3. Ensure 85%+ test coverage
4. Pass all linting rules
5. Create pull request with description
6. Require code review approval

## License

MIT License - VALEO NeuroERP Team
