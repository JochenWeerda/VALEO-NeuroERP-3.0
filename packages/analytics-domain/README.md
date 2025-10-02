# Analytics Domain

A comprehensive analytics and business intelligence domain service for the VALEO NeuroERP system, providing real-time KPIs, forecasting, reporting, and multi-dimensional data analysis capabilities.

## 🚀 Features

### Core Analytics Capabilities
- **Real-time KPI Calculation**: Contract positions, quality metrics, financial indicators
- **Predictive Forecasting**: Multiple ML models (ARIMA, Exponential Smoothing, Linear Regression)
- **Multi-format Reporting**: JSON, CSV, Excel, PDF report generation
- **Cube Analytics**: Multi-dimensional data analysis for business intelligence
- **Event-Driven Architecture**: Real-time data ingestion and processing

### Technical Features
- **Domain-Driven Design**: Clean architecture with aggregate roots and domain services
- **Event-First Approach**: All state changes emit domain events
- **Tenant Isolation**: Multi-tenant architecture with data segregation
- **Observability**: OpenTelemetry tracing, metrics, and structured logging
- **Security**: JWT authentication, RBAC, and tenant-based access control

## 📊 Analytics Components

### KPI Calculation Engine
Automated calculation of key performance indicators:
- **Contract KPIs**: Hedging ratios, position exposures, net risk
- **Quality KPIs**: Pass rates, moisture/protein averages, failure rates
- **Financial KPIs**: Revenue, margins, outstanding invoices, overdue amounts
- **Regulatory KPIs**: Eligibility rates, compliance metrics

### Forecasting Service
Advanced time series forecasting with multiple algorithms:
- **ARIMA**: Statistical forecasting model
- **Exponential Smoothing**: Trend-based forecasting
- **Linear Regression**: Trend analysis and prediction
- **External ML Models**: Integration with external ML services
- **Confidence Intervals**: Statistical uncertainty quantification

### Report Generation
Flexible report generation system:
- **Multiple Formats**: JSON, CSV, Excel, PDF
- **Asynchronous Processing**: Background report generation
- **Template System**: Configurable report templates
- **Scheduled Reports**: Automated report generation

### Cube Analytics
Multi-dimensional data analysis:
- **Contract Positions**: Commodity, time, and position analysis
- **Quality Statistics**: Test results, pass rates, trends
- **Regulatory Compliance**: Label eligibility, compliance tracking
- **Financial KPIs**: Revenue, costs, margins by dimensions

## 🏗️ Architecture

### Domain Layer
```
src/domain/
├── entities/          # Domain entities (KPI, Report, Forecast)
├── services/          # Domain services (KPI Engine, Forecasting)
├── events/            # Domain events and event factories
└── contracts/         # Zod schemas for domain validation
```

### Infrastructure Layer
```
src/infra/
├── db/                # Database schema and migrations
├── messaging/         # Event publishing (NATS/Kafka)
├── telemetry/         # OpenTelemetry tracing and metrics
└── security/          # JWT validation and security utilities
```

### Application Layer
```
src/app/
├── routes/            # REST API routes
├── middleware/        # Authentication, authorization, logging
└── server.ts          # Fastify server setup
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 13+
- NATS or Kafka (optional)
- OpenTelemetry Collector (optional)

### Installation

1. **Clone and install dependencies:**
```bash
cd packages/analytics-domain
npm install
```

2. **Environment configuration:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database setup:**
```bash
npm run migrate:up
```

4. **Start the service:**
```bash
npm run dev  # Development
npm start    # Production
```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t analytics-domain .
docker run -p 3005:3005 --env-file .env analytics-domain
```

## 📡 API Reference

### REST Endpoints

#### KPIs
- `GET /kpis` - List KPIs with filtering and pagination
- `GET /kpis/:id` - Get specific KPI
- `POST /kpis` - Create new KPI
- `PATCH /kpis/:id` - Update KPI
- `DELETE /kpis/:id` - Delete KPI
- `POST /kpis/recalculate` - Recalculate KPIs

#### Reports
- `GET /reports` - List reports
- `GET /reports/:id` - Get report metadata
- `GET /reports/:id/content` - Get report content
- `POST /reports` - Generate new report
- `DELETE /reports/:id` - Delete report

#### Forecasts
- `GET /forecasts` - List forecasts
- `GET /forecasts/:id` - Get specific forecast
- `GET /forecasts/:id/compare` - Compare forecast with actual data
- `POST /forecasts` - Generate new forecast
- `DELETE /forecasts/:id` - Delete forecast
- `DELETE /forecasts/cleanup` - Clean up old forecasts

#### Cubes
- `GET /cubes/contract-positions` - Contract position cube data
- `GET /cubes/weighing-volumes` - Weighing volume cube data
- `GET /cubes/quality` - Quality statistics cube data
- `GET /cubes/regulatory` - Regulatory compliance cube data
- `GET /cubes/finance` - Finance KPIs cube data
- `POST /cubes/refresh` - Refresh cube materialized views
- `GET /cubes/status` - Get cube refresh status

### Authentication

All API endpoints require JWT authentication with Bearer token:

```bash
curl -H "Authorization: Bearer <jwt-token>" \
     http://localhost:3005/kpis
```

### OpenAPI Documentation

Access the OpenAPI documentation at:
```
http://localhost:3005/documentation
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3005` |
| `POSTGRES_URL` | PostgreSQL connection URL | Required |
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |
| `JWKS_URL` | JWKS endpoint for JWT validation | Required |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry collector endpoint | `http://localhost:4318` |
| `EXTERNAL_ML_SERVICE_URL` | External ML service URL | Optional |

See `.env.example` for complete configuration options.

## 🧪 Testing

### Unit Tests
```bash
npm run test:unit
```

### Integration Tests
```bash
npm run test:integration
```

### End-to-End Tests
```bash
npm run test:e2e
```

### Test Coverage
```bash
npm run test:coverage
```

## 📊 Monitoring & Observability

### Metrics
- KPI calculation duration and success rates
- Forecast generation performance
- Report generation metrics
- Cube refresh operations
- API request/response metrics

### Tracing
- Distributed tracing with OpenTelemetry
- Request tracing through all service layers
- Database query tracing
- External service call tracing

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with context
- Performance logging

## 🔒 Security

### Authentication
- JWT-based authentication with JWKS validation
- Bearer token validation
- Token expiration handling

### Authorization
- Role-Based Access Control (RBAC)
- Permission-based access control
- Tenant isolation at database level

### Data Protection
- Tenant-specific data segregation
- Input validation with Zod schemas
- SQL injection prevention with parameterized queries

## 🚀 CI/CD

### Build Pipeline
```bash
npm run build
npm run test
npm run lint
```

### Docker Build
```bash
docker build -t analytics-domain .
```

### Database Migrations
```bash
npm run migrate:gen  # Generate migrations
npm run migrate:up   # Apply migrations
npm run migrate:down # Rollback migrations
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is part of the VALEO NeuroERP system. See the main project license for details.

## 🆘 Support

For support and questions:
- Create an issue in the project repository
- Contact the development team
- Check the documentation for common solutions

## 📈 Roadmap

### Planned Features
- [ ] Advanced ML model integration (TensorFlow, PyTorch)
- [ ] Real-time dashboard streaming
- [ ] Predictive maintenance analytics
- [ ] Advanced statistical analysis tools
- [ ] Custom KPI formula builder
- [ ] Report scheduling and distribution
- [ ] Data export to external BI tools
- [ ] Machine learning model training pipelines