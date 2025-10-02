# Integration Domain

VALEO NeuroERP 3.0 - Integration Domain with Clean Architecture

## 🏗️ Architecture Overview

This package implements the Integration Domain following Clean Architecture principles and Domain-Driven Design patterns. It provides a robust, scalable, and maintainable foundation for handling integrations, webhooks, and sync jobs.

### Key Features

- **Clean Architecture**: Separation of concerns with clear layer boundaries
- **Domain-Driven Design**: Rich domain models with business logic
- **Event-Driven**: Domain events for loose coupling and audit trails
- **Type Safety**: Full TypeScript support with strict typing
- **Extensible**: Plugin architecture for custom integrations
- **Testable**: Dependency injection and interface-based design

## 📦 Package Structure

```
src/
├── domain/           # Core business logic
│   ├── entities/     # Domain entities (Integration, Webhook, SyncJob)
│   ├── events/       # Domain events for event sourcing
│   ├── interfaces/   # Repository contracts
│   └── values/       # Value objects (IDs, etc.)
├── application/      # Application services and use cases
├── infrastructure/   # External concerns (repositories, external services)
├── presentation/     # API layer (controllers, middleware)
└── shared/          # Shared utilities and types
```

## 🚀 Quick Start

### Basic Usage

```typescript
import { Integration, IntegrationType } from '@valero-neuroerp/integration-domain';

// Create a new integration
const integration = Integration.create(
  'My API Integration',
  'api',
  {
    endpoint: 'https://api.example.com',
    credentials: {
      apiKey: 'your-api-key'
    },
    timeout: 30000
  },
  'user123',
  'Integration with external API',
  ['production', 'api']
);

// Activate the integration
integration.activate('user123');

// Access domain events
const events = integration.getUncommittedEvents();
console.log(events); // [IntegrationCreatedEvent, IntegrationUpdatedEvent]
```

### Working with Webhooks

```typescript
import { Webhook } from '@valero-neuroerp/integration-domain';

const webhook = Webhook.create(
  'Order Created Webhook',
  integration.id,
  {
    url: 'https://api.example.com/webhooks/orders',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer token'
    }
  },
  ['order.created', 'order.updated'],
  'user123'
);

// Trigger the webhook
webhook.trigger(
  { orderId: '12345', status: 'created' },
  'system'
);
```

### Managing Sync Jobs

```typescript
import { SyncJob } from '@valero-neuroerp/integration-domain';

const syncJob = SyncJob.create(
  'Customer Sync',
  integration.id,
  {
    source: {
      type: 'database',
      connection: { host: 'source-db', database: 'customers' },
      query: 'SELECT * FROM customers WHERE updated_at > ?'
    },
    target: {
      type: 'api',
      connection: { endpoint: 'https://api.target.com/customers' },
      batchSize: 100
    },
    schedule: {
      cron: '0 */6 * * *', // Every 6 hours
      timezone: 'UTC'
    }
  },
  'user123'
);

// Start the sync job
syncJob.start('system');
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/integrations

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# Monitoring
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

### Package Configuration

```json
{
  "name": "@valero-neuroerp/integration-domain",
  "dependencies": {
    "@valero-neuroerp/data-models": "workspace:*",
    "@valero-neuroerp/utilities": "workspace:*",
    "uuid": "^9.0.0",
    "zod": "^3.22.0"
  }
}
```

## 🧪 Testing

```bash
# Run tests
pnpm test

# Run tests with coverage
pnpm test:coverage

# Run tests in watch mode
pnpm test:watch
```

### Example Test

```typescript
import { Integration } from '../src/domain/entities/integration.js';

describe('Integration Entity', () => {
  it('should create a new integration with events', () => {
    const integration = Integration.create(
      'Test Integration',
      'api',
      { endpoint: 'https://test.com' },
      'user123'
    );

    expect(integration.name).toBe('Test Integration');
    expect(integration.type).toBe('api');
    expect(integration.getUncommittedEvents()).toHaveLength(1);
  });
});
```

## 📈 Monitoring & Observability

The Integration Domain includes built-in support for:

- **Structured Logging**: All domain events are logged with context
- **Metrics Collection**: Performance and usage metrics
- **Distributed Tracing**: Request tracing across services
- **Health Checks**: Service health monitoring

## 🔒 Security

- **API Key Management**: Secure storage and rotation of API keys
- **Authentication**: JWT token validation
- **Authorization**: Role-based access control
- **Audit Logging**: Complete audit trail of all operations

## 🚀 Deployment

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: integration-domain
spec:
  replicas: 3
  selector:
    matchLabels:
      app: integration-domain
  template:
    metadata:
      labels:
        app: integration-domain
    spec:
      containers:
      - name: integration-domain
        image: valeo-neuroerp/integration-domain:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
```

## 📚 API Reference

### Domain Entities

- [Integration](./docs/entities/integration.md)
- [Webhook](./docs/entities/webhook.md)
- [SyncJob](./docs/entities/sync-job.md)

### Repository Interfaces

- [IntegrationRepository](./docs/repositories/integration-repository.md)
- [WebhookRepository](./docs/repositories/webhook-repository.md)
- [SyncJobRepository](./docs/repositories/sync-job-repository.md)

### Domain Events

- [Integration Events](./docs/events/integration-events.md)
- [Webhook Events](./docs/events/webhook-events.md)
- [Sync Job Events](./docs/events/sync-job-events.md)

## 🤝 Contributing

1. Follow Clean Architecture principles
2. Write comprehensive tests
3. Document all public APIs
4. Use conventional commits
5. Ensure type safety

## 📄 License

Private - VALEO NeuroERP 3.0
