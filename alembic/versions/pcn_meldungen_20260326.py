"""PCN-Meldungen Persistenz-Tabelle (Wave 104 Gap-D)

Revision ID: pcn_meldungen_20260326
Revises: flow_spine_instances_20260326
Create Date: 2026-03-26

Ersetzt den _PCN_STORE In-Memory-Dict durch eine persistente Tabelle.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "pcn_meldungen_20260326"
down_revision = "flow_spine_instances_20260326"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_ops"))

    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_ops.ops_pcn_meldungen (
            id                   VARCHAR(36)  PRIMARY KEY,
            produktname          VARCHAR(255) NOT NULL DEFAULT '',
            ufi                  VARCHAR(24),
            cas_nummern          VARCHAR(500),
            gefahrenklassen      JSONB        NOT NULL DEFAULT '[]',
            verwendungskategorie VARCHAR(120),
            pcn_status           VARCHAR(30)  NOT NULL DEFAULT 'entwurf',
            tenant_id            VARCHAR(120) NOT NULL DEFAULT 'default',
            created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_ops_pcn_meldungen_tenant_id "
        "ON domain_ops.ops_pcn_meldungen (tenant_id)"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS domain_ops.ops_pcn_meldungen"))
