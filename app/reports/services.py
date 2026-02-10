"""
Reports Services
Business logic for generating reports and analytics
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    SalesPerformanceReport,
    CustomerAnalyticsReport,
    ProductAnalyticsReport,
    FinancialAnalyticsReport,
    TrendAnalyticsReport,
    DashboardSummary,
    DateRangeFilter
)

logger = logging.getLogger(__name__)


class ReportsService:
    """Service for generating various reports and analytics"""

    def __init__(self, db_store: Dict[str, dict]):
        self._db = db_store

    def _filter_by_date_range(self, docs: List[dict], start_date: Optional[str], end_date: Optional[str]) -> List[dict]:
        """Filter documents by date range"""
        if not start_date and not end_date:
            return docs

        filtered = []
        for doc in docs:
            doc_date = doc.get("date", "")
            if start_date and doc_date < start_date:
                continue
            if end_date and doc_date > end_date:
                continue
            filtered.append(doc)
        return filtered

    def get_sales_performance_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> SalesPerformanceReport:
        """Generate sales performance report"""
        docs = self._filter_by_date_range(list(self._db.values()), start_date, end_date)

        # Calculate metrics
        sales_orders = [d for d in docs if d.get("number", "").startswith("SO")]
        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]
        customer_inquiries = [d for d in docs if d.get("number", "").startswith("INQ")]
        sales_offers = [d for d in docs if d.get("number", "").startswith("SO") and "validUntil" in d]

        total_revenue = sum(inv.get("totalGross", 0) for inv in sales_invoices if inv.get("status") == "BEZAHLT")
        total_orders = len(sales_orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Conversion rates
        inquiry_to_offer_rate = len(sales_offers) / len(customer_inquiries) * 100 if customer_inquiries else 0
        offer_to_order_rate = len(sales_orders) / len(sales_offers) * 100 if sales_offers else 0
        order_to_invoice_rate = len(sales_invoices) / len(sales_orders) * 100 if sales_orders else 0

        return SalesPerformanceReport(
            totalRevenue=total_revenue,
            totalOrders=total_orders,
            averageOrderValue=avg_order_value,
            conversionRates={
                "inquiryToOffer": inquiry_to_offer_rate,
                "offerToOrder": offer_to_order_rate,
                "orderToInvoice": order_to_invoice_rate
            },
            period=DateRangeFilter(start_date=start_date, end_date=end_date)
        )

    def get_customer_analytics_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> CustomerAnalyticsReport:
        """Generate customer analytics report"""
        docs = self._filter_by_date_range(list(self._db.values()), start_date, end_date)
        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]

        # Group by customer
        customer_revenue = defaultdict(float)
        customer_orders = defaultdict(int)

        for inv in sales_invoices:
            customer_id = inv.get("customerId")
            if customer_id:
                customer_revenue[customer_id] += inv.get("totalGross", 0)
                customer_orders[customer_id] += 1

        # Top customers by revenue
        top_customers = sorted(
            [{"customerId": cid, "totalRevenue": rev, "orderCount": customer_orders[cid]}
             for cid, rev in customer_revenue.items()],
            key=lambda x: x["totalRevenue"],
            reverse=True
        )[:10]

        # Customer acquisition (new customers per month)
        customer_first_order = {}
        for inv in sales_invoices:
            cid = inv.get("customerId")
            date = inv.get("date")
            if cid and date:
                if cid not in customer_first_order or date < customer_first_order[cid]:
                    customer_first_order[cid] = date

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

    def get_product_analytics_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> ProductAnalyticsReport:
        """Generate product analytics report"""
        docs = self._filter_by_date_range(list(self._db.values()), start_date, end_date)
        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]

        # Aggregate product data
        product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0.0, "orderCount": 0})

        for inv in sales_invoices:
            for line in inv.get("lines", []):
                article = line.get("article")
                qty = line.get("qty", 0)
                price = line.get("price", 0)

                if article:
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
            topProductsByRevenue=top_products_revenue,
            topProductsByQuantity=top_products_quantity,
            totalUniqueProducts=len(product_sales),
            period=DateRangeFilter(start_date=start_date, end_date=end_date)
        )

    def get_financial_analytics_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> FinancialAnalyticsReport:
        """Generate financial analytics report"""
        docs = self._filter_by_date_range(list(self._db.values()), start_date, end_date)
        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]
        payments = [d for d in docs if d.get("number", "").startswith("PAY")]

        # Revenue breakdown
        total_revenue = sum(inv.get("totalGross", 0) for inv in sales_invoices)
        paid_revenue = sum(inv.get("totalGross", 0) for inv in sales_invoices if inv.get("status") == "BEZAHLT")
        outstanding_revenue = total_revenue - paid_revenue

        # Outstanding payments by age
        outstanding_invoices = [inv for inv in sales_invoices if inv.get("status") in ["VERSENDET", "ÜBERFÄLLIG"]]
        current_outstanding = 0
        overdue_30 = 0
        overdue_60 = 0
        overdue_90 = 0

        today = datetime.now().date()
        for inv in outstanding_invoices:
            due_date_str = inv.get("dueDate")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str).date()
                    days_overdue = (today - due_date).days
                    amount = inv.get("totalGross", 0)

                    if days_overdue <= 0:
                        current_outstanding += amount
                    elif days_overdue <= 30:
                        overdue_30 += amount
                    elif days_overdue <= 60:
                        overdue_60 += amount
                    else:
                        overdue_90 += amount
                except ValueError:
                    current_outstanding += inv.get("totalGross", 0)

        # Payment methods distribution
        payment_methods = defaultdict(float)
        for pay in payments:
            method = pay.get("paymentMethod", "Unknown")
            payment_methods[method] += pay.get("amount", 0)

        return FinancialAnalyticsReport(
            revenue={
                "total": total_revenue,
                "paid": paid_revenue,
                "outstanding": outstanding_revenue
            },
            outstandingPayments={
                "current": current_outstanding,
                "overdue30Days": overdue_30,
                "overdue60Days": overdue_60,
                "overdue90Days": overdue_90
            },
            paymentMethods=dict(payment_methods),
            period=DateRangeFilter(start_date=start_date, end_date=end_date)
        )

    def get_trend_analytics_report(self, period: str = "monthly", start_date: Optional[str] = None, end_date: Optional[str] = None) -> TrendAnalyticsReport:
        """Generate trend analytics report"""
        docs = self._filter_by_date_range(list(self._db.values()), start_date, end_date)
        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]
        sales_orders = [d for d in docs if d.get("number", "").startswith("SO")]
        customer_inquiries = [d for d in docs if d.get("number", "").startswith("INQ")]

        # Group by period
        def get_period_key(date_str: str) -> str:
            date = datetime.fromisoformat(date_str)
            if period == "daily":
                return date.strftime("%Y-%m-%d")
            elif period == "weekly":
                week_start = date - timedelta(days=date.weekday())
                return week_start.strftime("%Y-%W")
            else:  # monthly
                return date.strftime("%Y-%m")

        revenue_trends = defaultdict(float)
        order_trends = defaultdict(int)
        inquiry_trends = defaultdict(int)

        for inv in sales_invoices:
            date = inv.get("date")
            if date:
                key = get_period_key(date)
                revenue_trends[key] += inv.get("totalGross", 0)

        for order in sales_orders:
            date = order.get("date")
            if date:
                key = get_period_key(date)
                order_trends[key] += 1

        for inquiry in customer_inquiries:
            date = inquiry.get("date")
            if date:
                key = get_period_key(date)
                inquiry_trends[key] += 1

        # Sort trends by period
        sorted_revenue = dict(sorted(revenue_trends.items()))
        sorted_orders = dict(sorted(order_trends.items()))
        sorted_inquiries = dict(sorted(inquiry_trends.items()))

        return TrendAnalyticsReport(
            revenueTrends=sorted_revenue,
            orderVolumeTrends=sorted_orders,
            inquiryTrends=sorted_inquiries,
            periodType=period,
            period=DateRangeFilter(start_date=start_date, end_date=end_date)
        )

    def get_dashboard_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> DashboardSummary:
        """Generate dashboard summary with key metrics"""
        docs = self._filter_by_date_range(list(self._db.values()), start_date, end_date)

        sales_invoices = [d for d in docs if d.get("number", "").startswith("INV")]
        sales_orders = [d for d in docs if d.get("number", "").startswith("SO")]
        customer_inquiries = [d for d in docs if d.get("number", "").startswith("INQ")]
        sales_offers = [d for d in docs if d.get("number", "").startswith("SO") and "validUntil" in d]

        # Calculate metrics
        total_revenue = sum(inv.get("totalGross", 0) for inv in sales_invoices if inv.get("status") == "BEZAHLT")
        total_orders = len(sales_orders)
        active_customers = len(set(inv.get("customerId") for inv in sales_invoices if inv.get("customerId")))
        outstanding_invoices = len([inv for inv in sales_invoices if inv.get("status") in ["VERSENDET", "ÜBERFÄLLIG"]])

        # Conversion rate (offers to orders)
        conversion_rate = len(sales_orders) / len(sales_offers) * 100 if sales_offers else 0

        return DashboardSummary(
            totalRevenue=total_revenue,
            totalOrders=total_orders,
            activeCustomers=active_customers,
            outstandingInvoices=outstanding_invoices,
            conversionRate=conversion_rate,
            period=DateRangeFilter(start_date=start_date, end_date=end_date)
        )