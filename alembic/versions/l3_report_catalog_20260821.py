"""Governed L3 report catalog fact projection.

Revision ID: l3_report_catalog_20260821
Revises: tank_adapter_20260821
"""

from alembic import op

revision = "l3_report_catalog_20260821"
down_revision = "tank_adapter_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_reporting;
      CREATE TABLE IF NOT EXISTS domain_reporting.l3_report_facts (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, source_type TEXT NOT NULL,
        source_ref TEXT NOT NULL, source_number TEXT, source_route TEXT NOT NULL,
        occurred_on DATE NOT NULL, fact_type TEXT NOT NULL,
        representative_id TEXT, representative_name TEXT,
        customer_id TEXT, customer_name TEXT,
        article_id TEXT, article_name TEXT, article_group_id TEXT, article_group_name TEXT,
        batch_id TEXT, batch_name TEXT, harvest_id TEXT, harvest_name TEXT,
        route_id TEXT, route_name TEXT, quantity NUMERIC(18,3) NOT NULL DEFAULT 0,
        net_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
        gross_amount NUMERIC(18,2) NOT NULL DEFAULT 0, currency TEXT NOT NULL DEFAULT 'EUR',
        payload_hash TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,source_type,source_ref,fact_type)
      );
      CREATE INDEX IF NOT EXISTS ix_l3_report_facts_period
        ON domain_reporting.l3_report_facts (tenant_id,occurred_on,fact_type);
      CREATE INDEX IF NOT EXISTS ix_l3_report_facts_dimensions
        ON domain_reporting.l3_report_facts (tenant_id,representative_id,customer_id,article_id,article_group_id,batch_id,harvest_id,route_id);
      CREATE TABLE IF NOT EXISTS domain_reporting.l3_report_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, report_id TEXT NOT NULL,
        action TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL,
        parameter_hash TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_reporting.l3_report_audit;
      DROP TABLE IF EXISTS domain_reporting.l3_report_facts;
    """)
