# Weighing Domain Service

A comprehensive domain service for agricultural weighing operations in the VALEO NeuroERP system. This service handles automated weighing processes, traffic control, ANPR integration, and real-time analytics for agricultural trading operations.

## 🚀 Features

### Core Functionality
- **Automated Weighing Operations**: Complete ticket lifecycle management
- **Multi-Modal Weighing**: Vehicle, container, silo, and manual weighing
- **Real-Time Weight Calculation**: Automatic net weight computation with tolerance checking
- **Quality Assurance**: Configurable tolerance limits and compliance validation

### Traffic Control & Logistics
- **Gate Management**: Automated gate sequencing and priority handling
- **Slot Scheduling**: Time-window based appointment system
- **Traffic Flow Optimization**: Real-time queue management and bottleneck detection

### ANPR Integration
- **Automatic Number Plate Recognition**: Camera integration with confidence scoring
- **Vehicle Lookup**: Automatic contract and order matching
- **Ticket Suggestions**: AI-powered ticket creation from license plate data

### Analytics & Reporting
- **Real-Time KPIs**: Wait times, service efficiency, throughput metrics
- **Volume Analytics**: Daily/weekly/monthly weighing statistics
- **Performance Monitoring**: Gate utilization and operator efficiency
- **Compliance Reporting**: Tolerance violations and quality metrics

## 🏗️ Architecture

### Domain-Driven Design
- **Entities**: WeighingTicket, Slot, ANPRRecord, WaitLog, AuditLog
- **Services**: WeighingService, TrafficControlService, ANPRService
- **Events**: Domain events for system integration
- **Contracts**: Zod schemas for API validation

### Technology Stack
- **Runtime**: Node.js 20 with TypeScript
- **Framework**: Fastify with OpenAPI/Swagger
- **Database**: PostgreSQL with Drizzle ORM
- **Events**: NATS/Kafka for event publishing
- **Security**: JWT with JWKS, tenant isolation, RBAC
- **Observability**: OpenTelemetry tracing and structured logging

## 📋 API Reference

### Base URL
```
http://localhost:3005/weighing/api/v1
```

### Core Endpoints

#### Weighing Tickets
```http
POST   /tickets              # Create weighing ticket
GET    /tickets/:id          # Get ticket details
GET    /tickets              # List tickets with filtering
PATCH  /tickets/:id          # Update ticket
DELETE /tickets/:id          # Delete draft ticket

POST   /tickets/:id/weigh    # Record weight measurement
POST   /tickets/:id/complete # Complete ticket
POST   /tickets/:id/cancel   # Cancel ticket

GET    /tickets/active       # Get active tickets
GET    /tickets/completed-today # Get today's completions
```

#### Traffic Control
```http
POST   /slots                # Schedule time slot
GET    /slots                # List slots
PATCH  /slots/:id            # Update slot status
```

#### ANPR Operations
```http
POST   /anpr/records         # ANPR camera input
GET    /anpr/records/:id     # Get ANPR record
POST   /anpr/:id/assign      # Assign to ticket
```

#### Analytics
```http
GET    /analytics/volume     # Volume statistics
GET    /analytics/performance # Performance KPIs
GET    /analytics/wait-times # Wait time analysis
```

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- PostgreSQL 15+
- NATS or Kafka (optional)

### Installation

1. **Clone and install dependencies:**
```bash
cd packages/weighing-domain
npm install
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
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

### Docker Deployment

```bash
# Build image
docker build -t weighing-domain .

# Run with PostgreSQL
docker run -p 3005:3005 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  weighing-domain
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3005` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |
| `JWT_SECRET` | JWT signing secret | Required |
| `LOG_LEVEL` | Logging level | `info` |

### Database Schema

The service uses PostgreSQL with the following main tables:
- `weighing_tickets` - Core weighing operations
- `slots` - Time slot scheduling
- `anpr_records` - License plate recognition
- `wait_logs` - Traffic flow analytics
- `audit_logs` - Compliance and audit trail

## 🧪 Testing

### Unit Tests
```bash
npm run test
```

### Integration Tests
```bash
npm run test:e2e
```

### Coverage Report
```bash
npm run test:coverage
```

## 📊 Business Logic

### Weighing Process Flow
1. **Ticket Creation**: Manual or ANPR-triggered
2. **Gross Weight**: First weighing measurement
3. **Tare Weight**: Second weighing measurement
4. **Net Calculation**: Automatic net weight computation
5. **Tolerance Check**: Quality assurance validation
6. **Completion**: Final status update

### Tolerance Validation
```typescript
const tolerance = (expectedWeight * tolerancePercent) / 100;
const isWithinTolerance = Math.abs(netWeight - expectedWeight) <= tolerance;
```

### Ticket Numbering
Format: `{PREFIX}-{DATE}-{SEQUENCE}`
Example: `WT-20241201-0001`

## 🔐 Security

### Authentication
- JWT tokens with JWKS validation
- Role-based access control (RBAC)
- Tenant isolation middleware

### Authorization
- Resource-level permissions
- Operation-specific access control
- Audit logging for all operations

## 📈 Monitoring & Observability

### Health Checks
- `/health` - Basic health status
- `/ready` - Database connectivity check
- `/live` - Application liveness

### Metrics
- Request/response times
- Error rates
- Database query performance
- Event publishing success rates

### Logging
- Structured JSON logging
- Request ID tracing
- Error correlation
- Performance monitoring

## 🔗 Integration Points

### BFF Layer
- **bff-web**: Dashboard and management interface
- **bff-mobile**: Gate scanner and status updates
- **bff-back-office**: Reporting and analytics

### Other Domains
- **Contracts**: Order and contract references
- **Inventory**: Weight-based inventory updates
- **Analytics**: KPI data aggregation
- **Logistics**: Route planning integration

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Verify connection string
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

## 📚 Development

### Project Structure
```
packages/weighing-domain/
├── src/
│   ├── app/                 # Fastify application
│   │   ├── routes/         # API route handlers
│   │   └── server.ts       # Main server file
│   ├── domain/             # Domain logic
│   │   ├── entities/       # Domain entities
│   │   └── services/       # Domain services
│   ├── infra/              # Infrastructure
│   │   ├── db/            # Database schema & migrations
│   │   ├── repo/          # Repository implementations
│   │   └── messaging/     # Event publishing
│   └── contracts/          # API contracts (Zod schemas)
├── tests/                  # Test suites
├── migrations/            # Database migrations
└── Dockerfile             # Container definition
```

### Development Commands
```bash
# Development
npm run dev              # Start with hot reload
npm run build           # TypeScript compilation
npm start               # Production start

# Database
npm run migrate:gen     # Generate migrations
npm run migrate:up      # Run migrations
npm run db:studio       # Drizzle Studio

# Testing
npm test                # Unit tests
npm run test:e2e        # Integration tests
npm run test:coverage   # Coverage report

# Code Quality
npm run lint            # ESLint check
```

## 🤝 Contributing

1. Follow the established code patterns
2. Add tests for new functionality
3. Update API documentation
4. Ensure type safety
5. Follow commit message conventions

## 📄 License

This project is part of the VALEO NeuroERP system. See the main project license for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/documentation`
- Review application logs
- Contact the development team

---

**Built with ❤️ for agricultural excellence**