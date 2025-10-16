"""
Reports Models
Pydantic models for reporting and analytics
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DateRangeFilter(BaseModel):
    """Date range filter for reports"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class SalesPerformanceReport(BaseModel):
    """Sales Performance Report"""
    totalRevenue: float
    totalOrders: int
    averageOrderValue: float
    conversionRates: Dict[str, float]
    period: DateRangeFilter


class CustomerAnalyticsReport(BaseModel):
    """Customer Analytics Report"""
    topCustomers: List[Dict[str, Any]]
    customerAcquisitionTrends: Dict[str, int]
    totalUniqueCustomers: int
    period: DateRangeFilter


class ProductAnalyticsReport(BaseModel):
    """Product Analytics Report"""
    topProductsByRevenue: List[Dict[str, Any]]
    topProductsByQuantity: List[Dict[str, Any]]
    totalUniqueProducts: int
    period: DateRangeFilter


class FinancialAnalyticsReport(BaseModel):
    """Financial Analytics Report"""
    revenue: Dict[str, float]
    outstandingPayments: Dict[str, float]
    paymentMethods: Dict[str, float]
    period: DateRangeFilter


class TrendAnalyticsReport(BaseModel):
    """Trend Analytics Report"""
    revenueTrends: Dict[str, float]
    orderVolumeTrends: Dict[str, int]
    inquiryTrends: Dict[str, int]
    periodType: str
    period: DateRangeFilter


class ReportMetadata(BaseModel):
    """Report metadata"""
    reportType: str
    generatedAt: str = Field(default_factory=lambda: datetime.now().isoformat())
    filters: Dict[str, Any] = Field(default_factory=dict)
    dataPoints: int = 0


class ReportResponse(BaseModel):
    """Generic report response"""
    ok: bool = True
    metadata: ReportMetadata
    data: Dict[str, Any]


class DashboardSummary(BaseModel):
    """Dashboard summary with key metrics"""
    totalRevenue: float
    totalOrders: int
    activeCustomers: int
    outstandingInvoices: int
    conversionRate: float
    period: DateRangeFilter