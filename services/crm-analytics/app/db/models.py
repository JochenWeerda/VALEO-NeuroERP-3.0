"""SQLAlchemy models for CRM Analytics Service."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text, Integer, Float, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ReportType(str, Enum):
    SALES_PERFORMANCE = "sales_performance"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    CASE_MANAGEMENT = "case_management"
    LEAD_CONVERSION = "lead_conversion"
    REVENUE_ANALYSIS = "revenue_analysis"
    CUSTOM = "custom"


class MetricType(str, Enum):
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    TREND = "trend"


class DashboardType(str, Enum):
    EXECUTIVE = "executive"
    SALES = "sales"
    SERVICE = "service"
    MARKETING = "marketing"
    CUSTOM = "custom"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  # noqa: E731


class Dashboard(Base):
    __tablename__ = "crm_analytics_dashboards"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[DashboardType] = mapped_column(
        SQLEnum(
            DashboardType,
            name="crm_analytics_dashboard_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    config: Mapped[dict] = mapped_column(JSON, nullable=False)  # Dashboard layout and widgets
    filters: Mapped[dict] = mapped_column(JSON, nullable=False)  # Default filters

    is_active: Mapped[bool] = mapped_column(default=True)
    is_default: Mapped[bool] = mapped_column(default=False)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    __tablename__ = "crm_analytics_reports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[ReportType] = mapped_column(
        SQLEnum(
            ReportType,
            name="crm_analytics_report_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    config: Mapped[dict] = mapped_column(JSON, nullable=False)  # Report configuration
    filters: Mapped[dict] = mapped_column(JSON, nullable=False)  # Report filters
    results: Mapped[dict | None] = mapped_column(JSON)  # Cached results

    schedule: Mapped[str | None] = mapped_column(String(128))  # Cron schedule for automated reports
    last_run: Mapped[datetime | None] = mapped_column(DateTime)
    next_run: Mapped[datetime | None] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_scheduled: Mapped[bool] = mapped_column(default=False)

    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Metric(Base):
    __tablename__ = "crm_analytics_metrics"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[MetricType] = mapped_column(
        SQLEnum(
            MetricType,
            name="crm_analytics_metric_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    entity: Mapped[str] = mapped_column(String(64), nullable=False)  # customers, leads, cases, etc.
    field: Mapped[str] = mapped_column(String(64), nullable=False)  # Field to aggregate
    aggregation: Mapped[str] = mapped_column(String(32), nullable=False)  # sum, count, avg, etc.

    filters: Mapped[dict] = mapped_column(JSON, nullable=False)  # Metric filters
    value: Mapped[float | None] = mapped_column(Float)  # Cached current value
    trend: Mapped[float | None] = mapped_column(Float)  # Trend percentage

    last_calculated: Mapped[datetime | None] = mapped_column(DateTime)
    calculation_interval: Mapped[int] = mapped_column(Integer, default=300)  # Seconds

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "crm_analytics_predictions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    model_type: Mapped[str] = mapped_column(String(64), nullable=False)  # lead_scoring, churn_prediction, etc.
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)  # Customer, lead, etc. ID
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # customer, lead, case, etc.

    score: Mapped[float] = mapped_column(Float, nullable=False)  # Prediction score 0-1
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # Model confidence 0-1
    features: Mapped[dict] = mapped_column(JSON, nullable=False)  # Input features used

    prediction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Export(Base):
    __tablename__ = "crm_analytics_exports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[str] = mapped_column(String(16), nullable=False)  # csv, excel, pdf
    config: Mapped[dict] = mapped_column(JSON, nullable=False)  # Export configuration

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")  # pending, processing, completed, failed
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_size: Mapped[int | None] = mapped_column(Integer)

    requested_by: Mapped[str | None] = mapped_column(String(64))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)