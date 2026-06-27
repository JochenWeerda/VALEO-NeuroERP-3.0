"""WAREHOUSE-REPAIR-001: domain_inventory.warehouses fehlende Spalten nachziehen.

001_initial_schema.py (Parallel-Branch) hat warehouses mit einem abgespeckten
Schema angelegt (kein city, postal_code, country, contact_person, phone, email,
warehouse_type, total_capacity, used_capacity, deleted_at). Diese Repair-Migration
legt die Tabelle idempotent an (frische Installs) und fuegt fehlende Spalten
per ADD COLUMN IF NOT EXISTS nach (bestehende Dev-DBs mit 001-Schema).

Revision ID: warehouse_schema_repair_20260626
Revises: einkauf_ls_opportunities_repair_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "warehouse_schema_repair_20260626"
down_revision = "einkauf_ls_opportunities_repair_20260626"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_inventory"))

    # Tabelle fuer frische Installs anlegen
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_inventory.warehouses (
            id              VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR,
            warehouse_code  VARCHAR(20)     NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            address         TEXT,
            city            VARCHAR(50),
            postal_code     VARCHAR(10),
            country         VARCHAR(2)      NOT NULL DEFAULT 'DE',
            contact_person  VARCHAR(100),
            phone           VARCHAR(20),
            email           VARCHAR(100),
            warehouse_type  VARCHAR(20)     NOT NULL DEFAULT 'standard',
            total_capacity  NUMERIC(12,2),
            used_capacity   NUMERIC(12,2)   NOT NULL DEFAULT 0,
            is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
            deleted_at      TIMESTAMPTZ,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
        )
    """))

    # Fehlende Spalten fuer bestehende Dev-DBs (001-Schema) nachziehen
    for ddl in [
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS city VARCHAR(50)",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10)",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS country VARCHAR(2) DEFAULT 'DE'",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS contact_person VARCHAR(100)",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS phone VARCHAR(20)",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS email VARCHAR(100)",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS warehouse_type VARCHAR(20) DEFAULT 'standard'",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS total_capacity NUMERIC(12,2)",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS used_capacity NUMERIC(12,2) DEFAULT 0",
        "ALTER TABLE domain_inventory.warehouses ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ",
    ]:
        conn.execute(text(ddl))

    # Index fuer Tenant-Abfragen
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_warehouses_tenant_active
            ON domain_inventory.warehouses (tenant_id, is_active)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_warehouses_tenant_code
            ON domain_inventory.warehouses (tenant_id, warehouse_code)
    """))

    # domain_inventory.inventory_counts (ORM: InventoryCount)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_inventory.inventory_counts (
            id              VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR         NOT NULL,
            warehouse_id    VARCHAR         NOT NULL,
            count_date      DATE            NOT NULL,
            status          VARCHAR(20)     NOT NULL DEFAULT 'open',
            counted_by      VARCHAR(100),
            approved_by     VARCHAR(100),
            notes           TEXT,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            CONSTRAINT chk_inventory_counts_status
                CHECK (status IN ('open','in_progress','completed','approved','cancelled'))
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_inventory_counts_tenant_warehouse
            ON domain_inventory.inventory_counts (tenant_id, warehouse_id, count_date)
    """))

    # domain_inventory.inventory_stock_movements (falls noch nicht vorhanden)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_inventory.inventory_stock_movements (
            id              VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR         NOT NULL,
            article_id      VARCHAR         NOT NULL,
            warehouse_id    VARCHAR         NOT NULL,
            movement_type   VARCHAR(30)     NOT NULL,
            quantity        NUMERIC(14,3)   NOT NULL,
            unit            VARCHAR(20),
            reference_type  VARCHAR(60),
            reference_id    VARCHAR(64),
            charge          VARCHAR(80),
            bin_id          VARCHAR(64),
            booked_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            booked_by       VARCHAR(100),
            notes           TEXT,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
        )
    """))
    for ddl in [
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS tenant_id VARCHAR",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS article_id VARCHAR",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS warehouse_id VARCHAR",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS movement_type VARCHAR(30)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS quantity NUMERIC(14,3)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS unit VARCHAR(20)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS reference_type VARCHAR(60)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS reference_id VARCHAR(64)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS charge VARCHAR(80)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS bin_id VARCHAR(64)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS booked_at TIMESTAMPTZ DEFAULT NOW()",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS booked_by VARCHAR(100)",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS notes TEXT",
        "ALTER TABLE domain_inventory.inventory_stock_movements ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()",
    ]:
        conn.execute(text(ddl))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_inv_stock_movements_tenant_article
            ON domain_inventory.inventory_stock_movements (tenant_id, article_id, booked_at)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_inv_stock_movements_tenant_warehouse
            ON domain_inventory.inventory_stock_movements (tenant_id, warehouse_id, booked_at)
    """))


def downgrade() -> None:
    # Repair-Migrations werden nicht rueckgaengig gemacht (IF NOT EXISTS Pattern)
    pass
