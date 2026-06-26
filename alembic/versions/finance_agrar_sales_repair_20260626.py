"""BULK-REPAIR-001: Finance + Agrar + Sales Batch-Repair-Migration Wave 11.

Tabellen aus Parallel-Alembic-Branches idempotent in der Hauptkette anlegen:

  domain_erp   — dunning_rules, dunning_notices, payment_runs, payment_run_items,
                 payment_returns, exchange_rates
                 (aus ensure_finance_api_tables_20260413)

  domain_agrar — ernte_planung, agrar_maschinen
                 (aus agrar_ernte_planung_20260520, agrar_maschinen_wetter_20260301)

  domain_shared — branches (Niederlassungen)
  domain_sales  — delivery_notes (Verkaufs-Lieferscheine)
                 (aus sales_delivery_notes_branches_audit_20260216)

  domain_crm   — sales_order_items (Auftragspositionen)
                 + ADD COLUMN IF NOT EXISTS shipping_method auf sales_orders
                 (aus sales_orders_items_shipping_20260215)

Revision ID: finance_agrar_sales_repair_20260626
Revises: warehouse_schema_repair_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "finance_agrar_sales_repair_20260626"
down_revision = "warehouse_schema_repair_20260626"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── Schemata sicherstellen ───────────────────────────────────────────────
    for schema in ("domain_erp", "domain_agrar", "domain_shared", "domain_sales", "domain_crm", "domain_audit"):
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    # ════════════════════════════════════════════════════════════════════════
    # domain_erp — Finance-Tabellen
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.dunning_rules (
            id                      VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id               VARCHAR(64)     NOT NULL,
            level                   INTEGER         NOT NULL,
            days_overdue_min        INTEGER         NOT NULL DEFAULT 0,
            days_overdue_max        INTEGER,
            fee_amount              NUMERIC(15,2)   NOT NULL DEFAULT 0,
            fee_percentage          NUMERIC(7,4)    NOT NULL DEFAULT 0,
            interest_rate           NUMERIC(7,4)    NOT NULL DEFAULT 0,
            payment_deadline_days   INTEGER         NOT NULL DEFAULT 14,
            block_customer          BOOLEAN         NOT NULL DEFAULT FALSE,
            escalate_to_collection  BOOLEAN         NOT NULL DEFAULT FALSE,
            description_template    TEXT,
            active                  BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at              TIMESTAMPTZ     DEFAULT NOW(),
            updated_at              TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.dunning_notices (
            id                  VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(64)     NOT NULL,
            op_id               VARCHAR(64),
            debtor_id           VARCHAR(64),
            dunning_level       INTEGER         NOT NULL DEFAULT 1,
            dunning_date        DATE            NOT NULL,
            due_date            DATE,
            open_amount         NUMERIC(15,2)   NOT NULL DEFAULT 0,
            dunning_fee         NUMERIC(15,2)   NOT NULL DEFAULT 0,
            interest            NUMERIC(15,2)   NOT NULL DEFAULT 0,
            total_amount        NUMERIC(15,2)   NOT NULL DEFAULT 0,
            payment_deadline    DATE,
            status              VARCHAR(32)     NOT NULL DEFAULT 'created',
            sent_date           DATE,
            payment_date        DATE,
            notes               TEXT,
            created_at          TIMESTAMPTZ     DEFAULT NOW(),
            updated_at          TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.payment_runs (
            id                  VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(64)     NOT NULL,
            run_number          VARCHAR(50)     NOT NULL,
            execution_date      DATE            NOT NULL,
            initiator_name      VARCHAR(255)    NOT NULL,
            initiator_iban      VARCHAR(34)     NOT NULL,
            initiator_bic       VARCHAR(11),
            total_amount        NUMERIC(15,2)   NOT NULL DEFAULT 0,
            payment_count       INTEGER         NOT NULL DEFAULT 0,
            status              VARCHAR(32)     NOT NULL DEFAULT 'draft',
            approved_at         TIMESTAMPTZ,
            approved_by         VARCHAR(128),
            executed_at         TIMESTAMPTZ,
            sepa_file_id        VARCHAR(128),
            notes               TEXT,
            created_at          TIMESTAMPTZ     DEFAULT NOW(),
            updated_at          TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_runs_tenant_run_number
            ON domain_erp.payment_runs (tenant_id, run_number)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.payment_run_items (
            id                  VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(64)     NOT NULL,
            payment_run_id      VARCHAR(64)     NOT NULL,
            creditor_id         VARCHAR(64),
            creditor_name       VARCHAR(255),
            iban                VARCHAR(34),
            bic                 VARCHAR(11),
            amount              NUMERIC(15,2)   NOT NULL DEFAULT 0,
            purpose             TEXT,
            op_id               VARCHAR(64),
            invoice_number      VARCHAR(100),
            discount_used       BOOLEAN         NOT NULL DEFAULT FALSE,
            discount_amount     NUMERIC(15,2)   NOT NULL DEFAULT 0,
            end_to_end_id       VARCHAR(64),
            status              VARCHAR(32)     NOT NULL DEFAULT 'pending',
            created_at          TIMESTAMPTZ     DEFAULT NOW(),
            updated_at          TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.payment_returns (
            id                  VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(64)     NOT NULL,
            payment_run_id      VARCHAR(64)     NOT NULL,
            payment_item_id     VARCHAR(64)     NOT NULL,
            return_reason       VARCHAR(100),
            return_date         DATE,
            notes               TEXT,
            created_at          TIMESTAMPTZ     DEFAULT NOW()
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_erp.exchange_rates (
            id              VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            from_currency   VARCHAR(3)      NOT NULL,
            to_currency     VARCHAR(3)      NOT NULL,
            rate            NUMERIC(18,8)   NOT NULL,
            valid_from      DATE,
            valid_to        DATE,
            rate_date       DATE            NOT NULL DEFAULT CURRENT_DATE,
            rate_type       VARCHAR(32)     NOT NULL DEFAULT 'SPOT',
            source          VARCHAR(64),
            active          BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_exchange_rates_tenant_pair_date_type
            ON domain_erp.exchange_rates (tenant_id, from_currency, to_currency, rate_date, rate_type)
    """))

    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_dunning_rules_tenant
            ON domain_erp.dunning_rules (tenant_id, active, level)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_dunning_notices_tenant_debtor
            ON domain_erp.dunning_notices (tenant_id, debtor_id, dunning_date)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_payment_runs_tenant_status
            ON domain_erp.payment_runs (tenant_id, status, execution_date)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_payment_run_items_run
            ON domain_erp.payment_run_items (payment_run_id, status)
    """))

    # ════════════════════════════════════════════════════════════════════════
    # domain_agrar — Ernte-Planung + Maschinenpark
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_agrar.ernte_planung (
            id          VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id   VARCHAR(120)    NOT NULL,
            schlag      VARCHAR(255)    NOT NULL,
            kultur      VARCHAR(120)    NOT NULL,
            datum       DATE            NOT NULL,
            menge       FLOAT           NOT NULL DEFAULT 0,
            ertrag      FLOAT           NOT NULL DEFAULT 0,
            status      VARCHAR(30)     NOT NULL DEFAULT 'geplant',
            created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_ernte_planung_tenant
            ON domain_agrar.ernte_planung (tenant_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_ernte_planung_datum
            ON domain_agrar.ernte_planung (datum)
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_agrar.agrar_maschinen (
            id                          VARCHAR     NOT NULL PRIMARY KEY,
            tenant_id                   VARCHAR     NOT NULL,
            customer_id                 VARCHAR,
            name                        VARCHAR(200) NOT NULL,
            typ                         VARCHAR(50)  NOT NULL,
            hersteller                  VARCHAR(100),
            modell                      VARCHAR(100),
            baujahr                     INTEGER,
            kennzeichen                 VARCHAR(20),
            fahrgestellnummer           VARCHAR(50),
            leistung_kw                 FLOAT,
            betriebsstunden             FLOAT       NOT NULL DEFAULT 0,
            naechste_wartung_stunden    FLOAT,
            naechste_wartung_datum      TIMESTAMPTZ,
            status                      VARCHAR(20) NOT NULL DEFAULT 'verfuegbar',
            standort                    VARCHAR(100),
            notiz                       TEXT,
            ist_aktiv                   BOOLEAN     NOT NULL DEFAULT TRUE,
            created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at                  TIMESTAMPTZ
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_agrar_maschinen_tenant_id
            ON domain_agrar.agrar_maschinen (tenant_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_agrar_maschinen_customer_id
            ON domain_agrar.agrar_maschinen (customer_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_agrar_maschinen_status
            ON domain_agrar.agrar_maschinen (status)
    """))

    # ════════════════════════════════════════════════════════════════════════
    # domain_shared — Niederlassungen (Branches)
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_shared.branches (
            id              VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id       VARCHAR         NOT NULL,
            branch_number   INTEGER         NOT NULL,
            name            VARCHAR(255)    NOT NULL,
            address         JSONB,
            is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_branches_tenant_branch_number UNIQUE (tenant_id, branch_number)
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_branches_tenant_id
            ON domain_shared.branches (tenant_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_branches_branch_number
            ON domain_shared.branches (branch_number)
    """))

    # ════════════════════════════════════════════════════════════════════════
    # domain_sales — Lieferscheine (Delivery Notes)
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_sales.delivery_notes (
            id                          VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id                   VARCHAR         NOT NULL,
            delivery_note_number        VARCHAR(50)     NOT NULL,
            customer_id                 VARCHAR,
            branch_id                   VARCHAR,
            sales_rep_id                VARCHAR,
            operator_id                 VARCHAR,
            delivery_date               DATE            NOT NULL,
            delivery_time               TIME,
            cost_center_id              VARCHAR,
            truck_number                INTEGER,
            is_credit_note              BOOLEAN         NOT NULL DEFAULT FALSE,
            is_self_pickup              BOOLEAN         NOT NULL DEFAULT FALSE,
            is_early_payment            BOOLEAN         NOT NULL DEFAULT FALSE,
            reference_invoice_number    VARCHAR(50),
            status                      VARCHAR(20)     NOT NULL DEFAULT 'draft',
            is_printed                  BOOLEAN         NOT NULL DEFAULT FALSE,
            is_delivered                BOOLEAN         NOT NULL DEFAULT FALSE,
            invoice_number              VARCHAR(50),
            total_net                   NUMERIC(14,2),
            total_vat                   NUMERIC(14,2),
            total_gross                 NUMERIC(14,2),
            notes                       TEXT,
            created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_delivery_notes_tenant_number UNIQUE (tenant_id, delivery_note_number)
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_delivery_notes_tenant_date
            ON domain_sales.delivery_notes (tenant_id, delivery_date)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_delivery_notes_customer
            ON domain_sales.delivery_notes (customer_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_delivery_notes_status
            ON domain_sales.delivery_notes (tenant_id, status)
    """))

    # ════════════════════════════════════════════════════════════════════════
    # domain_crm — Auftragspositionen + shipping_method
    # ════════════════════════════════════════════════════════════════════════

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_crm.sales_order_items (
            id                  VARCHAR         NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR         NOT NULL,
            order_id            VARCHAR         NOT NULL,
            line_number         INTEGER         NOT NULL,
            article_number      VARCHAR(80)     NOT NULL,
            description         VARCHAR(255),
            quantity            NUMERIC(12,3)   NOT NULL,
            unit_price          NUMERIC(12,4)   NOT NULL,
            discount_percent    NUMERIC(7,2)    NOT NULL DEFAULT 0,
            line_total          NUMERIC(14,2)   NOT NULL,
            created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_sales_order_items_order_id
            ON domain_crm.sales_order_items (order_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_sales_order_items_article_number
            ON domain_crm.sales_order_items (article_number)
    """))

    # shipping_method-Spalte auf sales_orders nachrüsten (falls Tabelle existiert)
    conn.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'domain_crm' AND table_name = 'sales_orders'
            ) THEN
                ALTER TABLE domain_crm.sales_orders
                    ADD COLUMN IF NOT EXISTS shipping_method VARCHAR(40);
            END IF;
        END
        $$
    """))


def downgrade() -> None:
    # Repair-Migrations werden nicht rueckgaengig gemacht (IF NOT EXISTS Pattern)
    pass
