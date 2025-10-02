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

## API Endpoints

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

### Orders
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `GET /api/orders/:id` - Get order details
- `PUT /api/orders/:id/status` - Update order status

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
REDIS_URL=redis://host:port
```

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
npm test
npm run test:coverage
```

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