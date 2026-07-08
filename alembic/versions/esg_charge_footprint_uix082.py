"""UIX-082 ESG charge footprint read-model.

Revision ID: esg_charge_footprint_uix082
Revises: user_screen_overlays_uix071
"""
from __future__ import annotations

from alembic import op

revision = "esg_charge_footprint_uix082"
down_revision = "user_screen_overlays_uix071"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_agrar.esg_charge_footprint (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
            charge_id VARCHAR(96) NOT NULL,
            factor_version VARCHAR(32) NOT NULL,
            co2e_kg NUMERIC(18, 3) NOT NULL DEFAULT 0,
            components JSONB NOT NULL DEFAULT '[]'::jsonb,
            inputs JSONB NOT NULL DEFAULT '[]'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_esg_charge_footprint UNIQUE (tenant_id, charge_id, factor_version)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_esg_charge_footprint_charge
        ON domain_agrar.esg_charge_footprint (tenant_id, charge_id)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_esg_charge_footprint_charge")
    op.execute("DROP TABLE IF EXISTS domain_agrar.esg_charge_footprint")
