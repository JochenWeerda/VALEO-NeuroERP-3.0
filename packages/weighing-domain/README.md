***REMOVED*** Weighing Domain Service

A comprehensive domain service for agricultural weighing operations in the VALEO NeuroERP system. This service handles automated weighing processes, traffic control, ANPR integration, and real-time analytics for agricultural trading operations.

***REMOVED******REMOVED*** 🚀 Features

***REMOVED******REMOVED******REMOVED*** Core Functionality
- **Automated Weighing Operations**: Complete ticket lifecycle management
- **Multi-Modal Weighing**: Vehicle, container, silo, and manual weighing
- **Real-Time Weight Calculation**: Automatic net weight computation with tolerance checking
- **Quality Assurance**: Configurable tolerance limits and compliance validation

***REMOVED******REMOVED******REMOVED*** Traffic Control & Logistics
- **Gate Management**: Automated gate sequencing and priority handling
- **Slot Scheduling**: Time-window based appointment system
- **Traffic Flow Optimization**: Real-time queue management and bottleneck detection

***REMOVED******REMOVED******REMOVED*** ANPR Integration
- **Automatic Number Plate Recognition**: Camera integration with confidence scoring
- **Vehicle Lookup**: Automatic contract and order matching
- **Ticket Suggestions**: AI-powered ticket creation from license plate data

***REMOVED******REMOVED******REMOVED*** Analytics & Reporting
- **Real-Time KPIs**: Wait times, service efficiency, throughput metrics
- **Volume Analytics**: Daily/weekly/monthly weighing statistics
- **Performance Monitoring**: Gate utilization and operator efficiency
- **Compliance Reporting**: Tolerance violations and quality metrics

***REMOVED******REMOVED*** 🏗️ Architecture

***REMOVED******REMOVED******REMOVED*** Domain-Driven Design
- **Entities**: WeighingTicket, Slot, ANPRRecord, WaitLog, AuditLog
- **Services**: WeighingService, TrafficControlService, ANPRService
- **Events**: Domain events for system integration
- **Contracts**: Zod schemas for API validation

***REMOVED******REMOVED******REMOVED*** Technology Stack
- **Runtime**: Node.js 20 with TypeScript
- **Framework**: Fastify with OpenAPI/Swagger
- **Database**: PostgreSQL with Drizzle ORM
- **Events**: NATS/Kafka for event publishing
- **Security**: JWT with JWKS, tenant isolation, RBAC
- **Observability**: OpenTelemetry tracing and structured logging

***REMOVED******REMOVED*** 📋 API Reference

***REMOVED******REMOVED******REMOVED*** Base URL
```
http://localhost:3005/weighing/api/v1
```

***REMOVED******REMOVED******REMOVED*** Core Endpoints

***REMOVED******REMOVED******REMOVED******REMOVED*** Weighing Tickets
```http
POST   /tickets              ***REMOVED*** Create weighing ticket
GET    /tickets/:id          ***REMOVED*** Get ticket details
GET    /tickets              ***REMOVED*** List tickets with filtering
PATCH  /tickets/:id          ***REMOVED*** Update ticket
DELETE /tickets/:id          ***REMOVED*** Delete draft ticket

POST   /tickets/:id/weigh    ***REMOVED*** Record weight measurement
POST   /tickets/:id/complete ***REMOVED*** Complete ticket
POST   /tickets/:id/cancel   ***REMOVED*** Cancel ticket

GET    /tickets/active       ***REMOVED*** Get active tickets
GET    /tickets/completed-today ***REMOVED*** Get today's completions
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Traffic Control
```http
POST   /slots                ***REMOVED*** Schedule time slot
GET    /slots                ***REMOVED*** List slots
PATCH  /slots/:id            ***REMOVED*** Update slot status
```

***REMOVED******REMOVED******REMOVED******REMOVED*** ANPR Operations
```http
POST   /anpr/records         ***REMOVED*** ANPR camera input
GET    /anpr/records/:id     ***REMOVED*** Get ANPR record
POST   /anpr/:id/assign      ***REMOVED*** Assign to ticket
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Analytics
```http
GET    /analytics/volume     ***REMOVED*** Volume statistics
GET    /analytics/performance ***REMOVED*** Performance KPIs
GET    /analytics/wait-times ***REMOVED*** Wait time analysis
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites
- Node.js 20+
- PostgreSQL 15+
- NATS or Kafka (optional)

***REMOVED******REMOVED******REMOVED*** Installation

1. **Clone and install dependencies:**
```bash
cd packages/weighing-domain
npm install
```

2. **Set up environment:**
```bash
cp .env.example .env
***REMOVED*** Edit .env with your configuration
```

3. **Set up database:**
```bash
npm run migrate:up
```

4. **Start development server:**
```bash
npm run dev
```

The API will be available at `http://localhost:3005` with documentation at `/documentation`.

***REMOVED******REMOVED******REMOVED*** Docker Deployment

```bash
***REMOVED*** Build image
docker build -t weighing-domain .

***REMOVED*** Run with PostgreSQL
docker run -p 3005:3005 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  weighing-domain
```

***REMOVED******REMOVED*** 🔧 Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3005` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |
| `JWT_SECRET` | JWT signing secret | Required |
| `LOG_LEVEL` | Logging level | `info` |

***REMOVED******REMOVED******REMOVED*** Database Schema

The service uses PostgreSQL with the following main tables:
- `weighing_tickets` - Core weighing operations
- `slots` - Time slot scheduling
- `anpr_records` - License plate recognition
- `wait_logs` - Traffic flow analytics
- `audit_logs` - Compliance and audit trail

***REMOVED******REMOVED*** 🧪 Testing

***REMOVED******REMOVED******REMOVED*** Unit Tests
```bash
npm run test
```

***REMOVED******REMOVED******REMOVED*** Integration Tests
```bash
npm run test:e2e
```

***REMOVED******REMOVED******REMOVED*** Coverage Report
```bash
npm run test:coverage
```

***REMOVED******REMOVED*** 📊 Business Logic

***REMOVED******REMOVED******REMOVED*** Weighing Process Flow
1. **Ticket Creation**: Manual or ANPR-triggered
2. **Gross Weight**: First weighing measurement
3. **Tare Weight**: Second weighing measurement
4. **Net Calculation**: Automatic net weight computation
5. **Tolerance Check**: Quality assurance validation
6. **Completion**: Final status update

***REMOVED******REMOVED******REMOVED*** Tolerance Validation
```typescript
const tolerance = (expectedWeight * tolerancePercent) / 100;
const isWithinTolerance = Math.abs(netWeight - expectedWeight) <= tolerance;
```

***REMOVED******REMOVED******REMOVED*** Ticket Numbering
Format: `{PREFIX}-{DATE}-{SEQUENCE}`
Example: `WT-20241201-0001`

***REMOVED******REMOVED*** 🔐 Security

***REMOVED******REMOVED******REMOVED*** Authentication
- JWT tokens with JWKS validation
- Role-based access control (RBAC)
- Tenant isolation middleware

***REMOVED******REMOVED******REMOVED*** Authorization
- Resource-level permissions
- Operation-specific access control
- Audit logging for all operations

***REMOVED******REMOVED*** 📈 Monitoring & Observability

***REMOVED******REMOVED******REMOVED*** Health Checks
- `/health` - Basic health status
- `/ready` - Database connectivity check
- `/live` - Application liveness

***REMOVED******REMOVED******REMOVED*** Metrics
- Request/response times
- Error rates
- Database query performance
- Event publishing success rates

***REMOVED******REMOVED******REMOVED*** Logging
- Structured JSON logging
- Request ID tracing
- Error correlation
- Performance monitoring

***REMOVED******REMOVED*** 🔗 Integration Points

***REMOVED******REMOVED******REMOVED*** BFF Layer
- **bff-web**: Dashboard and management interface
- **bff-mobile**: Gate scanner and status updates
- **bff-back-office**: Reporting and analytics

***REMOVED******REMOVED******REMOVED*** Other Domains
- **Contracts**: Order and contract references
- **Inventory**: Weight-based inventory updates
- **Analytics**: KPI data aggregation
- **Logistics**: Route planning integration

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

**Database Connection Failed**
```bash
***REMOVED*** Check PostgreSQL status
pg_isready -h localhost -p 5432

***REMOVED*** Verify connection string
psql $DATABASE_URL -c "SELECT 1"
```

**ANPR Not Working**
- Verify camera connectivity
- Check confidence thresholds
- Review ANPR service logs

**High Wait Times**
- Check slot scheduling
- Monitor gate utilization
- Review traffic patterns

***REMOVED******REMOVED*** 📚 Development

***REMOVED******REMOVED******REMOVED*** Project Structure
```
packages/weighing-domain/
├── src/
│   ├── app/                 ***REMOVED*** Fastify application
│   │   ├── routes/         ***REMOVED*** API route handlers
│   │   └── server.ts       ***REMOVED*** Main server file
│   ├── domain/             ***REMOVED*** Domain logic
│   │   ├── entities/       ***REMOVED*** Domain entities
│   │   └── services/       ***REMOVED*** Domain services
│   ├── infra/              ***REMOVED*** Infrastructure
│   │   ├── db/            ***REMOVED*** Database schema & migrations
│   │   ├── repo/          ***REMOVED*** Repository implementations
│   │   └── messaging/     ***REMOVED*** Event publishing
│   └── contracts/          ***REMOVED*** API contracts (Zod schemas)
├── tests/                  ***REMOVED*** Test suites
├── migrations/            ***REMOVED*** Database migrations
└── Dockerfile             ***REMOVED*** Container definition
```

***REMOVED******REMOVED******REMOVED*** Development Commands
```bash
***REMOVED*** Development
npm run dev              ***REMOVED*** Start with hot reload
npm run build           ***REMOVED*** TypeScript compilation
npm start               ***REMOVED*** Production start

***REMOVED*** Database
npm run migrate:gen     ***REMOVED*** Generate migrations
npm run migrate:up      ***REMOVED*** Run migrations
npm run db:studio       ***REMOVED*** Drizzle Studio

***REMOVED*** Testing
npm test                ***REMOVED*** Unit tests
npm run test:e2e        ***REMOVED*** Integration tests
npm run test:coverage   ***REMOVED*** Coverage report

***REMOVED*** Code Quality
npm run lint            ***REMOVED*** ESLint check
```

***REMOVED******REMOVED*** 🤝 Contributing

1. Follow the established code patterns
2. Add tests for new functionality
3. Update API documentation
4. Ensure type safety
5. Follow commit message conventions

***REMOVED******REMOVED*** 📄 License

This project is part of the VALEO NeuroERP system. See the main project license for details.

***REMOVED******REMOVED*** 🆘 Support

For support and questions:
- Check the API documentation at `/documentation`
- Review application logs
- Contact the development team

---

**Built with ❤️ for agricultural excellence**