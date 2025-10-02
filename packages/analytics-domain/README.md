***REMOVED*** Analytics Domain

A comprehensive analytics and business intelligence domain service for the VALEO NeuroERP system, providing real-time KPIs, forecasting, reporting, and multi-dimensional data analysis capabilities.

***REMOVED******REMOVED*** 🚀 Features

***REMOVED******REMOVED******REMOVED*** Core Analytics Capabilities
- **Real-time KPI Calculation**: Contract positions, quality metrics, financial indicators
- **Predictive Forecasting**: Multiple ML models (ARIMA, Exponential Smoothing, Linear Regression)
- **Multi-format Reporting**: JSON, CSV, Excel, PDF report generation
- **Cube Analytics**: Multi-dimensional data analysis for business intelligence
- **Event-Driven Architecture**: Real-time data ingestion and processing

***REMOVED******REMOVED******REMOVED*** Technical Features
- **Domain-Driven Design**: Clean architecture with aggregate roots and domain services
- **Event-First Approach**: All state changes emit domain events
- **Tenant Isolation**: Multi-tenant architecture with data segregation
- **Observability**: OpenTelemetry tracing, metrics, and structured logging
- **Security**: JWT authentication, RBAC, and tenant-based access control

***REMOVED******REMOVED*** 📊 Analytics Components

***REMOVED******REMOVED******REMOVED*** KPI Calculation Engine
Automated calculation of key performance indicators:
- **Contract KPIs**: Hedging ratios, position exposures, net risk
- **Quality KPIs**: Pass rates, moisture/protein averages, failure rates
- **Financial KPIs**: Revenue, margins, outstanding invoices, overdue amounts
- **Regulatory KPIs**: Eligibility rates, compliance metrics

***REMOVED******REMOVED******REMOVED*** Forecasting Service
Advanced time series forecasting with multiple algorithms:
- **ARIMA**: Statistical forecasting model
- **Exponential Smoothing**: Trend-based forecasting
- **Linear Regression**: Trend analysis and prediction
- **External ML Models**: Integration with external ML services
- **Confidence Intervals**: Statistical uncertainty quantification

***REMOVED******REMOVED******REMOVED*** Report Generation
Flexible report generation system:
- **Multiple Formats**: JSON, CSV, Excel, PDF
- **Asynchronous Processing**: Background report generation
- **Template System**: Configurable report templates
- **Scheduled Reports**: Automated report generation

***REMOVED******REMOVED******REMOVED*** Cube Analytics
Multi-dimensional data analysis:
- **Contract Positions**: Commodity, time, and position analysis
- **Quality Statistics**: Test results, pass rates, trends
- **Regulatory Compliance**: Label eligibility, compliance tracking
- **Financial KPIs**: Revenue, costs, margins by dimensions

***REMOVED******REMOVED*** 🏗️ Architecture

***REMOVED******REMOVED******REMOVED*** Domain Layer
```
src/domain/
├── entities/          ***REMOVED*** Domain entities (KPI, Report, Forecast)
├── services/          ***REMOVED*** Domain services (KPI Engine, Forecasting)
├── events/            ***REMOVED*** Domain events and event factories
└── contracts/         ***REMOVED*** Zod schemas for domain validation
```

***REMOVED******REMOVED******REMOVED*** Infrastructure Layer
```
src/infra/
├── db/                ***REMOVED*** Database schema and migrations
├── messaging/         ***REMOVED*** Event publishing (NATS/Kafka)
├── telemetry/         ***REMOVED*** OpenTelemetry tracing and metrics
└── security/          ***REMOVED*** JWT validation and security utilities
```

***REMOVED******REMOVED******REMOVED*** Application Layer
```
src/app/
├── routes/            ***REMOVED*** REST API routes
├── middleware/        ***REMOVED*** Authentication, authorization, logging
└── server.ts          ***REMOVED*** Fastify server setup
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites
- Node.js 18+
- PostgreSQL 13+
- NATS or Kafka (optional)
- OpenTelemetry Collector (optional)

***REMOVED******REMOVED******REMOVED*** Installation

1. **Clone and install dependencies:**
```bash
cd packages/analytics-domain
npm install
```

2. **Environment configuration:**
```bash
cp .env.example .env
***REMOVED*** Edit .env with your configuration
```

3. **Database setup:**
```bash
npm run migrate:up
```

4. **Start the service:**
```bash
npm run dev  ***REMOVED*** Development
npm start    ***REMOVED*** Production
```

***REMOVED******REMOVED******REMOVED*** Docker Deployment

```bash
***REMOVED*** Build and run with Docker
docker build -t analytics-domain .
docker run -p 3005:3005 --env-file .env analytics-domain
```

***REMOVED******REMOVED*** 📡 API Reference

***REMOVED******REMOVED******REMOVED*** REST Endpoints

***REMOVED******REMOVED******REMOVED******REMOVED*** KPIs
- `GET /kpis` - List KPIs with filtering and pagination
- `GET /kpis/:id` - Get specific KPI
- `POST /kpis` - Create new KPI
- `PATCH /kpis/:id` - Update KPI
- `DELETE /kpis/:id` - Delete KPI
- `POST /kpis/recalculate` - Recalculate KPIs

***REMOVED******REMOVED******REMOVED******REMOVED*** Reports
- `GET /reports` - List reports
- `GET /reports/:id` - Get report metadata
- `GET /reports/:id/content` - Get report content
- `POST /reports` - Generate new report
- `DELETE /reports/:id` - Delete report

***REMOVED******REMOVED******REMOVED******REMOVED*** Forecasts
- `GET /forecasts` - List forecasts
- `GET /forecasts/:id` - Get specific forecast
- `GET /forecasts/:id/compare` - Compare forecast with actual data
- `POST /forecasts` - Generate new forecast
- `DELETE /forecasts/:id` - Delete forecast
- `DELETE /forecasts/cleanup` - Clean up old forecasts

***REMOVED******REMOVED******REMOVED******REMOVED*** Cubes
- `GET /cubes/contract-positions` - Contract position cube data
- `GET /cubes/weighing-volumes` - Weighing volume cube data
- `GET /cubes/quality` - Quality statistics cube data
- `GET /cubes/regulatory` - Regulatory compliance cube data
- `GET /cubes/finance` - Finance KPIs cube data
- `POST /cubes/refresh` - Refresh cube materialized views
- `GET /cubes/status` - Get cube refresh status

***REMOVED******REMOVED******REMOVED*** Authentication

All API endpoints require JWT authentication with Bearer token:

```bash
curl -H "Authorization: Bearer <jwt-token>" \
     http://localhost:3005/kpis
```

***REMOVED******REMOVED******REMOVED*** OpenAPI Documentation

Access the OpenAPI documentation at:
```
http://localhost:3005/documentation
```

***REMOVED******REMOVED*** 🔧 Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3005` |
| `POSTGRES_URL` | PostgreSQL connection URL | Required |
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |
| `JWKS_URL` | JWKS endpoint for JWT validation | Required |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry collector endpoint | `http://localhost:4318` |
| `EXTERNAL_ML_SERVICE_URL` | External ML service URL | Optional |

See `.env.example` for complete configuration options.

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

***REMOVED******REMOVED******REMOVED*** Test Coverage
```bash
npm run test:coverage
```

***REMOVED******REMOVED*** 📊 Monitoring & Observability

***REMOVED******REMOVED******REMOVED*** Metrics
- KPI calculation duration and success rates
- Forecast generation performance
- Report generation metrics
- Cube refresh operations
- API request/response metrics

***REMOVED******REMOVED******REMOVED*** Tracing
- Distributed tracing with OpenTelemetry
- Request tracing through all service layers
- Database query tracing
- External service call tracing

***REMOVED******REMOVED******REMOVED*** Logging
- Structured JSON logging
- Request/response logging
- Error tracking with context
- Performance logging

***REMOVED******REMOVED*** 🔒 Security

***REMOVED******REMOVED******REMOVED*** Authentication
- JWT-based authentication with JWKS validation
- Bearer token validation
- Token expiration handling

***REMOVED******REMOVED******REMOVED*** Authorization
- Role-Based Access Control (RBAC)
- Permission-based access control
- Tenant isolation at database level

***REMOVED******REMOVED******REMOVED*** Data Protection
- Tenant-specific data segregation
- Input validation with Zod schemas
- SQL injection prevention with parameterized queries

***REMOVED******REMOVED*** 🚀 CI/CD

***REMOVED******REMOVED******REMOVED*** Build Pipeline
```bash
npm run build
npm run test
npm run lint
```

***REMOVED******REMOVED******REMOVED*** Docker Build
```bash
docker build -t analytics-domain .
```

***REMOVED******REMOVED******REMOVED*** Database Migrations
```bash
npm run migrate:gen  ***REMOVED*** Generate migrations
npm run migrate:up   ***REMOVED*** Apply migrations
npm run migrate:down ***REMOVED*** Rollback migrations
```

***REMOVED******REMOVED*** 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

***REMOVED******REMOVED*** 📄 License

This project is part of the VALEO NeuroERP system. See the main project license for details.

***REMOVED******REMOVED*** 🆘 Support

For support and questions:
- Create an issue in the project repository
- Contact the development team
- Check the documentation for common solutions

***REMOVED******REMOVED*** 📈 Roadmap

***REMOVED******REMOVED******REMOVED*** Planned Features
- [ ] Advanced ML model integration (TensorFlow, PyTorch)
- [ ] Real-time dashboard streaming
- [ ] Predictive maintenance analytics
- [ ] Advanced statistical analysis tools
- [ ] Custom KPI formula builder
- [ ] Report scheduling and distribution
- [ ] Data export to external BI tools
- [ ] Machine learning model training pipelines