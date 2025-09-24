***REMOVED*** CRM Service - Customer Relationship Management

***REMOVED******REMOVED*** 🎯 Service Overview

The CRM Service is responsible for managing customer relationships, sales pipelines, and customer analytics within the VALEO NeuroERP 3.0 ecosystem.

***REMOVED******REMOVED*** 🏗️ Architecture

***REMOVED******REMOVED******REMOVED*** Domain Structure
```
src/
├── core/                   ***REMOVED*** Domain Core Logic
│   ├── entities/          ***REMOVED*** Customer, Contact, Opportunity
│   ├── value-objects/     ***REMOVED*** Email, Phone, Address
│   ├── domain-events/     ***REMOVED*** CustomerCreated, OpportunityWon
│   └── domain-services/   ***REMOVED*** CustomerValidationService
├── application/           ***REMOVED*** Application Layer
│   ├── commands/          ***REMOVED*** CreateCustomer, UpdateOpportunity
│   ├── queries/           ***REMOVED*** GetCustomer, ListOpportunities
│   ├── dto/               ***REMOVED*** CustomerDTO, OpportunityDTO
│   └── events/            ***REMOVED*** Application Event Handlers
├── infrastructure/        ***REMOVED*** Infrastructure Layer
│   ├── repositories/      ***REMOVED*** CustomerRepository, OpportunityRepository
│   ├── external-services/ ***REMOVED*** EmailService, SMSService
│   ├── messaging/         ***REMOVED*** Event Publisher, Event Subscriber
│   └── persistence/       ***REMOVED*** Database Layer
└── presentation/          ***REMOVED*** Presentation Layer
    ├── controllers/       ***REMOVED*** CustomerController, OpportunityController
    ├── middleware/        ***REMOVED*** Authentication, Validation
    └── views/             ***REMOVED*** Response Views
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.8+

***REMOVED******REMOVED******REMOVED*** Installation
```bash
***REMOVED*** Install dependencies
npm install

***REMOVED*** Set up environment variables
cp .env.example .env

***REMOVED*** Run database migrations
npm run migrate

***REMOVED*** Start development server
npm run dev
```

***REMOVED******REMOVED******REMOVED*** Environment Variables
```env
***REMOVED*** Service Configuration
SERVICE_PORT=8081
SERVICE_NAME=crm-service
SERVICE_REGISTRY_URL=http://service-registry:8761

***REMOVED*** Database Configuration
DATABASE_URL=postgresql://crm_user:crm_pass@crm-db:5432/crm_db
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10

***REMOVED*** Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=

***REMOVED*** Message Queue Configuration
RABBITMQ_URL=amqp://admin:admin123@service-bus:5672
RABBITMQ_EXCHANGE=crm.events

***REMOVED*** Security Configuration
JWT_SECRET=your-jwt-secret
JWT_EXPIRES_IN=24h
BCRYPT_ROUNDS=12

***REMOVED*** Logging Configuration
LOG_LEVEL=info
LOG_FORMAT=json
```

***REMOVED******REMOVED*** 📊 API Endpoints

***REMOVED******REMOVED******REMOVED*** Customer Management
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers/:id` - Get customer
- `PUT /api/v1/customers/:id` - Update customer
- `DELETE /api/v1/customers/:id` - Delete customer

***REMOVED******REMOVED******REMOVED*** Opportunity Management
- `GET /api/v1/opportunities` - List opportunities
- `POST /api/v1/opportunities` - Create opportunity
- `GET /api/v1/opportunities/:id` - Get opportunity
- `PUT /api/v1/opportunities/:id` - Update opportunity
- `DELETE /api/v1/opportunities/:id` - Delete opportunity

***REMOVED******REMOVED******REMOVED*** Contact Management
- `GET /api/v1/contacts` - List contacts
- `POST /api/v1/contacts` - Create contact
- `GET /api/v1/contacts/:id` - Get contact
- `PUT /api/v1/contacts/:id` - Update contact
- `DELETE /api/v1/contacts/:id` - Delete contact

***REMOVED******REMOVED*** 🧪 Testing

***REMOVED******REMOVED******REMOVED*** Unit Tests
```bash
npm run test:unit
```

***REMOVED******REMOVED******REMOVED*** Integration Tests
```bash
npm run test:integration
```

***REMOVED******REMOVED******REMOVED*** End-to-End Tests
```bash
npm run test:e2e
```

***REMOVED******REMOVED******REMOVED*** Performance Tests
```bash
npm run test:performance
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

***REMOVED******REMOVED******REMOVED*** Docker Compose
```bash
docker-compose up crm-service
```

***REMOVED******REMOVED*** 📈 Monitoring

***REMOVED******REMOVED******REMOVED*** Health Check
- **Endpoint:** `GET /health`
- **Response:** Service health status

***REMOVED******REMOVED******REMOVED*** Metrics
- **Endpoint:** `GET /metrics`
- **Response:** Prometheus metrics

***REMOVED******REMOVED******REMOVED*** Logs
- **Format:** JSON structured logging
- **Levels:** error, warn, info, debug
- **Correlation ID:** Request tracing

***REMOVED******REMOVED*** 🔒 Security

***REMOVED******REMOVED******REMOVED*** Authentication
- JWT token-based authentication
- Role-based access control (RBAC)
- API key authentication for service-to-service

***REMOVED******REMOVED******REMOVED*** Authorization
- Customer data access control
- Opportunity visibility rules
- Contact privacy controls

***REMOVED******REMOVED******REMOVED*** Data Protection
- Encryption at rest
- Encryption in transit
- GDPR compliance features

***REMOVED******REMOVED*** 📚 Documentation

***REMOVED******REMOVED******REMOVED*** API Documentation
- **OpenAPI Spec:** `/api/docs`
- **Swagger UI:** `/api/docs-ui`

***REMOVED******REMOVED******REMOVED*** Domain Documentation
- **Domain Model:** `docs/domain-model.md`
- **Business Rules:** `docs/business-rules.md`
- **Integration Guide:** `docs/integration.md`

***REMOVED******REMOVED*** 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

***REMOVED******REMOVED*** 📄 License

MIT License - see LICENSE file for details
