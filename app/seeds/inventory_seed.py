"""
Inventory seed data for local development.
Creates a handful of articles and optional warehouse records so the POS search returns results immediately.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from app.core.database import SessionLocal
from app.infrastructure.models import Article, Warehouse

DEFAULT_TENANT = "system"

SEED_WAREHOUSES = [
    {
        "id": str(uuid4()),
        "tenant_id": DEFAULT_TENANT,
        "warehouse_code": "MAIN",
        "name": "Hauptlager",
        "address": "Industriestr. 12, 10115 Berlin",
        "city": "Berlin",
        "postal_code": "10115",
        "country": "DE",
        "warehouse_type": "standard",
        "total_capacity": Decimal("10000"),
        "used_capacity": Decimal("2500"),
    },
]

SEED_ARTICLES = [
    {
        "article_number": "A-001",
        "name": "Blumenerde Premium 20L",
        "category": "Erde",
        "barcode": "4001234567890",
        "sales_price": Decimal("12.99"),
        "current_stock": Decimal("45"),
    },
    {
        "article_number": "A-002",
        "name": "Tomatensamen BIO",
        "category": "Saatgut",
        "barcode": "4001234567891",
        "sales_price": Decimal("2.99"),
        "current_stock": Decimal("120"),
    },
    {
        "article_number": "A-003",
        "name": "Universaldünger 5kg",
        "category": "Dünger",
        "barcode": "4001234567892",
        "sales_price": Decimal("24.99"),
        "current_stock": Decimal("28"),
    },
    {
        "article_number": "A-004",
        "name": "Gartenschere Professional",
        "category": "Werkzeug",
        "barcode": "4001234567893",
        "sales_price": Decimal("19.99"),
        "current_stock": Decimal("15"),
    },
]


def seed_inventory() -> None:
    """Seed inventory articles and warehouses."""
    session = SessionLocal()
    try:
        _ensure_warehouses(session)
        _ensure_articles(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _ensure_warehouses(session) -> None:
    for data in SEED_WAREHOUSES:
        exists = (
            session.query(Warehouse)
            .filter(
                Warehouse.warehouse_code == data["warehouse_code"],
                Warehouse.tenant_id == DEFAULT_TENANT,
            )
            .first()
        )
        if exists:
            continue
        warehouse = Warehouse(
            id=data["id"],
            tenant_id=data["tenant_id"],
            warehouse_code=data["warehouse_code"],
            name=data["name"],
            address=data["address"],
            city=data["city"],
            postal_code=data["postal_code"],
            country=data["country"],
            warehouse_type=data["warehouse_type"],
            total_capacity=data["total_capacity"],
            used_capacity=data["used_capacity"],
            is_active=True,
        )
        session.add(warehouse)


def _ensure_articles(session) -> None:
    for data in SEED_ARTICLES:
        exists = (
            session.query(Article)
            .filter(
                Article.article_number == data["article_number"],
                Article.tenant_id == DEFAULT_TENANT,
            )
            .first()
        )
        if exists:
            continue
        article = Article(
            id=str(uuid4()),
            tenant_id=DEFAULT_TENANT,
            article_number=data["article_number"],
            name=data["name"],
            unit="PCS",
            category=data["category"],
            sales_price=data["sales_price"],
            current_stock=data["current_stock"],
            available_stock=data["current_stock"],
            reserved_stock=Decimal("0"),
            barcode=data.get("barcode"),
            description=data["name"],
            is_active=True,
        )
        session.add(article)


if __name__ == "__main__":
    seed_inventory()
