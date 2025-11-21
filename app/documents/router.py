"""
Documents Router
API-Endpoints für Belegverwaltung & Folgebeleg-Erstellung
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, Callable, Any, List, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from .models import CustomerInquiry, SalesOffer, SalesOrder, SalesDelivery, SalesInvoice, PaymentReceived, FollowRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/documents", tags=["documents"])

# In-Memory Store (TODO: durch echte DB ersetzen)
_DB: Dict[str, dict] = {}


# --- CRUD Endpoints ---


@router.post("/customer_inquiry")
async def upsert_customer_inquiry(doc: CustomerInquiry) -> dict:
    """Erstellt oder aktualisiert Kundenanfrage"""
    try:
        # Status-Transition-Logik
        existing = _DB.get(doc.number)
        if existing:
            old_status = existing.get("status", "OFFEN")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "OFFEN": ["IN_BEARBEITUNG"],
                "IN_BEARBEITUNG": ["ANGEBOTEN", "ABGELEHNT"],
                "ANGEBOTEN": [],  # Final status
                "ABGELEHNT": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved customer inquiry: {doc.number} (status: {doc.status})")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save customer inquiry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales_offer")
async def upsert_sales_offer(doc: SalesOffer) -> dict:
    """Erstellt oder aktualisiert Verkaufsangebot"""
    try:
        # Berechne Gesamtbeträge falls nicht gesetzt
        if doc.subtotalNet == 0 and doc.lines:
            doc.subtotalNet = sum(
                (line.qty * line.price) for line in doc.lines if line.price
            )
            doc.totalTax = sum(
                (line.qty * line.price * line.vatRate / 100) for line in doc.lines if line.price
            )
            doc.totalGross = doc.subtotalNet + doc.totalTax

        # Status-Transition-Logik
        existing = _DB.get(doc.number)
        if existing:
            old_status = existing.get("status", "ENTWURF")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "ENTWURF": ["VERSENDET"],
                "VERSENDET": ["ANGENOMMEN", "ABGELEHNT"],
                "ANGENOMMEN": [],  # Final status
                "ABGELEHNT": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved sales offer: {doc.number} (status: {doc.status})")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales offer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales_order")
async def upsert_sales_order(doc: SalesOrder) -> dict:
    """Erstellt oder aktualisiert Verkaufsauftrag"""
    try:
        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved sales order: {doc.number}")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales_delivery")
async def upsert_sales_delivery(doc: SalesDelivery) -> dict:
    """Erstellt oder aktualisiert Lieferschein"""
    try:
        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved sales delivery: {doc.number}")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales delivery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales_invoice")
async def upsert_sales_invoice(doc: SalesInvoice) -> dict:
    """Erstellt oder aktualisiert Rechnung"""
    try:
        # Berechne Gesamtbeträge falls nicht gesetzt
        if doc.subtotalNet == 0 and doc.lines:
            doc.subtotalNet = sum(
                (line.qty * line.price) for line in doc.lines if line.price
            )
            doc.totalTax = sum(
                (line.qty * line.price * line.vatRate / 100) for line in doc.lines if line.price
            )
            doc.totalGross = doc.subtotalNet + doc.totalTax

        # Status-Transition-Logik
        existing = _DB.get(doc.number)
        if existing:
            old_status = existing.get("status", "ENTWURF")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "ENTWURF": ["VERSENDET"],
                "VERSENDET": ["BEZAHLT", "ÜBERFÄLLIG"],
                "BEZAHLT": [],  # Final status
                "ÜBERFÄLLIG": ["BEZAHLT"],  # Kann noch bezahlt werden
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved sales invoice: {doc.number} (status: {doc.status})")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment_received")
async def upsert_payment_received(doc: PaymentReceived) -> dict:
    """Erstellt oder aktualisiert Zahlungseingang"""
    try:
        # Status-Transition-Logik
        existing = _DB.get(doc.number)
        if existing:
            old_status = existing.get("status", "EINGEGANGEN")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "EINGEGANGEN": ["VERBUCHT"],
                "VERBUCHT": ["ABGEGLICHEN"],
                "ABGEGLICHEN": [],  # Final status
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved payment received: {doc.number} (status: {doc.status})")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save payment received: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_number}")
async def get_document(doc_number: str) -> dict:
    """Holt einzelnen Beleg"""
    doc = _DB.get(doc_number)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"ok": True, "data": doc}


# --- Belegfluss-Engine ---

# Flow-Matrix: (from_type, to_type) → Transformation-Function
FLOW: Dict[tuple[str, str], Callable[[dict], dict]] = {
    # Inquiry → Offer
    ("customer_inquiry", "sales_offer"): lambda payload: {
        "number": payload["number"].replace("INQ", "SO"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "status": "ENTWURF",
        "contactPerson": payload.get("contactPerson"),
        "validUntil": payload.get("deadline"),  # Verwende Deadline als validUntil
        "deliveryDate": None,
        "deliveryAddress": "",
        "paymentTerms": "net30",
        "notes": f"Aus Anfrage {payload['number']}: {payload.get('notes', '')}",
        "lines": payload.get("lines", []),
        "subtotalNet": 0,
        "totalTax": 0,
        "totalGross": 0,
    },
    # Order → Delivery
    ("sales_order", "delivery"): lambda payload: {
        "number": payload["number"].replace("SO", "DL"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload["number"],
        "deliveryAddress": payload.get("deliveryAddress", ""),
        "carrier": "dhl",
        "deliveryDate": payload.get("deliveryDate"),
        "status": "ENTWURF",
        "lines": payload.get("lines", []),
    },
    # Offer → Order
    ("sales_offer", "sales_order"): lambda payload: {
        "number": payload["number"].replace("SO", "SO"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "salesOfferId": payload["number"],
        "status": "ENTWURF",
        "contactPerson": payload.get("contactPerson"),
        "deliveryDate": payload.get("deliveryDate"),
        "deliveryAddress": payload.get("deliveryAddress"),
        "paymentTerms": payload.get("paymentTerms", "net30"),
        "notes": payload.get("notes", ""),
        "lines": payload.get("lines", []),
    },
    # Order → Invoice (direkt)
    ("sales_order", "invoice"): lambda payload: {
        "number": payload["number"].replace("SO", "INV"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload["number"],
        "paymentTerms": payload.get("paymentTerms", "net30"),
        "dueDate": payload["date"],  # TODO: +30 Tage berechnen
        "status": "ENTWURF",
        "lines": payload.get("lines", []),
        "subtotalNet": sum(
            (line.get("qty", 0) * line.get("price", 0))
            for line in payload.get("lines", [])
        ),
        "totalTax": sum(
            (line.get("qty", 0) * line.get("price", 0) * line.get("vatRate", 0) / 100)
            for line in payload.get("lines", [])
        ),
        "totalGross": sum(
            (line.get("qty", 0) * line.get("price", 0) * (1 + line.get("vatRate", 0) / 100))
            for line in payload.get("lines", [])
        ),
    },
    # Delivery → Invoice
    ("sales_delivery", "invoice"): lambda payload: {
        "number": payload["number"].replace("DL", "INV"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload.get("sourceOrder"),
        "sourceDelivery": payload["number"],
        "paymentTerms": "net30",
        "dueDate": payload["date"],  # TODO: +30 Tage berechnen
        "status": "ENTWURF",
        "lines": [
            {**line, "price": 0, "vatRate": 19}
            for line in payload.get("lines", [])
        ],
        "subtotalNet": sum(
            (line.get("qty", 0) * line.get("price", 0))
            for line in payload.get("lines", [])
        ),
        "totalTax": sum(
            (line.get("qty", 0) * line.get("price", 0) * line.get("vatRate", 19) / 100)
            for line in payload.get("lines", [])
        ),
        "totalGross": sum(
            (line.get("qty", 0) * line.get("price", 0) * (1 + line.get("vatRate", 19) / 100))
            for line in payload.get("lines", [])
        ),
    },
    # Invoice → PaymentReceived
    ("sales_invoice", "payment_received"): lambda payload: {
        "number": payload["number"].replace("INV", "PAY"),
        "date": payload["date"],
        "salesInvoiceId": payload["number"],
        "amount": payload.get("totalGross", 0),
        "paymentMethod": "Überweisung",
        "bankReference": None,
        "status": "EINGEGANGEN",
        "notes": f"Zahlung für Rechnung {payload['number']}",
    },
}


@router.post("/follow")
async def create_follow_up(req: FollowRequest) -> dict:
    """
    Erstellt Folgebeleg aus Quell-Beleg

    Args:
        req: FollowRequest mit fromType, toType, payload

    Returns:
        Transformierter Folgebeleg
    """
    try:
        flow_key = (req.fromType, req.toType)
        transform_fn = FLOW.get(flow_key)

        if not transform_fn:
            logger.warning(f"Flow not defined: {flow_key}")
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "flow not defined"},
            )

        # Transformation durchführen
        out = transform_fn(req.payload)

        logger.info(
            f"Created follow-up: {req.fromType} → {req.toType} (number: {out.get('number')})"
        )

        return {"ok": True, **out}
    except Exception as e:
        logger.error(f"Failed to create follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Lookup-Endpoints (für Autocomplete) ---


@router.get("/customers/search")
async def search_customers(q: str = "") -> dict:
    """Sucht Kunden (Autocomplete)"""
    # TODO: Echte DB-Suche
    mock_customers = [
        {"id": "CUST-001", "label": "Müller GmbH"},
        {"id": "CUST-002", "label": "Schmidt AG"},
        {"id": "CUST-003", "label": "Weber & Co."},
    ]

    filtered = [c for c in mock_customers if q.lower() in c["label"].lower()]
    return {"ok": True, "data": filtered}


@router.get("/articles/search")
async def search_articles(q: str = "") -> dict:
    """Sucht Artikel (Autocomplete)"""
    # TODO: Echte DB-Suche
    mock_articles = [
        {"id": "ART-001", "label": "Apfel Elstar"},
        {"id": "ART-002", "label": "Birne Conference"},
        {"id": "ART-003", "label": "Kartoffel festkochend"},
    ]

    filtered = [a for a in mock_articles if q.lower() in a["label"].lower()]
    return {"ok": True, "data": filtered}


# --- Analytics Endpoints ---

@router.get("/analytics/sales-performance")
async def get_sales_performance_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Sales Performance Analytics
    - Total revenue
    - Number of orders
    - Average order value
    - Conversion rates
    """
    try:
        # Filter documents by date range if provided
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

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

        return {
            "ok": True,
            "data": {
                "totalRevenue": total_revenue,
                "totalOrders": total_orders,
                "averageOrderValue": avg_order_value,
                "conversionRates": {
                    "inquiryToOffer": inquiry_to_offer_rate,
                    "offerToOrder": offer_to_order_rate,
                    "orderToInvoice": order_to_invoice_rate
                },
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get sales performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/customer-analytics")
async def get_customer_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Customer Analytics
    - Top customers by revenue
    - Customer acquisition trends
    - Customer retention metrics
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

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

        return {
            "ok": True,
            "data": {
                "topCustomers": top_customers,
                "customerAcquisitionTrends": dict(acquisition_trends),
                "totalUniqueCustomers": len(customer_revenue),
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get customer analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/product-analytics")
async def get_product_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Product Analytics
    - Top products by sales volume and revenue
    - Product performance trends
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

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

        return {
            "ok": True,
            "data": {
                "topProductsByRevenue": top_products_revenue,
                "topProductsByQuantity": top_products_quantity,
                "totalUniqueProducts": len(product_sales),
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get product analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/financial-analytics")
async def get_financial_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Financial Analytics
    - Revenue breakdown
    - Outstanding payments
    - Payment status overview
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

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

        return {
            "ok": True,
            "data": {
                "revenue": {
                    "total": total_revenue,
                    "paid": paid_revenue,
                    "outstanding": outstanding_revenue
                },
                "outstandingPayments": {
                    "current": current_outstanding,
                    "overdue30Days": overdue_30,
                    "overdue60Days": overdue_60,
                    "overdue90Days": overdue_90
                },
                "paymentMethods": dict(payment_methods),
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get financial analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/trend-analytics")
async def get_trend_analytics(
    period: str = Query("monthly", description="Aggregation period: daily, weekly, monthly"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """
    Trend Analytics
    - Revenue trends over time
    - Order volume trends
    - Customer acquisition trends
    """
    try:
        docs = list(_DB.values())
        if start_date:
            docs = [d for d in docs if d.get("date", "") >= start_date]
        if end_date:
            docs = [d for d in docs if d.get("date", "") <= end_date]

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

        return {
            "ok": True,
            "data": {
                "revenueTrends": sorted_revenue,
                "orderVolumeTrends": sorted_orders,
                "inquiryTrends": sorted_inquiries,
                "periodType": period,
                "period": {
                    "startDate": start_date,
                    "endDate": end_date
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get trend analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


