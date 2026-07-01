"""pricing: staffelrabatte Tabelle anlegen

Revision ID: pricing_staffelrabatte_20260701
Revises:
Create Date: 2026-07-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "pricing_staffelrabatte_20260701"
down_revision = None
branch_labels = ("pricing_staffelrabatte",)
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_pricing.staffelrabatte (
            id              VARCHAR(36)     PRIMARY KEY,
            tenant_id       VARCHAR(64)     NOT NULL,
            artikel_id      VARCHAR(36),
            artikelgruppe   VARCHAR(100),
            kunden_id       VARCHAR(36),
            kundengruppe    VARCHAR(100),
            gueltig_von     DATE,
            gueltig_bis     DATE,
            stufen          JSONB           NOT NULL DEFAULT '[]',
            bezeichnung     VARCHAR(255),
            status          VARCHAR(20)     NOT NULL DEFAULT 'aktiv',
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_staffelrabatte_tenant_artikel
            ON domain_pricing.staffelrabatte (tenant_id, artikel_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_staffelrabatte_tenant_kunden
            ON domain_pricing.staffelrabatte (tenant_id, kunden_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_pricing.staffelrabatte")
