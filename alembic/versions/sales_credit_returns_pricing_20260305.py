"""Sales: credit notes, returns, price list items

Revision ID: sales_cn_ret_pl_20260305
Revises: crm_consent_segments_20260305
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa

revision = "sales_cn_ret_pl_20260305"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_sales"))
    conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_pricing"))

    # ---- Price Lists (if not exists) ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_pricing.price_lists (
            id          VARCHAR(36) PRIMARY KEY,
            tenant_id   VARCHAR(64) NOT NULL DEFAULT 'default',
            name        VARCHAR(200) NOT NULL,
            description TEXT,
            currency    VARCHAR(3) NOT NULL DEFAULT 'EUR',
            price_list_type VARCHAR(50) DEFAULT 'standard',
            valid_from  DATE,
            valid_until DATE,
            is_active   BOOLEAN NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMPTZ DEFAULT NOW(),
            updated_at  TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    # ---- Price List Items (Staffelpreise) ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_pricing.price_list_items (
            id          VARCHAR(36) PRIMARY KEY,
            price_list_id VARCHAR(36) NOT NULL,
            article_id  VARCHAR(36) NOT NULL,
            article_number VARCHAR(80),
            unit_price  NUMERIC(18,4) NOT NULL DEFAULT 0,
            min_quantity NUMERIC(18,4) NOT NULL DEFAULT 0,
            max_quantity NUMERIC(18,4),
            discount_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
            valid_from  DATE,
            valid_until DATE,
            CONSTRAINT fk_pli_price_list FOREIGN KEY (price_list_id)
                REFERENCES domain_pricing.price_lists(id) ON DELETE CASCADE
        )
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_pli_price_list ON domain_pricing.price_list_items(price_list_id)
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_pli_article ON domain_pricing.price_list_items(article_id)
    """))

    # ---- Sales Credit Notes ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_sales.sales_credit_notes (
            id          VARCHAR(36) PRIMARY KEY,
            tenant_id   VARCHAR(64) NOT NULL,
            credit_note_number VARCHAR(64) NOT NULL,
            customer_id VARCHAR(64) NOT NULL,
            customer_name VARCHAR(200),
            invoice_reference VARCHAR(64),
            reason      VARCHAR(500) NOT NULL,
            total_amount NUMERIC(18,4) NOT NULL DEFAULT 0,
            currency    VARCHAR(3) NOT NULL DEFAULT 'EUR',
            status      VARCHAR(20) NOT NULL DEFAULT 'draft',
            notes       TEXT,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_scn_tenant ON domain_sales.sales_credit_notes(tenant_id)
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_scn_customer ON domain_sales.sales_credit_notes(customer_id)
    """))

    # ---- Sales Credit Note Lines ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_sales.sales_credit_note_lines (
            id          VARCHAR(36) PRIMARY KEY,
            credit_note_id VARCHAR(36) NOT NULL,
            line_number INT NOT NULL DEFAULT 1,
            article_number VARCHAR(80),
            description VARCHAR(500),
            quantity    NUMERIC(18,4) NOT NULL DEFAULT 0,
            unit_price  NUMERIC(18,4) NOT NULL DEFAULT 0,
            tax_rate    NUMERIC(5,2) NOT NULL DEFAULT 19,
            line_total  NUMERIC(18,4) NOT NULL DEFAULT 0,
            CONSTRAINT fk_scnl_cn FOREIGN KEY (credit_note_id)
                REFERENCES domain_sales.sales_credit_notes(id) ON DELETE CASCADE
        )
    """))

    # ---- Sales Returns / Retouren ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_sales.sales_returns (
            id          VARCHAR(36) PRIMARY KEY,
            tenant_id   VARCHAR(64) NOT NULL,
            return_number VARCHAR(64) NOT NULL,
            customer_id VARCHAR(64) NOT NULL,
            customer_name VARCHAR(200),
            delivery_note_reference VARCHAR(64),
            invoice_reference VARCHAR(64),
            reason      VARCHAR(500) NOT NULL,
            return_type VARCHAR(20) NOT NULL DEFAULT 'full',
            status      VARCHAR(20) NOT NULL DEFAULT 'open',
            notes       TEXT,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_sret_tenant ON domain_sales.sales_returns(tenant_id)
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_sret_customer ON domain_sales.sales_returns(customer_id)
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS domain_sales.sales_credit_note_lines"))
    conn.execute(sa.text("DROP TABLE IF EXISTS domain_sales.sales_credit_notes"))
    conn.execute(sa.text("DROP TABLE IF EXISTS domain_sales.sales_returns"))
    conn.execute(sa.text("DROP TABLE IF EXISTS domain_pricing.price_list_items"))
