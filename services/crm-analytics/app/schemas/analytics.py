"""Pydantic schemas for Analytics."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class DashboardBase(BaseModel):
    """Base dashboard schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="executive, sales, service, marketing, custom")
    config: dict = Field(..., description="Dashboard layout and widgets")
    filters: dict = Field(..., description="Default filters")


class DashboardCreate(DashboardBase):
    """Schema for creating dashboards."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class DashboardUpdate(BaseModel):
    """Schema for updating dashboards."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = None
    config: Optional[dict] = None
    filters: Optional[dict] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class Dashboard(DashboardBase):
    """Full dashboard schema."""
    id: UUID
    tenant_id: str
    is_active: bool = True
    is_default: bool = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    """Base report schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="sales_performance, customer_satisfaction, etc.")
    config: dict = Field(..., description="Report configuration")
    filters: dict = Field(..., description="Report filters")
    schedule: Optional[str] = Field(None, max_length=128)


class ReportCreate(ReportBase):
    """Schema for creating reports."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class ReportUpdate(BaseModel):
    """Schema for updating reports."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = None
    config: Optional[dict] = None
    filters: Optional[dict] = None
    schedule: Optional[str] = Field(None, max_length=128)
    updated_by: Optional[str] = Field(None, max_length=64)


class Report(ReportBase):
    """Full report schema."""
    id: UUID
    tenant_id: str
    results: Optional[dict] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    is_active: bool = True
    is_scheduled: bool = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MetricBase(BaseModel):
    """Base metric schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="count, sum, average, percentage, trend")
    entity: str = Field(..., max_length=64, description="customers, leads, cases, etc.")
    field: str = Field(..., max_length=64, description="Field to aggregate")
    aggregation: str = Field(..., max_length=32, description="sum, count, avg, etc.")
    filters: dict = Field(..., description="Metric filters")


class MetricCreate(MetricBase):
    """Schema for creating metrics."""
    tenant_id: str = Field(..., max_length=64)


class MetricUpdate(BaseModel):
    """Schema for updating metrics."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = None
    entity: Optional[str] = Field(None, max_length=64)
    field: Optional[str] = Field(None, max_length=64)
    aggregation: Optional[str] = Field(None, max_length=32)
    filters: Optional[dict] = None


class Metric(MetricBase):
    """Full metric schema."""
    id: UUID
    tenant_id: str
    value: Optional[float] = None
    trend: Optional[float] = None
    last_calculated: Optional[datetime] = None
    calculation_interval: int = 300
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PredictionBase(BaseModel):
    """Base prediction schema."""
    model_type: str = Field(..., max_length=64, description="lead_scoring, churn_prediction, etc.")
    entity_id: UUID
    entity_type: str = Field(..., max_length=64, description="customer, lead, case, etc.")
    score: float = Field(..., ge=0, le=1, description="Prediction score 0-1")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence 0-1")
    features: dict = Field(..., description="Input features used")


class PredictionCreate(PredictionBase):
    """Schema for creating predictions."""
    tenant_id: str = Field(..., max_length=64)


class Prediction(PredictionBase):
    """Full prediction schema."""
    id: UUID
    tenant_id: str
    prediction_date: datetime
    valid_until: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class ExportBase(BaseModel):
    """Base export schema."""
    name: str = Field(..., max_length=255)
    format: str = Field(..., max_length=16, description="csv, excel, pdf")
    config: dict = Field(..., description="Export configuration")


class ExportCreate(ExportBase):
    """Schema for creating exports."""
    tenant_id: str = Field(..., max_length=64)
    requested_by: Optional[str] = Field(None, max_length=64)


class Export(ExportBase):
    """Full export schema."""
    id: UUID
    tenant_id: str
    status: str = "pending"
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    requested_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardData(BaseModel):
    """Dashboard data response."""
    dashboard: Dashboard
    metrics: List[Metric]
    charts: dict = Field(..., description="Chart data for dashboard widgets")
    last_updated: datetime


class ReportData(BaseModel):
    """Report data response."""
    report: Report
    data: dict = Field(..., description="Report data")
    generated_at: datetime
    execution_time: float