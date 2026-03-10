"""add lkw_annahme_queue table (Gap 002)

Revision ID: lkw_queue_20260306
Revises: ensure_controlling_tables_20260304
Create Date: 2026-03-06

Adds domain_inventory.lkw_annahme_queue for persistent LKW-Annahme-Warteschlange.
Replaces Redis cache; data survives restarts.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = "lkw_queue_20260306"
down_revision = "ensure_controlling_tables_20260304"
branch_labels = None
depends_on = None


def _table_exists(conn, schema: str, table: str) -> bool:
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = :schema AND table_name = :table"
        ),
        {"schema": schema, "table": table},
    )
    return r.scalar() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "domain_inventory", "lkw_annahme_queue"):
        return

    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_inventory"))

    op.execute(
        sa.text(
            """
            CREATE TABLE domain_inventory.lkw_annahme_queue (
                id VARCHAR PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                kennzeichen VARCHAR(20) NOT NULL,
                lieferant VARCHAR(200) NOT NULL,
                lieferschein_nr VARCHAR(100) DEFAULT '',
                artikel VARCHAR(200) DEFAULT '',
                ankunftszeit TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                prioritaet VARCHAR(20) NOT NULL DEFAULT 'normal',
                status VARCHAR(30) NOT NULL DEFAULT 'wartend',
                attachment_ids JSONB DEFAULT '[]'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ,
                CONSTRAINT fk_lkw_queue_tenant FOREIGN KEY (tenant_id)
                    REFERENCES domain_shared.tenants(id) ON DELETE CASCADE
            )
            """
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX ix_lkw_annahme_queue_tenant_status ON domain_inventory.lkw_annahme_queue (tenant_id, status)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX ix_lkw_annahme_queue_ankunftszeit ON domain_inventory.lkw_annahme_queue (ankunftszeit)"
        )
    )


def downgrade() -> None:
    op.drop_table("lkw_annahme_queue", schema="domain_inventory")
