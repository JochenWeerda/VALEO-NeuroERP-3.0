"""DOM-LOG-004.2/.3: tour_disposition_checks + epod_settlements

Revision ID: log_disposition_20260623
Revises: log_carrier_invoices_20260618
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "log_disposition_20260623"
down_revision = "log_carrier_invoices_20260618"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_logistics")

    op.create_table(
        "tour_disposition_checks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tour_id", sa.String(36), nullable=False),
        sa.Column(
            "checked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("total_weight_kg", sa.Numeric(14, 2)),
        sa.Column("capacity_kg", sa.Numeric(14, 2)),
        sa.Column("utilization_pct", sa.Numeric(8, 2)),
        sa.Column("stops_count", sa.Integer),
        sa.Column("result", sa.String(20)),
        sa.Column("tenant_id", sa.String(36)),
        schema="domain_logistics",
    )
    op.create_index(
        "ix_tour_disposition_checks_tour_id",
        "tour_disposition_checks",
        ["tour_id"],
        schema="domain_logistics",
    )

    op.create_table(
        "epod_settlements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tour_id", sa.String(36), nullable=False),
        sa.Column("stop_id", sa.String(36), nullable=False, unique=True),
        sa.Column(
            "settled_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("recipient_name", sa.String(255)),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("tenant_id", sa.String(36)),
        schema="domain_logistics",
    )
    op.create_index(
        "ix_epod_settlements_tour_id",
        "epod_settlements",
        ["tour_id"],
        schema="domain_logistics",
    )

    # add epod_status column to existing tour_stops if not present
    op.execute("""
        ALTER TABLE domain_logistics.tour_stops
        ADD COLUMN IF NOT EXISTS epod_status VARCHAR(20) DEFAULT 'PENDING'
    """)
    op.execute("""
        ALTER TABLE domain_logistics.tour_stops
        ADD COLUMN IF NOT EXISTS epod_photo_ref VARCHAR(500)
    """)
    op.execute("""
        ALTER TABLE domain_logistics.tour_stops
        ADD COLUMN IF NOT EXISTS recipient_name VARCHAR(255)
    """)


def downgrade() -> None:
    op.drop_table("epod_settlements", schema="domain_logistics")
    op.drop_table("tour_disposition_checks", schema="domain_logistics")
    # note: epod_status/epod_photo_ref/recipient_name columns not dropped (non-destructive)
