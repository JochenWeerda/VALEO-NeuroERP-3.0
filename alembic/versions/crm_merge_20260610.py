"""crm_merge — Kunden-Zusammenführung (DOM-CRM-004.2)

merged_into-Zeiger auf public.kunden (Verlierer → Master) + append-only Audit-Log
der Zusammenführungen.

Revision ID: crm_merge_20260610
Revises: supply_chain_events_20260610
Create Date: 2026-06-10
"""

from __future__ import annotations

from alembic import op

revision = "crm_merge_20260610"
down_revision = "supply_chain_events_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.kunden ADD COLUMN IF NOT EXISTS merged_into VARCHAR(32)")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.crm_merge_log (
            id            UUID PRIMARY KEY,
            tenant_id     TEXT,
            master_nr     VARCHAR(32) NOT NULL,
            duplicate_nr  VARCHAR(32) NOT NULL,
            moved         JSONB,
            bediener      VARCHAR(64),
            created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_merge_log_master "
        "ON public.crm_merge_log (master_nr, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.ix_crm_merge_log_master")
    op.execute("DROP TABLE IF EXISTS public.crm_merge_log")
    op.execute("ALTER TABLE public.kunden DROP COLUMN IF EXISTS merged_into")
