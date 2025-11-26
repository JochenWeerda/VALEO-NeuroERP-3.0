# CRM Analytics

Microservice providing advanced analytics, reporting dashboards, and business intelligence for the CRM system.

## Features

- **Real-time Dashboards**: Interactive dashboards with KPIs and metrics
- **Advanced Reporting**: Custom reports with filtering and export capabilities
- **Data Aggregation**: Unified analytics from all CRM services
- **Predictive Analytics**: Lead scoring and churn prediction models
- **Performance Metrics**: SLA compliance, conversion rates, customer satisfaction
- **Historical Trends**: Time-series analysis and forecasting

## API Endpoints

- `GET /api/v1/analytics/dashboard` - Main dashboard data
- `GET /api/v1/analytics/reports/{type}` - Predefined reports
- `POST /api/v1/analytics/reports/custom` - Custom report generation
- `GET /api/v1/analytics/metrics/{metric}` - Individual KPI data
- `GET /api/v1/analytics/predictive/{model}` - Predictive analytics results
- `POST /api/v1/analytics/export` - Data export functionality

## Database Tables

- `crm_analytics_dashboards` - Dashboard configurations
- `crm_analytics_reports` - Report definitions and results
- `crm_analytics_metrics` - KPI calculations and caching
- `crm_analytics_predictions` - Predictive model results
- `crm_analytics_exports` - Export job tracking

## Dependencies

- PostgreSQL for analytics data storage
- Redis for caching dashboard data
- Integration with all CRM services for data aggregation
- Optional: Data warehouse for large-scale analytics
