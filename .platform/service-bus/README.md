***REMOVED*** Service Bus - Core Message Bus

***REMOVED******REMOVED*** 🎯 Service Overview

The Service Bus is the core message broker for VALEO NeuroERP 3.0, providing reliable inter-service communication using AMQP protocol.

***REMOVED******REMOVED*** 🏗️ Architecture

***REMOVED******REMOVED******REMOVED*** Message Bus Components
```
src/
├── core/                   ***REMOVED*** Core Message Bus Logic
│   ├── exchanges/          ***REMOVED*** Exchange Definitions
│   ├── queues/             ***REMOVED*** Queue Definitions
│   ├── routing/            ***REMOVED*** Message Routing Logic
│   └── events/             ***REMOVED*** Event Definitions
├── infrastructure/          ***REMOVED*** Infrastructure Layer
│   ├── connections/        ***REMOVED*** AMQP Connections
│   ├── publishers/         ***REMOVED*** Message Publishers
│   ├── subscribers/        ***REMOVED*** Message Subscribers
│   └── monitoring/         ***REMOVED*** Message Monitoring
└── presentation/           ***REMOVED*** Management Interface
    ├── controllers/        ***REMOVED*** Management Controllers
    ├── middleware/         ***REMOVED*** Request Middleware
    └── views/              ***REMOVED*** Management Views
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites
- Node.js 18+
- RabbitMQ 3.8+

***REMOVED******REMOVED******REMOVED*** Installation
```bash
***REMOVED*** Install dependencies
npm install

***REMOVED*** Set up environment variables
cp .env.example .env

***REMOVED*** Start development server
npm run dev
```

***REMOVED******REMOVED******REMOVED*** Environment Variables
```env
***REMOVED*** Service Configuration
SERVICE_PORT=5672
MANAGEMENT_PORT=15672
SERVICE_NAME=service-bus

***REMOVED*** RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin123
RABBITMQ_VHOST=/

***REMOVED*** Exchange Configuration
DEFAULT_EXCHANGE=valero.events
DEAD_LETTER_EXCHANGE=valero.dlx

***REMOVED*** Queue Configuration
DEFAULT_QUEUE_TTL=3600000
MAX_RETRY_ATTEMPTS=3

***REMOVED*** Logging Configuration
LOG_LEVEL=info
LOG_FORMAT=json
```

***REMOVED******REMOVED*** 📊 Message Bus Features

***REMOVED******REMOVED******REMOVED*** Exchanges
- **valero.events** - Main event exchange
- **valero.commands** - Command exchange
- **valero.queries** - Query exchange
- **valero.dlx** - Dead letter exchange

***REMOVED******REMOVED******REMOVED*** Queues
- **crm.events** - CRM domain events
- **erp.events** - ERP domain events
- **analytics.events** - Analytics domain events
- **integration.events** - Integration domain events

***REMOVED******REMOVED******REMOVED*** Routing
- **Topic Routing** - Event-based routing
- **Direct Routing** - Command-based routing
- **Fanout Routing** - Broadcast routing

***REMOVED******REMOVED*** 🧪 Testing

***REMOVED******REMOVED******REMOVED*** Unit Tests
```bash
npm run test:unit
```

***REMOVED******REMOVED******REMOVED*** Integration Tests
```bash
npm run test:integration
```

***REMOVED******REMOVED*** 🐳 Docker

***REMOVED******REMOVED******REMOVED*** Build Image
```bash
npm run docker:build
```

***REMOVED******REMOVED******REMOVED*** Run Container
```bash
npm run docker:run
```

***REMOVED******REMOVED*** 📈 Monitoring

***REMOVED******REMOVED******REMOVED*** Health Check
- **Endpoint:** `GET /health`
- **Response:** Service health status

***REMOVED******REMOVED******REMOVED*** Metrics
- **Endpoint:** `GET /metrics`
- **Response:** Prometheus metrics

***REMOVED******REMOVED******REMOVED*** Management UI
- **URL:** `http://localhost:15672`
- **Username:** admin
- **Password:** admin123

***REMOVED******REMOVED*** 🔒 Security

***REMOVED******REMOVED******REMOVED*** Authentication
- AMQP authentication
- Management UI authentication
- API key authentication

***REMOVED******REMOVED******REMOVED*** Authorization
- Virtual host access control
- Exchange permissions
- Queue permissions

***REMOVED******REMOVED*** 📚 Documentation

***REMOVED******REMOVED******REMOVED*** API Documentation
- **OpenAPI Spec:** `/api/docs`
- **Swagger UI:** `/api/docs-ui`

***REMOVED******REMOVED******REMOVED*** Message Bus Documentation
- **Exchange Guide:** `docs/exchanges.md`
- **Queue Guide:** `docs/queues.md`
- **Routing Guide:** `docs/routing.md`

***REMOVED******REMOVED*** 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

***REMOVED******REMOVED*** 📄 License

MIT License - see LICENSE file for details
