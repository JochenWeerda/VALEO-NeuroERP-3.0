"""crm_gifts — Kunden-Präsente (KIM-S3)

Kundenbezogene Präsente/Geschenke-PR (L3 „Kunden-Präsente"). Optional einem
Ansprechpartner zugeordnet, Filter nach Jahr.

Revision ID: crm_gifts_kim_s3_20260609
Revises: crm_notifications_kim_l3_backend_20260609
Create Date: 2026-06-09
"""

from __future__ import annotations

from alembic import op

revision = "crm_gifts_kim_s3_20260609"
down_revision = "crm_notifications_kim_l3_backend_20260609"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.crm_gifts (
            id                      UUID PRIMARY KEY,
            tenant_id               UUID NOT NULL,
            kunden_nr               VARCHAR(32) NOT NULL,
            contact_id              UUID,
            year                    INTEGER NOT NULL,
            gift_date               DATE,
            occasion                VARCHAR(256),
            gift_name               VARCHAR(256),
            quantity                NUMERIC(12,2) DEFAULT 1,
            sales_rep               VARCHAR(64),
            operator                VARCHAR(64),
            representative_officer  VARCHAR(64),
            sequence_number         INTEGER,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_gifts_kunde "
        "ON public.crm_gifts (tenant_id, kunden_nr, year)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.ix_crm_gifts_kunde")
    op.execute("DROP TABLE IF EXISTS public.crm_gifts")
