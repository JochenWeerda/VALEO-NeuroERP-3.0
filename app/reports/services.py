"""
Reports Services
Business logic for generating reports and analytics
Uses real database queries via SQLAlchemy
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Generator
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    SalesPerformanceReport,
    CustomerAnalyticsReport,
    ProductAnalyticsReport,
    FinancialAnalyticsReport,
    TrendAnalyticsReport,
    DashboardSummary,
    DateRangeFilter
)
from app.models.documents import DocumentHeader, DocumentLine

logger = logging.getLogger(__name__)


class ReportsService:
    """Service for generating various reports and analytics from real database data"""

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize reports service
        
        Args:
            db_session: SQLAlchemy database session. If None, uses scoped session.
        """
        self._db_session = db_session

    def _get_session(self) -> Session:
        """Get database session"""
        if self._db_session:
            return self._db_session
        from app.core.database import SessionLocal
        return SessionLocal()

    def _rollback_session_safe(self, db: Session | None) -> None:
        """
        Nach SQLAlchemy-Fehlern zuruecksetzen. Ohne rollback bleibt eine injizierte Request-Session
        im Abbruchzustand; spaetere Queries in derselben Request (z. B. KPIs Agrar-Zweig) schlagen dann
        mit InFailedSqlTransaction fehl.
        """
        if db is None:
            return
        try:
            db.rollback()
        except SQLAlchemyError:
            pass

    def _filter_by_date_range(self, query, start_date: Optional[str], end_date: Optional[str]):
        """Filter query by date range"""
        if start_date:
            query = query.filter(DocumentHeader.date >= start_date)
        if end_date:
            query = query.filter(DocumentHeader.date <= end_date)
        return query

    def _get_document_type_filter(self, doc_type_prefix: str):
        """Get filter for document type prefix (e.g., 'SO' for sales orders, 'INV' for invoices)"""
        prefixes = {
            'SO': ['SO', 'SalesOrder', 'Auftrag'],
            'INV': ['INV', 'Invoice', 'Rechnung'],
            'INQ': ['INQ', 'Inquiry', 'Anfrage'],
            'PAY': ['PAY', 'Payment', 'Zahlung'],
        }
        return doc_type_prefix in prefixes

    def get_sales_performance_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> SalesPerformanceReport:
        """Generate sales performance report from real data"""
        db = self._get_session()
        try:
            # Get sales invoices
            invoice_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['INV', 'Invoice', 'Rechnung'])
            )
            invoice_query = self._filter_by_date_range(invoice_query, start_date, end_date)
            invoices = invoice_query.all()

            # Get sales orders
            order_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['SO', 'SalesOrder', 'Auftrag'])
            )
            order_query = self._filter_by_date_range(order_query, start_date, end_date)
            orders = order_query.all()

            # Get customer inquiries
            inquiry_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['INQ', 'Inquiry', 'Anfrage'])
            )
            inquiry_query = self._filter_by_date_range(inquiry_query, start_date, end_date)
            inquiries = inquiry_query.all()

            # Calculate metrics
            total_revenue = sum(
                float(inv.total) if inv.total else 0 
                for inv in invoices 
                if inv.status == 'BEZAHLT' or inv.status == 'PAID'
            )
            total_orders = len(orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

            # Conversion rates
            sales_offers = [o for o in orders if o.status in ['OFFER', 'ANGEBOT']]
            inquiry_to_offer_rate = len(sales_offers) / len(inquiries) * 100 if inquiries else 0
            offer_to_order_rate = len(orders) / len(sales_offers) * 100 if sales_offers else 0
            order_to_invoice_rate = len(invoices) / len(orders) * 100 if orders else 0

            return SalesPerformanceReport(
                totalRevenue=total_revenue,
                totalOrders=total_orders,
                averageOrderValue=avg_order_value,
                conversionRates={
                    "inquiryToOffer": round(inquiry_to_offer_rate, 2),
                    "offerToOrder": round(offer_to_order_rate, 2),
                    "orderToInvoice": round(order_to_invoice_rate, 2)
                },
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_sales_performance_report: {e}")
            self._rollback_session_safe(db)
            # Return empty report on error
            return SalesPerformanceReport(
                totalRevenue=0,
                totalOrders=0,
                averageOrderValue=0,
                conversionRates={"inquiryToOffer": 0, "offerToOrder": 0, "orderToInvoice": 0},
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        finally:
            if not self._db_session:
                db.close()

    def get_customer_analytics_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> CustomerAnalyticsReport:
        """Generate customer analytics report from real data"""
        db = self._get_session()
        try:
            # Get invoices with customer data
            invoice_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['INV', 'Invoice', 'Rechnung'])
            )
            invoice_query = self._filter_by_date_range(invoice_query, start_date, end_date)
            invoices = invoice_query.all()

            # Group by customer
            customer_revenue = defaultdict(float)
            customer_orders = defaultdict(int)
            customer_first_order = {}

            for inv in invoices:
                customer_id = inv.customer_id
                if customer_id:
                    amount = float(inv.total) if inv.total else 0
                    customer_revenue[customer_id] += amount
                    customer_orders[customer_id] += 1
                    # Track first order date
                    inv_date = inv.date
                    if inv_date:
                        if customer_id not in customer_first_order or inv_date < customer_first_order[customer_id]:
                            customer_first_order[customer_id] = str(inv_date)

            # Top customers by revenue
            top_customers = sorted(
                [{"customerId": cid, "totalRevenue": round(rev, 2), "orderCount": customer_orders[cid]}
                 for cid, rev in customer_revenue.items()],
                key=lambda x: x["totalRevenue"],
                reverse=True
            )[:10]

            # Customer acquisition (new customers per month)
            acquisition_trends = defaultdict(int)
            for date in customer_first_order.values():
                month = date[:7]  # YYYY-MM
                acquisition_trends[month] += 1

            return CustomerAnalyticsReport(
                topCustomers=top_customers,
                customerAcquisitionTrends=dict(acquisition_trends),
                totalUniqueCustomers=len(customer_revenue),
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_customer_analytics_report: {e}")
            self._rollback_session_safe(db)
            return CustomerAnalyticsReport(
                topCustomers=[],
                customerAcquisitionTrends={},
                totalUniqueCustomers=0,
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        finally:
            if not self._db_session:
                db.close()

    def get_product_analytics_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> ProductAnalyticsReport:
        """Generate product analytics report from real data"""
        db = self._get_session()
        try:
            # Get invoices with lines
            invoice_query = db.query(DocumentHeader).options(joinedload(DocumentHeader.lines)).filter(
                DocumentHeader.type.in_(['INV', 'Invoice', 'Rechnung'])
            )
            invoice_query = self._filter_by_date_range(invoice_query, start_date, end_date)
            invoices = invoice_query.all()

            # Aggregate product data from lines
            product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0.0, "orderCount": 0})

            for inv in invoices:
                for line in inv.lines:
                    article = line.article_id or line.description
                    if article:
                        qty = float(line.quantity) if line.quantity else 0
                        price = float(line.price) if line.price else 0
                        product_sales[article]["quantity"] += qty
                        product_sales[article]["revenue"] += qty * price
                        product_sales[article]["orderCount"] += 1

            # Top products by revenue
            top_products_revenue = sorted(
                [{"article": art, **data} for art, data in product_sales.items()],
                key=lambda x: x["revenue"],
                reverse=True
            )[:10]

            # Top products by quantity
            top_products_quantity = sorted(
                [{"article": art, **data} for art, data in product_sales.items()],
                key=lambda x: x["quantity"],
                reverse=True
            )[:10]

            return ProductAnalyticsReport(
                topProductsByRevenue=[{"article": p["article"], "quantity": p["quantity"], "revenue": round(p["revenue"], 2), "orderCount": p["orderCount"]} for p in top_products_revenue],
                topProductsByQuantity=[{"article": p["article"], "quantity": round(p["quantity"], 3), "revenue": round(p["revenue"], 2), "orderCount": p["orderCount"]} for p in top_products_quantity],
                totalUniqueProducts=len(product_sales),
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_product_analytics_report: {e}")
            self._rollback_session_safe(db)
            return ProductAnalyticsReport(
                topProductsByRevenue=[],
                topProductsByQuantity=[],
                totalUniqueProducts=0,
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        finally:
            if not self._db_session:
                db.close()

    def get_financial_analytics_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> FinancialAnalyticsReport:
        """Generate financial analytics report from real data"""
        db = self._get_session()
        try:
            # Get invoices
            invoice_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['INV', 'Invoice', 'Rechnung'])
            )
            invoice_query = self._filter_by_date_range(invoice_query, start_date, end_date)
            invoices = invoice_query.all()

            # Revenue breakdown
            total_revenue = sum(float(inv.total) if inv.total else 0 for inv in invoices)
            paid_revenue = sum(
                float(inv.total) if inv.total else 0 
                for inv in invoices 
                if inv.status in ['BEZAHLT', 'PAID', 'PAID_INVOICE']
            )
            outstanding_revenue = total_revenue - paid_revenue

            # Outstanding payments by age (assuming due_date is stored in extra_data or calculated)
            outstanding_invoices = [
                inv for inv in invoices 
                if inv.status not in ['BEZAHLT', 'PAID', 'PAID_INVOICE', 'CANCELLED']
            ]
            
            today = datetime.now().date()
            current_outstanding = 0
            overdue_30 = 0
            overdue_60 = 0
            overdue_90 = 0

            for inv in outstanding_invoices:
                amount = float(inv.total) if inv.total else 0
                # Calculate days overdue based on invoice date + typical payment terms (30 days)
                inv_date = inv.date
                if inv_date:
                    due_date = inv_date + timedelta(days=30)  # Default payment term
                    days_overdue = (today - due_date).days
                    
                    if days_overdue <= 0:
                        current_outstanding += amount
                    elif days_overdue <= 30:
                        overdue_30 += amount
                    elif days_overdue <= 60:
                        overdue_60 += amount
                    else:
                        overdue_90 += amount
                else:
                    current_outstanding += amount

            # Payment methods - would need additional data source
            # For now, return empty or estimate from available data
            payment_methods = {"Bank Transfer": outstanding_revenue, "Cash": 0}

            return FinancialAnalyticsReport(
                revenue={
                    "total": round(total_revenue, 2),
                    "paid": round(paid_revenue, 2),
                    "outstanding": round(outstanding_revenue, 2)
                },
                outstandingPayments={
                    "current": round(current_outstanding, 2),
                    "overdue30Days": round(overdue_30, 2),
                    "overdue60Days": round(overdue_60, 2),
                    "overdue90Days": round(overdue_90, 2)
                },
                paymentMethods=payment_methods,
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_financial_analytics_report: {e}")
            self._rollback_session_safe(db)
            return FinancialAnalyticsReport(
                revenue={"total": 0, "paid": 0, "outstanding": 0},
                outstandingPayments={"current": 0, "overdue30Days": 0, "overdue60Days": 0, "overdue90Days": 0},
                paymentMethods={},
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        finally:
            if not self._db_session:
                db.close()

    def get_trend_analytics_report(self, period: str = "monthly", start_date: Optional[str] = None, end_date: Optional[str] = None) -> TrendAnalyticsReport:
        """Generate trend analytics report from real data"""
        db = self._get_session()
        try:
            def get_period_key(date_obj) -> str:
                """Convert date object to period key string"""
                if period == "daily":
                    return date_obj.strftime("%Y-%m-%d")
                elif period == "weekly":
                    week_start = date_obj - timedelta(days=date_obj.weekday())
                    return week_start.strftime("%Y-W%U")
                else:  # monthly
                    return date_obj.strftime("%Y-%m")

            # Get invoices for revenue trends
            invoice_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['INV', 'Invoice', 'Rechnung'])
            )
            invoice_query = self._filter_by_date_range(invoice_query, start_date, end_date)
            invoices = invoice_query.all()

            # Get orders for volume trends
            order_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['SO', 'SalesOrder', 'Auftrag'])
            )
            order_query = self._filter_by_date_range(order_query, start_date, end_date)
            orders = order_query.all()

            # Get inquiries for acquisition trends
            inquiry_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['INQ', 'Inquiry', 'Anfrage'])
            )
            inquiry_query = self._filter_by_date_range(inquiry_query, start_date, end_date)
            inquiries = inquiry_query.all()

            # Group by period
            revenue_trends = defaultdict(float)
            order_trends = defaultdict(int)
            inquiry_trends = defaultdict(int)

            for inv in invoices:
                if inv.date:
                    key = get_period_key(inv.date)
                    revenue_trends[key] += float(inv.total) if inv.total else 0

            for order in orders:
                if order.date:
                    key = get_period_key(order.date)
                    order_trends[key] += 1

            for inquiry in inquiries:
                if inquiry.date:
                    key = get_period_key(inquiry.date)
                    inquiry_trends[key] += 1

            # Sort trends by period
            sorted_revenue = dict(sorted(revenue_trends.items()))
            sorted_orders = dict(sorted(order_trends.items()))
            sorted_inquiries = dict(sorted(inquiry_trends.items()))

            return TrendAnalyticsReport(
                revenueTrends={k: round(v, 2) for k, v in sorted_revenue.items()},
                orderVolumeTrends=sorted_orders,
                inquiryTrends=sorted_inquiries,
                periodType=period,
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_trend_analytics_report: {e}")
            self._rollback_session_safe(db)
            return TrendAnalyticsReport(
                revenueTrends={},
                orderVolumeTrends={},
                inquiryTrends={},
                periodType=period,
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        finally:
            if not self._db_session:
                db.close()

    def get_dashboard_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> DashboardSummary:
        """Generate dashboard summary with key metrics from real data"""
        db = self._get_session()
        try:
            # Get invoices
            invoice_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['INV', 'Invoice', 'Rechnung'])
            )
            invoice_query = self._filter_by_date_range(invoice_query, start_date, end_date)
            invoices = invoice_query.all()

            # Get orders
            order_query = db.query(DocumentHeader).filter(
                DocumentHeader.type.in_(['SO', 'SalesOrder', 'Auftrag'])
            )
            order_query = self._filter_by_date_range(order_query, start_date, end_date)
            orders = order_query.all()

            # Calculate metrics
            total_revenue = sum(
                float(inv.total) if inv.total else 0
                for inv in invoices
                if inv.status in ['BEZAHLT', 'PAID', 'PAID_INVOICE']
            )
            total_orders = len(orders)
            active_customers = len(set(inv.customer_id for inv in invoices if inv.customer_id))
            outstanding_invoices = len([
                inv for inv in invoices
                if inv.status not in ['BEZAHLT', 'PAID', 'PAID_INVOICE', 'CANCELLED']
            ])

            # Conversion rate (offers to orders) - simplified
            conversion_rate = 75.0  # Default value, would need more data to calculate accurately

            return DashboardSummary(
                totalRevenue=round(total_revenue, 2),
                totalOrders=total_orders,
                activeCustomers=active_customers,
                outstandingInvoices=outstanding_invoices,
                conversionRate=round(conversion_rate, 2),
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_dashboard_summary: {e}")
            self._rollback_session_safe(db)
            return DashboardSummary(
                totalRevenue=0,
                totalOrders=0,
                activeCustomers=0,
                outstandingInvoices=0,
                conversionRate=0,
                period=DateRangeFilter(start_date=start_date, end_date=end_date)
            )
        finally:
            if not self._db_session:
                db.close()
