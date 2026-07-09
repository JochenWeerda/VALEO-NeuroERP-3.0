"""
Inventory seed data for local development.

The bootstrap path calls this module via ``python -m app.seeds.inventory_seed``.
Keep the seed deterministic and idempotent: local booking and weighing tests need
stable article numbers, prices, stock and tenant ownership.
"""

from __future__ import annotations

import json
from decimal import Decimal

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

TENANT_ID = settings.DEFAULT_TENANT_ID
TENANT_DOMAIN = "default.local"
TENANT_NAME = "Default Dev Tenant"

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
        "id": "seed-art-get-wei-b",
        "article_number": "GET-WEI-B",
        "name": "Weizen B-Qualitaet",
        "description": "Buchungstest: lagerfaehiger Getreideartikel",
        "category": "Getreide",
        "subcategory": "Weizen",
        "warengruppe": "Getreide",
        "unit": "kg",
        "purchase_price": Decimal("0.19"),
        "sales_price": Decimal("0.24"),
        "current_stock": Decimal("25000.00"),
        "min_stock": Decimal("5000.00"),
        "max_stock": Decimal("100000.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": True,
        "lager_silo": True,
    },
    {
        "id": "seed-art-get-ger-f",
        "article_number": "GET-GER-F",
        "name": "Futtergerste",
        "description": "Buchungstest: Gerste fuer Einkauf, Lager und Verkauf",
        "category": "Getreide",
        "subcategory": "Gerste",
        "warengruppe": "Getreide",
        "unit": "kg",
        "purchase_price": Decimal("0.16"),
        "sales_price": Decimal("0.21"),
        "current_stock": Decimal("18000.00"),
        "min_stock": Decimal("4000.00"),
        "max_stock": Decimal("80000.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": True,
        "lager_silo": True,
    },
    {
        "id": "seed-art-oel-raps",
        "article_number": "OEL-RAPS",
        "name": "Raps Rohware",
        "description": "Buchungstest: Oelsaat mit Chargenpflicht",
        "category": "Oelsaaten",
        "subcategory": "Raps",
        "warengruppe": "Oelsaaten",
        "unit": "kg",
        "purchase_price": Decimal("0.39"),
        "sales_price": Decimal("0.48"),
        "current_stock": Decimal("12000.00"),
        "min_stock": Decimal("3000.00"),
        "max_stock": Decimal("60000.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": True,
        "lager_silo": True,
    },
    {
        "id": "seed-art-saa-ww-z",
        "article_number": "SAA-WW-Z",
        "name": "Winterweizen Z-Saatgut",
        "description": "Buchungstest: Saatgut Sackware",
        "category": "Saatgut",
        "subcategory": "Getreide",
        "warengruppe": "Saatgut",
        "unit": "kg",
        "purchase_price": Decimal("0.62"),
        "sales_price": Decimal("0.79"),
        "current_stock": Decimal("6500.00"),
        "min_stock": Decimal("1000.00"),
        "max_stock": Decimal("25000.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": False,
        "lager_silo": False,
    },
    {
        "id": "seed-art-seed-00123",
        "article_number": "SEED-00123",
        "name": "Saatgut Mais FAO 220",
        "description": "Buchungstest: Saatgut-Schnellstart fuer Erfassungsmasken",
        "category": "Saatgut",
        "subcategory": "Mais",
        "warengruppe": "Saatgut",
        "unit": "kg",
        "purchase_price": Decimal("1.85"),
        "sales_price": Decimal("2.35"),
        "current_stock": Decimal("2400.00"),
        "min_stock": Decimal("300.00"),
        "max_stock": Decimal("12000.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": False,
        "lager_silo": False,
    },
    {
        "id": "seed-art-fert-2007",
        "article_number": "FERT-2007",
        "name": "NPK Duenger 15-15-15",
        "description": "Buchungstest: Duenger-Schnellstart fuer Belegerfassung",
        "category": "Duengemittel",
        "subcategory": "NPK",
        "warengruppe": "Duengemittel",
        "unit": "kg",
        "purchase_price": Decimal("0.44"),
        "sales_price": Decimal("0.57"),
        "current_stock": Decimal("18500.00"),
        "min_stock": Decimal("2500.00"),
        "max_stock": Decimal("75000.00"),
        "chargenpflicht": False,
        "qs_pruefung_erforderlich": False,
        "lager_silo": False,
    },
    {
        "id": "seed-art-due-kas-27",
        "article_number": "DUE-KAS-27",
        "name": "KAS 27 Prozent N",
        "description": "Buchungstest: Duengemittel mit Preis und Bestand",
        "category": "Duengemittel",
        "subcategory": "Stickstoff",
        "warengruppe": "Duengemittel",
        "unit": "kg",
        "purchase_price": Decimal("0.31"),
        "sales_price": Decimal("0.39"),
        "current_stock": Decimal("42000.00"),
        "min_stock": Decimal("8000.00"),
        "max_stock": Decimal("120000.00"),
        "chargenpflicht": False,
        "qs_pruefung_erforderlich": False,
        "lager_silo": False,
    },
    {
        "id": "seed-art-psm-herb-get",
        "article_number": "PSM-HERB-GET",
        "name": "Herbizid Getreide",
        "description": "Buchungstest: Pflanzenschutzmittel",
        "category": "Pflanzenschutz",
        "subcategory": "Herbizid",
        "warengruppe": "Pflanzenschutz",
        "unit": "l",
        "purchase_price": Decimal("42.50"),
        "sales_price": Decimal("56.90"),
        "current_stock": Decimal("320.00"),
        "min_stock": Decimal("50.00"),
        "max_stock": Decimal("1500.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": False,
        "lager_silo": False,
    },
    {
        "id": "seed-art-fut-milch-18",
        "article_number": "FUT-MILCH-18",
        "name": "Milchleistungsfutter 18/3",
        "description": "Buchungstest: Futtermittel lose",
        "category": "Futtermittel",
        "subcategory": "Rind",
        "warengruppe": "Futtermittel",
        "unit": "kg",
        "purchase_price": Decimal("0.29"),
        "sales_price": Decimal("0.36"),
        "current_stock": Decimal("15000.00"),
        "min_stock": Decimal("2500.00"),
        "max_stock": Decimal("70000.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": True,
        "lager_silo": False,
    },
    {
        "id": "seed-art-mmx-standard",
        "article_number": "MMX-STANDARD",
        "name": "Mehlmischung Standard",
        "description": "Buchungstest: Mischware fuer Produktion/Verkauf",
        "category": "Futtermittel",
        "subcategory": "Mischfutter",
        "warengruppe": "MMX Mehlmischung",
        "unit": "kg",
        "purchase_price": Decimal("0.24"),
        "sales_price": Decimal("0.33"),
        "current_stock": Decimal("9000.00"),
        "min_stock": Decimal("2000.00"),
        "max_stock": Decimal("50000.00"),
        "chargenpflicht": True,
        "qs_pruefung_erforderlich": True,
        "lager_silo": False,
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
            SELECT id FROM domain_shared.tenants WHERE id = :id
            """
        ),
        {"id": TENANT_ID},
    ).scalar()

    if result:
        return str(result)

    conn.execute(
        text(
            """
            INSERT INTO domain_shared.tenants (id, name, domain, is_active, settings)
            VALUES (:id, :name, :domain, true, :settings)
            """
        ),
        {
            "id": TENANT_ID,
            "name": TENANT_NAME,
            "domain": TENANT_DOMAIN,
            "settings": json.dumps({"locale": "de-DE"}),
        },
    )
    return TENANT_ID


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

        params = {
            "id": f"seed-warehouse-{wh['warehouse_code'].lower()}",
            "tenant_id": tenant_id,
            "code": wh["warehouse_code"],
            "name": wh["name"],
            "address": wh["address"]["street"],
            "city": wh["address"]["city"],
            "postal_code": wh["address"]["postal_code"],
            "country": wh["address"]["country"],
        }

        if exists:
            conn.execute(
                text(
                    """
                    UPDATE domain_inventory.warehouses
                    SET tenant_id = :tenant_id,
                        name = :name,
                        address = :address,
                        city = :city,
                        postal_code = :postal_code,
                        country = :country,
                        is_active = true
                    WHERE warehouse_code = :code
                    """
                ),
                params,
            )
            continue

        conn.execute(
            text(
                """
                INSERT INTO domain_inventory.warehouses
                (id, tenant_id, warehouse_code, name, address, city, postal_code, country, is_active)
                VALUES (:id, :tenant_id, :code, :name, :address, :city, :postal_code, :country, true)
                """
            ),
            params,
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

        params = _article_params(article, tenant_id)

        if exists:
            conn.execute(
                text(
                    """
                    UPDATE domain_inventory.articles
                    SET tenant_id = :tenant_id,
                        name = :name,
                        description = :description,
                        category = :category,
                        subcategory = :subcategory,
                        warengruppe = :warengruppe,
                        unit = :unit,
                        purchase_price = :purchase_price,
                        sales_price = :sales_price,
                        current_stock = :current_stock,
                        reserved_stock = 0,
                        available_stock = :current_stock,
                        min_stock = :min_stock,
                        max_stock = :max_stock,
                        currency = 'EUR',
                        mhd_erforderlich = false,
                        lagerartikel = true,
                        chargenpflicht = :chargenpflicht,
                        qs_pruefung_erforderlich = :qs_pruefung_erforderlich,
                        bio_kennzeichnung = false,
                        gmp_plus_relevanz = false,
                        mehrwertsteuer_prozent = 19.00,
                        lagerorte = :lagerorte,
                        lager_silo = :lager_silo,
                        is_active = true,
                        deleted_at = NULL
                    WHERE article_number = :article_number
                    """
                ),
                params,
            )
            continue

        conn.execute(
            text(
                """
                INSERT INTO domain_inventory.articles
                (id, tenant_id, article_number, name, description, category,
                 subcategory, warengruppe, unit, purchase_price, sales_price,
                 current_stock, reserved_stock, available_stock, min_stock,
                 max_stock, currency, mhd_erforderlich, lagerartikel,
                 chargenpflicht, qs_pruefung_erforderlich, bio_kennzeichnung,
                 gmp_plus_relevanz, mehrwertsteuer_prozent, lagerorte,
                 lager_silo, is_active)
                VALUES
                (:id, :tenant_id, :article_number, :name, :description,
                 :category, :subcategory, :warengruppe, :unit, :purchase_price,
                 :sales_price, :current_stock, 0, :current_stock, :min_stock,
                 :max_stock, 'EUR', false, true, :chargenpflicht,
                 :qs_pruefung_erforderlich, false, false, 19.00, :lagerorte,
                 :lager_silo, true)
                """
            ),
            params,
        )


def _article_params(article: dict[str, object], tenant_id: str) -> dict[str, object]:
    current_stock = article["current_stock"]
    return {
        "id": article["id"],
        "tenant_id": tenant_id,
        "article_number": article["article_number"],
        "name": article["name"],
        "description": article["description"],
        "category": article["category"],
        "subcategory": article["subcategory"],
        "warengruppe": article["warengruppe"],
        "unit": article["unit"],
        "purchase_price": str(article["purchase_price"]),
        "sales_price": str(article["sales_price"]),
        "current_stock": str(current_stock),
        "min_stock": str(article["min_stock"]),
        "max_stock": str(article["max_stock"]),
        "chargenpflicht": bool(article["chargenpflicht"]),
        "qs_pruefung_erforderlich": bool(article["qs_pruefung_erforderlich"]),
        "lagerorte": json.dumps(["MAIN"]),
        "lager_silo": bool(article["lager_silo"]),
    }


if __name__ == "__main__":
    seed_inventory()
