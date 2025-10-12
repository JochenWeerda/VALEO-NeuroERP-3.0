"""
Inventory seed data for local development.
Inserts a default tenant, warehouse, and a handful of articles if they do not exist.
"""

from __future__ import annotations

import json
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import text

from app.core.database import engine

TENANT_DOMAIN = "demo.local"
TENANT_NAME = "Demo Tenant"

WAREHOUSES = [
    {
        "warehouse_code": "MAIN",
        "name": "Hauptlager",
        "address": {
            "street": "Industriestr. 12",
            "postal_code": "10115",
            "city": "Berlin",
            "country": "DE",
        },
    }
]

ARTICLES = [
    {
        "article_number": "A-001",
        "name": "Blumenerde Premium 20L",
        "category": "Erde",
        "unit": "BAG",
        "sales_price": Decimal("12.99"),
        "current_stock": 45,
    },
    {
        "article_number": "A-002",
        "name": "Tomatensamen BIO",
        "category": "Saatgut",
        "unit": "PKG",
        "sales_price": Decimal("2.99"),
        "current_stock": 120,
    },
    {
        "article_number": "A-003",
        "name": "Universaldünger 5kg",
        "category": "Dünger",
        "unit": "BAG",
        "sales_price": Decimal("24.99"),
        "current_stock": 28,
    },
    {
        "article_number": "A-004",
        "name": "Gartenschere Professional",
        "category": "Werkzeug",
        "unit": "PCS",
        "sales_price": Decimal("19.99"),
        "current_stock": 15,
    },
]


def seed_inventory() -> None:
    with engine.begin() as conn:
        tenant_id = ensure_tenant(conn)
        ensure_warehouses(conn, tenant_id)
        ensure_articles(conn, tenant_id)

    print("Inventory seed completed.")


def ensure_tenant(conn) -> str:
    result = conn.execute(
        text(
            """
            SELECT id FROM domain_shared.tenants WHERE domain = :domain
            """
        ),
        {"domain": TENANT_DOMAIN},
    ).scalar()

    if result:
        return str(result)

    tenant_id = str(uuid4())
    conn.execute(
        text(
            """
            INSERT INTO domain_shared.tenants (id, name, domain, is_active, settings)
            VALUES (:id, :name, :domain, true, :settings)
            """
        ),
        {
            "id": tenant_id,
            "name": TENANT_NAME,
            "domain": TENANT_DOMAIN,
            "settings": json.dumps({"locale": "de-DE"}),
        },
    )
    return tenant_id


def ensure_warehouses(conn, tenant_id: str) -> None:
    for wh in WAREHOUSES:
        exists = conn.execute(
            text(
                """
                SELECT 1 FROM domain_inventory.warehouses
                WHERE warehouse_code = :code
                """
            ),
            {"code": wh["warehouse_code"]},
        ).scalar()

        if exists:
            continue

        conn.execute(
            text(
                """
                INSERT INTO domain_inventory.warehouses
                (id, tenant_id, warehouse_code, name, address, is_active)
                VALUES (:id, :tenant_id, :code, :name, :address, true)
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "code": wh["warehouse_code"],
                "name": wh["name"],
                "address": json.dumps(wh["address"]),
            },
        )


def ensure_articles(conn, tenant_id: str) -> None:
    for article in ARTICLES:
        exists = conn.execute(
            text(
                """
                SELECT 1 FROM domain_inventory.articles
                WHERE article_number = :number
                """
            ),
            {"number": article["article_number"]},
        ).scalar()

        if exists:
            continue

        conn.execute(
            text(
                """
                INSERT INTO domain_inventory.articles
                (id, tenant_id, article_number, name, category, unit,
                 sales_price, current_stock, is_active, description)
                VALUES
                (:id, :tenant_id, :article_number, :name, :category, :unit,
                 :sales_price, :current_stock, true, :description)
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "article_number": article["article_number"],
                "name": article["name"],
                "category": article["category"],
                "unit": article["unit"],
                "sales_price": str(article["sales_price"]),
                "current_stock": article["current_stock"],
                "description": article["name"],
            },
        )


if __name__ == "__main__":
    seed_inventory()
